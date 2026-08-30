# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_to_multi_picking(self, picking_type):
        if not self.group_id:
            self.group_id = self.group_id.create(self._prepare_group_vals())
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("Debe configurar una ubicación de proveedor para el contacto %s", self.partner_id.name))

        dest_location_id = picking_type.default_location_dest_id.id
        if self.dest_address_id and picking_type.code == "dropship":
            dest_location_id = self.dest_address_id.property_stock_customer.id

        return {
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': dest_location_id,
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'state': 'draft',
        }

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type == 'consu' for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                # Agrupar líneas por picking_type_id (o por el picking_type_id global de la orden)
                lines_by_picking_type = {}
                for line in order.order_line.filtered(lambda l: l.product_id.type == 'consu' and not l.display_type):
                    ptype = line.picking_type_id or order.picking_type_id
                    lines_by_picking_type.setdefault(ptype, self.env['purchase.order.line'])
                    lines_by_picking_type[ptype] |= line

                for picking_type, lines in lines_by_picking_type.items():
                    existing_pickings = order.picking_ids.filtered(
                        lambda x: x.state not in ('done', 'cancel') and x.picking_type_id == picking_type
                    )
                    if not existing_pickings:
                        res = order._prepare_to_multi_picking(picking_type)
                        picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    else:
                        picking = existing_pickings[0]

                    moves = lines._create_stock_moves(picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()

                    forward_pickings = self.env['stock.picking']._get_impacted_pickings(moves)
                    (picking | forward_pickings).action_confirm()
                    picking.message_post_with_source(
                        'mail.message_origin_link',
                        render_values={'self': picking, 'origin': order},
                        subtype_xmlid='mail.mt_note',
                    )
        return True
