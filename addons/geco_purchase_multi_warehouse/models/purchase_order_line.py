# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string="Entregar en / Almacén",
        help="Tipo de operación o almacén de entrega específico para esta línea.",
    )
