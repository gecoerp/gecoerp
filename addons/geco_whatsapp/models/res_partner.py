# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """El historial de WhatsApp de un contacto vive directo en su propio chatter
    (igual que correos, notas y actividades) — nada de un modelo/pantalla aparte.
    'whatsapp_send=True' es la señal explícita para que un message_post() también
    dispare un envío real; sin ella, escribir una nota normal en el chatter jamás
    manda nada por WhatsApp. 'whatsapp_phone' permite enviar a un número distinto
    al guardado en el contacto (p.ej. uno resuelto por una plantilla)."""
    _inherit = 'res.partner'

    whatsapp_last_message_date = fields.Datetime(string='Último mensaje de WhatsApp')
    whatsapp_last_message_direction = fields.Selection([
        ('outbound', 'Enviado'),
        ('inbound', 'Recibido'),
    ], string='Dirección del último mensaje')
    whatsapp_created = fields.Boolean(
        string='Creado por WhatsApp', readonly=True, copy=False,
        help="Se marca solo cuando este contacto se creó automáticamente a partir "
             "de un mensaje de WhatsApp de un número que no estaba registrado — no "
             "se activa si el contacto ya existía y solo se le actualizaron datos.",
    )

    def message_post(self, *, body='', message_type='notification', attachment_ids=None, **kwargs):
        send_whatsapp = kwargs.pop('whatsapp_send', False)
        is_inbound = kwargs.pop('whatsapp_inbound', False)
        whatsapp_phone = kwargs.pop('whatsapp_phone', None)
        message = super().message_post(
            body=body, message_type=message_type, attachment_ids=attachment_ids, **kwargs,
        )
        if send_whatsapp or is_inbound:
            self.whatsapp_last_message_date = fields.Datetime.now()
            self.whatsapp_last_message_direction = 'inbound' if is_inbound else 'outbound'
        if send_whatsapp and not is_inbound:
            self._whatsapp_send_out(body, attachment_ids, phone=whatsapp_phone)
        return message

    def _whatsapp_send_out(self, body, attachment_ids, phone=None):
        self.ensure_one()
        attachment_base64 = attachment_filename = attachment_mimetype = None
        if attachment_ids:
            attachment = self.env['ir.attachment'].browse(attachment_ids[0])
            data = attachment.datas
            attachment_base64 = data.decode() if isinstance(data, bytes) else data
            attachment_filename = attachment.name
            attachment_mimetype = attachment.mimetype

        phone = phone or self.mobile or self.phone
        if not phone:
            raise UserError(_("Este contacto no tiene teléfono para enviar por WhatsApp."))

        try:
            service = self.env['geco.whatsapp.service'].sudo()
            # Resuelve la cuenta según la compañía del propio contacto (si la tiene),
            # para no cruzar el envío con el número de WhatsApp de otra compañía.
            account = service._resolve_account(company=self.company_id or None)
            service.send_message(
                phone=phone,
                message=body or '',
                account=account,
                attachment_base64=attachment_base64,
                attachment_filename=attachment_filename,
                attachment_mimetype=attachment_mimetype,
                partner_id=self.id,
            )
        except UserError as e:
            super(ResPartner, self).message_post(
                body=_("⚠️ No se pudo enviar por WhatsApp: %s") % str(e),
                message_type='notification',
            )
