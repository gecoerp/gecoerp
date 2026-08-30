# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class GecoWhatsappCompose(models.TransientModel):
    _name = 'geco.whatsapp.compose'
    _description = 'Enviar por WhatsApp'

    partner_id = fields.Many2one('res.partner', string='Contacto')
    phone = fields.Char(string='Teléfono', required=True)
    message = fields.Text(string='Mensaje', required=True)
    res_model = fields.Char(string='Modelo de origen')
    res_id = fields.Integer(string='ID de origen')
    wa_template_id = fields.Many2one('geco.whatsapp.template', string='Plantilla')
    include_attachment = fields.Boolean(string='Adjuntar documento PDF', default=True)
    has_report = fields.Boolean(string='Hay reporte disponible', compute='_compute_has_report')

    @api.depends('wa_template_id')
    def _compute_has_report(self):
        for wizard in self:
            wizard.has_report = bool(wizard.wa_template_id.report_id)

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        res_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        if not (res_model and res_id and res_model != self._name):
            return vals

        record = self.env[res_model].browse(res_id)
        vals['res_model'] = res_model
        vals['res_id'] = res_id

        partner = record if res_model == 'res.partner' else getattr(record, 'partner_id', False)
        if partner:
            vals.setdefault('partner_id', partner.id)
            # Si vino un teléfono explícito en el contexto (p.ej. el botón de WhatsApp
            # junto a un campo teléfono específico), respeta ese valor tal cual.
            if not vals.get('phone'):
                vals['phone'] = partner.mobile or partner.phone or ''

        template = self.env['geco.whatsapp.template']._find_default_for_model(res_model)
        if template:
            vals['wa_template_id'] = template.id
            vals['message'] = template.render_body(res_id)
            phone = template.resolve_phone(record)
            if phone:
                vals['phone'] = phone
        return vals

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and not self.wa_template_id:
            self.phone = self.partner_id.mobile or self.partner_id.phone or ''

    @api.onchange('wa_template_id')
    def _onchange_wa_template_id(self):
        if self.wa_template_id and self.res_model and self.res_id:
            self.message = self.wa_template_id.render_body(self.res_id)
            record = self.env[self.res_model].browse(self.res_id)
            phone = self.wa_template_id.resolve_phone(record)
            if phone:
                self.phone = phone

    def action_send(self):
        self.ensure_one()
        if not self.phone:
            raise UserError(_("Indica un número de teléfono."))

        if self.partner_id:
            partner = self.partner_id
        else:
            account = self.env['geco.whatsapp.account'].sudo()._get_default()
            partner = self.env['geco.whatsapp.service'].find_or_create_partner(self.phone, account=account)

        attachment_ids = []
        if self.include_attachment and self.wa_template_id and self.wa_template_id.report_id and self.res_id:
            b64, filename, mimetype = self.wa_template_id.render_attachment(self.res_id)
            if b64:
                attachment = self.env['ir.attachment'].create({
                    'name': filename, 'datas': b64, 'mimetype': mimetype,
                })
                attachment_ids = [attachment.id]

        partner.message_post(
            body=self.message, attachment_ids=attachment_ids, message_type='comment',
            whatsapp_send=True, whatsapp_phone=self.phone,
        )

        if self.res_model and self.res_id and self.res_model != 'res.partner':
            self.env[self.res_model].browse(self.res_id).message_post(
                body=_("Enviado por WhatsApp a %s: %s") % (self.phone, self.message),
            )

        return {'type': 'ir.actions.act_window_close'}
