# -*- coding: utf-8 -*-
import base64
import io
import logging
import re

import requests
from PIL import Image as PILImage

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30


class GecoWhatsappService(models.AbstractModel):
    _name = 'geco.whatsapp.service'
    _description = 'GECO WhatsApp Microservice Client'

    @api.model
    def _resolve_account(self, account=None, company=None):
        # sudo(): enviar por WhatsApp no debe requerir que el usuario tenga acceso
        # directo a las credenciales/tokens guardados en la cuenta.
        account = (account or self.env['geco.whatsapp.account']._get_default(company=company)).sudo()
        if not account:
            raise UserError(_(
                "No hay ninguna cuenta de WhatsApp configurada para esta compañía. "
                "Ve a WhatsApp > Cuentas y crea una."
            ))
        return account

    @api.model
    def _headers(self, account):
        return {'X-Internal-Token': account.internal_token} if account.internal_token else {}

    @api.model
    def normalize_phone(self, phone, account=None, default_country_code=None):
        digits = re.sub(r'\D', '', phone or '')
        if not digits:
            raise UserError(_("El contacto no tiene un número de teléfono válido para enviar WhatsApp."))
        cc = default_country_code or (account.default_country_code if account else None) or '52'
        if len(digits) <= 10 and not digits.startswith(cc):
            digits = f"{cc}{digits}"
        return digits

    @api.model
    def find_partner_by_phone(self, phone, company=None):
        """Búsqueda tolerante a formato: compara por los últimos 10 dígitos,
        ya que los contactos existentes pueden tener el teléfono guardado con
        espacios, guiones, '+' o sin código de país.

        Si se indica 'company', solo busca entre los contactos de esa compañía o
        compartidos (sin compañía asignada) — así una compañía no encuentra ni
        reutiliza por accidente el contacto de WhatsApp de otra."""
        digits = re.sub(r'\D', '', phone or '')
        if not digits:
            return self.env['res.partner']
        national = digits[-10:] if len(digits) >= 10 else digits
        domain = ['|', ('mobile', 'like', national), ('phone', 'like', national)]
        if company:
            domain = ['&', ('company_id', 'in', [False, company.id])] + domain
        return self.env['res.partner'].sudo().search(domain, limit=1)

    @api.model
    def find_or_create_partner(self, phone, name=None, image_base64=None, update_if_exists=False, account=None):
        company = account.company_id if account else None
        normalized = self.normalize_phone(phone, account=account)
        partner = self.find_partner_by_phone(normalized, company=company)
        if partner:
            if update_if_exists and name and partner.name != name:
                partner.sudo().write({'name': name})
            # La foto se rellena siempre que falte, sin importar 'update_if_exists':
            # solo se ESCRIBE cuando el contacto no tiene ninguna, nunca sobreescribe
            # una que ya exista. Va en un write() aparte y protegido — una foto
            # corrupta o que Odoo no pueda decodificar NUNCA debe tumbar el resto
            # del procesamiento del contacto/mensaje.
            if image_base64 and not partner.image_1920:
                self._safe_set_image(partner, image_base64)
            return partner
        vals = {
            'name': name or normalized,
            'mobile': normalized,
            'customer_rank': 1,
            'whatsapp_created': True,
        }
        if company:
            # Aísla el contacto a la compañía dueña del número que recibió el mensaje,
            # para que otra compañía en la misma base de datos no lo vea/reutilice.
            vals['company_id'] = company.id
        new_partner = self.env['res.partner'].sudo().create(vals)
        if image_base64:
            self._safe_set_image(new_partner, image_base64)
        return new_partner

    @api.model
    def _safe_set_image(self, partner, image_base64):
        # write() en un campo Image NO valida el contenido al momento — si los
        # bytes no son una imagen real, Odoo los guarda tal cual sin quejarse, y
        # el error solo aparece después, al abrir la ficha y que intente generar
        # las miniaturas. Por eso se valida con PIL ANTES de escribir, no se
        # confía en que write() vaya a rechazarlo.
        try:
            raw = base64.b64decode(image_base64, validate=True)
            with PILImage.open(io.BytesIO(raw)) as img:
                img.verify()
        except Exception as e:
            _logger.warning(
                "Foto de perfil de WhatsApp inválida para el contacto %s (id=%s), se omite: %s",
                partner.name, partner.id, str(e),
            )
            return
        try:
            partner.sudo().write({'image_1920': image_base64})
        except UserError as e:
            _logger.warning(
                "No se pudo guardar la foto de perfil de WhatsApp para el contacto %s (id=%s): %s",
                partner.name, partner.id, str(e),
            )

    @api.model
    def send_message(
        self,
        phone,
        message,
        account=None,
        attachment_base64=None,
        attachment_filename=None,
        attachment_mimetype=None,
        partner_id=None,
    ):
        account = self._resolve_account(account)
        normalized_phone = self.normalize_phone(phone, account=account)
        log = self.env['geco.whatsapp.log']

        if not account.microservice_url:
            error = _("La cuenta '%s' no tiene configurada la URL del microservicio.") % account.name
            log.log_event('outbound', account=account, phone=normalized_phone, partner_id=partner_id,
                           success=False, detail=error)
            raise UserError(error)

        payload = {
            'accountId': account.external_account_id,
            'phone': normalized_phone,
            'message': message,
        }
        if attachment_base64:
            payload['media'] = {
                'mimetype': attachment_mimetype or 'application/octet-stream',
                'data': attachment_base64,
                'filename': attachment_filename or 'documento',
            }

        url = f"{account.microservice_url.rstrip('/')}/api/whatsapp/send"
        try:
            response = requests.post(
                url, json=payload, headers=self._headers(account), timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as e:
            error = _("No se pudo conectar al microservicio de WhatsApp: %s") % str(e)
            log.log_event('outbound', account=account, phone=normalized_phone, partner_id=partner_id,
                           success=False, detail=error)
            raise UserError(error)

        if response.status_code >= 400:
            try:
                detail = response.json().get('error', response.text)
            except Exception:
                detail = response.text
            _logger.warning("WhatsApp send failed (%s): %s", response.status_code, detail)
            error = _("Error al enviar por WhatsApp: %s") % detail
            log.log_event('outbound', account=account, phone=normalized_phone, partner_id=partner_id,
                           success=False, detail=error)
            raise UserError(error)

        log.log_event('outbound', account=account, phone=normalized_phone, partner_id=partner_id,
                       success=True, detail=message[:200] if message else None)
        return response.json()
