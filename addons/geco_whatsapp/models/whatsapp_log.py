# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GecoWhatsappLog(models.Model):
    _name = 'geco.whatsapp.log'
    _description = 'Bitácora de WhatsApp'
    _order = 'create_date desc'

    account_id = fields.Many2one('geco.whatsapp.account', string='Cuenta', ondelete='cascade')
    direction = fields.Selection([
        ('outbound', 'Saliente'),
        ('inbound', 'Entrante'),
        ('status', 'Estado de cuenta'),
        ('webhook_error', 'Webhook rechazado'),
    ], required=True, string='Tipo')
    content_type = fields.Selection([
        ('text', 'Texto'),
        ('location', 'Ubicación'),
        ('contact', 'Contacto'),
        ('event', 'Evento'),
    ], string='Contenido', default='text')
    phone = fields.Char(string='Teléfono')
    partner_id = fields.Many2one('res.partner', string='Contacto')
    success = fields.Boolean(string='Éxito', default=True)
    detail = fields.Text(string='Detalle')
    raw_payload = fields.Text(
        string='JSON crudo',
        help="El payload completo tal como lo mandó el microservicio, sin recortar ni "
             "interpretar — para diagnosticar casos donde el resumen no alcanza.",
    )

    @api.model
    def log_event(self, direction, account=None, phone=None, partner_id=None, success=True, detail=None,
                  content_type='text', raw_payload=None):
        self.sudo().create({
            'account_id': account.id if account else False,
            'direction': direction,
            'content_type': content_type,
            'phone': phone,
            'partner_id': partner_id,
            'success': success,
            'detail': detail,
            'raw_payload': raw_payload,
        })
