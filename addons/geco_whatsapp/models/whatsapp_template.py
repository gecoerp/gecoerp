# -*- coding: utf-8 -*-
import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class GecoWhatsappTemplate(models.Model):
    _name = 'geco.whatsapp.template'
    _description = 'GECO WhatsApp Template'
    _order = 'sequence, id'

    name = fields.Char(string='Nombre', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        'ir.model', string='Aplica a', required=True, ondelete='cascade',
        domain=[('transient', '=', False)],
    )
    model = fields.Char(related='model_id.model', store=True, readonly=True)
    phone_field = fields.Char(
        string='Campo de teléfono', required=True, default='mobile',
        help="Nombre técnico del campo de donde tomar el teléfono destino. Admite rutas con "
             "punto, ej. 'partner_id.mobile'.",
    )
    body = fields.Text(
        string='Mensaje', required=True,
        default="Hola {{ object.partner_id.name }}, te compartimos información sobre {{ object.name }}.",
        help="Usa variables tipo {{ object.partner_id.name }} — se resuelven contra el registro de origen.",
    )
    report_id = fields.Many2one(
        'ir.actions.report', string='Reporte PDF a adjuntar',
        domain="[('model', '=', model)]",
        help="Si se define, su PDF se adjunta automáticamente al enviar.",
    )

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for template in self:
            if not template.model_id:
                continue
            target_fields = self.env[template.model_id.model]._fields
            if 'mobile' in target_fields:
                template.phone_field = 'mobile'
            elif 'phone' in target_fields:
                template.phone_field = 'phone'
            elif 'partner_id' in target_fields:
                template.phone_field = 'partner_id.mobile'

    def render_body(self, res_id):
        self.ensure_one()
        rendered = self.env['mail.render.mixin']._render_template(
            self.body, self.model, [res_id], engine='inline_template',
        )
        return rendered.get(res_id) or self.body

    def resolve_phone(self, record):
        self.ensure_one()
        try:
            values = record.mapped(self.phone_field)
        except Exception:
            return False
        return values[0] if values else False

    def render_attachment(self, res_id):
        self.ensure_one()
        if not self.report_id:
            return None, None, None
        report = self.report_id
        content, _report_type = report._render(report.report_name, [res_id])
        if isinstance(content, str):
            content = content.encode()
        record = self.env[self.model].browse(res_id)
        filename = '%s.pdf' % (getattr(record, 'name', None) or self.model).replace('/', '-')
        return base64.b64encode(content).decode(), filename, 'application/pdf'

    @api.model
    def _find_default_for_model(self, model_name):
        return self.search([('model', '=', model_name)], limit=1)
