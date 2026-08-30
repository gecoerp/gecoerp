# -*- coding: utf-8 -*-
from odoo import api, models

from odoo.addons.geco_mcp.core.tool import mcp_tool


class MCPMixin(models.AbstractModel):
    _inherit = 'geco_mcp.mixin'

    @api.model
    @mcp_tool(
        name='send_whatsapp',
        description=(
            "Sends a WhatsApp message via the connected whatsapp-web.js microservice. "
            "If 'res_model'/'res_id' point to a record with a configured geco.whatsapp.template "
            "(e.g. an invoice or quotation), its PDF report is attached automatically. Use "
            "'partner_id' to resolve the phone number automatically from the contact, or pass "
            "'phone' directly to override it."
        ),
        input_schema={
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'Message text to send (used as caption if a document is attached).',
                },
                'partner_id': {
                    'type': 'integer',
                    'description': "ID of the res.partner contact to send to. Its mobile/phone field "
                                   "is used unless 'phone' is also given.",
                },
                'phone': {
                    'type': 'string',
                    'description': "Phone number to send to, used instead of or as override for "
                                   "partner_id's phone.",
                },
                'res_model': {
                    'type': 'string',
                    'description': "Optional: technical model of a record to attach as PDF, e.g. "
                                   "'account.move' or 'sale.order' — only works if a geco.whatsapp.template "
                                   "with a report exists for that model.",
                },
                'res_id': {
                    'type': 'integer',
                    'description': 'ID of the record in res_model to attach as PDF.',
                },
            },
            'required': ['message'],
        },
        category='write',
    )
    def _mcp_send_whatsapp(self, message, partner_id=None, phone=None, res_model=None, res_id=None):
        partner = self.env['res.partner'].browse(partner_id) if partner_id else self.env['res.partner']
        target_phone = phone or (partner.mobile or partner.phone if partner else None)
        if not target_phone:
            return "Error: no se encontró un teléfono válido para enviar el WhatsApp."

        attachment_ids = []
        if res_model and res_id:
            template = self.env['geco.whatsapp.template']._find_default_for_model(res_model)
            if template and template.report_id:
                b64, filename, mimetype = template.render_attachment(res_id)
                if b64:
                    attachment = self.env['ir.attachment'].create({
                        'name': filename, 'datas': b64, 'mimetype': mimetype,
                    })
                    attachment_ids = [attachment.id]

        if partner:
            target_partner = partner
        else:
            account = self.env['geco.whatsapp.account'].sudo()._get_default()
            target_partner = self.env['geco.whatsapp.service'].find_or_create_partner(target_phone, account=account)
        target_partner.message_post(
            body=message, attachment_ids=attachment_ids, message_type='comment',
            whatsapp_send=True, whatsapp_phone=target_phone,
        )

        if res_model and res_id and res_model != 'res.partner':
            self.env[res_model].browse(res_id).message_post(
                body="Enviado por WhatsApp a %s: %s" % (target_phone, message),
            )

        return {'status': 'success', 'phone': target_phone}
