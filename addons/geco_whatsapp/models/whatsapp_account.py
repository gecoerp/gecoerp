# -*- coding: utf-8 -*-
import logging
import secrets
import uuid

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 20
# Timeout corto y separado para el ping de salud — la idea es detectar un
# microservicio caído o colgado en segundos, no esperar los 20s que se le
# da a una operación normal de cuenta.
HEALTH_CHECK_TIMEOUT = 5

STATUS_SELECTION = [
    ('draft', 'Sin registrar'),
    ('starting', 'Iniciando'),
    ('qr', 'Esperando QR'),
    ('connected', 'Conectado'),
    ('stopped', 'Detenido'),
    ('error', 'Error'),
]


class GecoWhatsappAccount(models.Model):
    _name = 'geco.whatsapp.account'
    _description = 'GECO WhatsApp Account'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Compañía', required=True,
        default=lambda self: self.env.company,
        help="A qué compañía pertenece este número de WhatsApp. Cada compañía "
             "resuelve su propia cuenta por defecto de forma independiente.",
    )
    is_default = fields.Boolean(
        string='Cuenta por defecto',
        help="Se usa cuando un envío no especifica una cuenta en particular, "
             "dentro de la misma compañía.",
    )
    default_country_code = fields.Char(
        string='Código de País por Defecto', default='52',
        help="Se antepone a los números que no incluyan código de país, ej. 52 para México. "
             "Cada cuenta/compañía puede tener el suyo.",
    )
    microservice_url = fields.Char(
        string='URL del Microservicio', required=True,
        help="URL base del microservicio de WhatsApp, ej. http://localhost:3006",
    )
    external_account_id = fields.Char(
        string='Account ID', required=True, copy=False,
        default=lambda self: str(uuid.uuid4()),
        help="Identificador de esta cuenta dentro del microservicio.",
    )
    internal_token = fields.Char(
        string='Token Interno',
        help="Valor de X-Internal-Token que exige el microservicio.",
    )
    webhook_secret = fields.Char(
        string='Secreto del Webhook', copy=False,
        default=lambda self: secrets.token_urlsafe(24),
        help="El microservicio debe reenviar este valor en el header X-Webhook-Secret "
             "de cada webhook, para que GECOERP pueda verificar su autenticidad.",
    )
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='draft', readonly=True)
    phone = fields.Char(string='Teléfono Vinculado', readonly=True)
    qr_code = fields.Binary(string='Código QR', readonly=True, attachment=False)

    _sql_constraints = [
        ('external_account_id_unique', 'unique(external_account_id)',
         'Ya existe una cuenta con ese Account ID.'),
    ]

    @api.constrains('is_default', 'active', 'company_id')
    def _check_single_default(self):
        for account in self.filtered('is_default'):
            others = self.search([
                ('is_default', '=', True), ('id', '!=', account.id),
                ('company_id', '=', account.company_id.id),
            ])
            if others:
                others.write({'is_default': False})

    # ------------------------------------------------------------------
    # Helpers HTTP
    # ------------------------------------------------------------------

    def _headers(self):
        self.ensure_one()
        return {'X-Internal-Token': self.internal_token} if self.internal_token else {}

    def _webhook_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        return f"{base_url}/geco_whatsapp/webhook/{self.external_account_id}"

    def _call_microservice(self, method, path, timeout=None, **kwargs):
        self.ensure_one()
        if not self.microservice_url:
            raise UserError(_("Configura la URL del microservicio primero."))
        url = f"{self.microservice_url.rstrip('/')}{path}"
        try:
            response = requests.request(
                method, url, headers=self._headers(), timeout=timeout or REQUEST_TIMEOUT, **kwargs,
            )
        except requests.RequestException as e:
            raise UserError(_("No se pudo conectar al microservicio de WhatsApp: %s") % str(e))
        if response.status_code >= 400:
            try:
                detail = response.json().get('error', response.text)
            except Exception:
                detail = response.text
            raise UserError(_("El microservicio respondió con un error: %s") % detail)
        try:
            return response.json()
        except ValueError:
            return {}

    def _check_gateway_health(self):
        """Ping liviano a la raíz del microservicio (sin autenticación, sin tocar
        cuentas) con timeout corto — permite distinguir 'el proceso ni siquiera
        responde' (caído/colgado) de 'responde pero esta cuenta no está
        conectada'. Devuelve (ok: bool, detail: str|None)."""
        self.ensure_one()
        if not self.microservice_url:
            return False, _("No hay URL de microservicio configurada.")
        url = self.microservice_url.rstrip('/') + '/'
        try:
            response = requests.get(url, timeout=HEALTH_CHECK_TIMEOUT)
        except requests.exceptions.Timeout:
            return False, _(
                "El microservicio no respondió en %s segundos — probablemente esté colgado."
            ) % HEALTH_CHECK_TIMEOUT
        except requests.RequestException as e:
            return False, _("No se pudo contactar al microservicio: %s") % str(e)
        if response.status_code >= 400:
            return False, _(
                "El microservicio respondió con un error HTTP %s."
            ) % response.status_code
        return True, None

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def action_register(self):
        """Da de alta (o actualiza) esta cuenta en el microservicio, indicándole
        a dónde debe reenviar los mensajes entrantes."""
        self.ensure_one()
        if not self.webhook_secret:
            self.webhook_secret = secrets.token_urlsafe(24)
        data = self._call_microservice('POST', '/api/accounts', json={
            'id': self.external_account_id,
            'name': self.name,
            'webhook_url': self._webhook_url(),
            'webhook_secret': self.webhook_secret,
        })
        self._apply_remote_status(data)
        return True

    def action_refresh_status(self):
        """Verifica el estado real del microservicio (¿está caído o colgado?) y,
        si responde, el estado real de esta cuenta — siempre mostrando un popup
        con el resultado, sea bueno o malo, en vez de fallar en silencio o
        limitarse a escribir el campo sin avisar nada."""
        self.ensure_one()
        healthy, health_error = self._check_gateway_health()
        if not healthy:
            self.status = 'error'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Servicio de WhatsApp no disponible"),
                    'message': health_error,
                    'type': 'danger',
                    'sticky': True,
                },
            }

        try:
            data = self._call_microservice('GET', f'/api/accounts/{self.external_account_id}')
            self._apply_remote_status(data)
            qr_data = self._call_microservice('GET', f'/api/accounts/{self.external_account_id}/qr')
            self._apply_qr(qr_data.get('qr_code'))
        except UserError as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("No se pudo actualizar el estado de la cuenta"),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                },
            }

        status_label = dict(STATUS_SELECTION).get(self.status, self.status)
        message = _("Microservicio activo. Estado de la cuenta: %s") % status_label
        if self.phone:
            message += " (%s)" % self.phone
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Estado actualizado"),
                'message': message,
                'type': 'success' if self.status == 'connected' else 'warning',
                'sticky': False,
            },
        }

    def action_view_qr(self):
        """Abre el diálogo de vinculación por QR con sondeo en vivo (como el
        modal de conexión del frontend de referencia: inicia la sesión y el
        propio diálogo va consultando el estado cada 2 segundos)."""
        self.ensure_one()
        try:
            self.action_start()
        except UserError:
            pass
        return {
            'type': 'ir.actions.client',
            'tag': 'geco_whatsapp_qr_dialog',
            'params': {'account_id': self.id},
        }

    def get_qr_status(self):
        """Consulta liviana de estado usada por el diálogo de QR mientras hace polling.
        A diferencia de action_refresh_status, no reintenta iniciar la sesión."""
        self.ensure_one()
        data = self._call_microservice('GET', f'/api/accounts/{self.external_account_id}')
        self._apply_remote_status(data)
        if self.status == 'connected':
            self.qr_code = False
        else:
            qr_data = self._call_microservice('GET', f'/api/accounts/{self.external_account_id}/qr')
            self._apply_qr(qr_data.get('qr_code'))
        qr_code_url = None
        if self.qr_code:
            qr_value = self.qr_code
            if isinstance(qr_value, bytes):
                qr_value = qr_value.decode()
            qr_code_url = f"data:image/png;base64,{qr_value}"
        return {
            'status': self.status,
            'phone': self.phone,
            'qr_code': qr_code_url,
        }

    def action_start(self):
        self.ensure_one()
        self._call_microservice('POST', f'/api/accounts/{self.external_account_id}/start')
        self.status = 'starting'
        return True

    def action_stop(self):
        self.ensure_one()
        self._call_microservice('POST', f'/api/accounts/{self.external_account_id}/stop')
        self.status = 'stopped'
        self.qr_code = False
        return True

    def _apply_remote_status(self, data):
        self.ensure_one()
        if not data:
            return
        vals = {}
        if data.get('status'):
            vals['status'] = data['status']
        if data.get('phone'):
            vals['phone'] = data['phone']
        if vals:
            self.write(vals)

    def _apply_qr(self, qr_data_url):
        self.ensure_one()
        if not qr_data_url:
            self.qr_code = False
            return
        try:
            _prefix, b64_data = qr_data_url.split(',', 1)
            self.qr_code = b64_data
        except Exception:
            _logger.warning("No se pudo decodificar el QR recibido del microservicio")

    @api.model
    def _get_default(self, company=None):
        # sudo(): resolver la cuenta por defecto no debe requerir que el usuario
        # que envía un mensaje tenga acceso directo al modelo de cuentas.
        # Cada compañía resuelve su propia cuenta por defecto de forma independiente
        # — así, dos compañías en la misma base de datos nunca comparten número.
        company_id = (company or self.env.company).id
        accounts = self.sudo()
        account = accounts.search([('is_default', '=', True), ('company_id', '=', company_id)], limit=1)
        if not account:
            account = accounts.search([('company_id', '=', company_id)], limit=1)
        return account
