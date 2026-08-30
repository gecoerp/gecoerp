# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models


class GecoWhatsappIgnore(models.Model):
    _name = 'geco.whatsapp.ignore'
    _description = 'Números de WhatsApp ignorados'
    _order = 'create_date desc'

    phone = fields.Char(required=True, string='Teléfono')
    reason = fields.Char(string='Motivo')
    company_id = fields.Many2one(
        'res.company', string='Compañía',
        help="Vacío = aplica para todas las compañías. Si se indica una, solo esa "
             "compañía ignora este número; las demás lo siguen procesando normal.",
    )
    active = fields.Boolean(default=True)

    @api.model
    def is_ignored(self, phone, company=None):
        """Comparación tolerante a formato (últimos 10 dígitos), igual que
        find_partner_by_phone, para que no importe con qué prefijo llegue.
        Un registro sin compañía aplica a todas; uno con compañía solo a esa."""
        digits = re.sub(r'\D', '', phone or '')
        if not digits:
            return False
        national = digits[-10:] if len(digits) >= 10 else digits
        domain = [('active', '=', True), ('phone', 'like', national)]
        if company:
            domain += ['|', ('company_id', '=', False), ('company_id', '=', company.id)]
        return bool(self.sudo().search(domain, limit=1))
