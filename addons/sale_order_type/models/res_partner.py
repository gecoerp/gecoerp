from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_type = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Order Type",
        domain="[('company_id', 'in', [False, company_id])]",
    )
