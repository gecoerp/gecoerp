from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    print_label_report_id = fields.Many2one(
        comodel_name='ir.actions.report',
        string='Default Label',
        domain=[('model', '=', 'print.product.label.line')],
    )
