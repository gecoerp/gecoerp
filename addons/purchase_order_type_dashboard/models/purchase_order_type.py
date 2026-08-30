# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from datetime import timedelta
from odoo import api, fields, models, _


class PurchaseOrderType(models.Model):
    _inherit = "purchase.order.type"

    color = fields.Integer(string="Color Index", default=0)
    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="order_type",
        string="Purchase Orders",
    )
    state_rfq_po_count = fields.Integer(string="RFQs", compute="_compute_po_counts")
    invoice_status_no_po_count = fields.Integer(
        string="Nothing to Bill", compute="_compute_po_counts"
    )
    invoice_status_ti_po_count = fields.Integer(
        string="Waiting Bills", compute="_compute_po_counts"
    )
    has_po_entries = fields.Boolean(
        string="Has Entries", compute="_compute_po_counts"
    )
    kanban_dashboard_graph = fields.Text(
        compute="_compute_kanban_dashboard_graph"
    )

    @api.depends(
        "purchase_order_ids",
        "purchase_order_ids.state",
        "purchase_order_ids.invoice_status",
    )
    def _compute_po_counts(self):
        rfq_states = ("draft", "sent", "to approve")
        po_states = ("purchase", "done")
        PurchaseOrder = self.env["purchase.order"]
        fetch_data = PurchaseOrder.read_group(
            [("order_type", "in", self.ids)],
            ["order_type", "state", "invoice_status"],
            ["order_type", "state", "invoice_status"],
            lazy=False,
        )
        result = [
            [
                data["order_type"][0],
                data["state"],
                data["invoice_status"],
                data["__count"],
            ]
            for data in fetch_data
        ]
        for order in self:
            order.state_rfq_po_count = sum(
                r[3] for r in result if r[0] == order.id and r[1] in rfq_states
            )
            order.invoice_status_no_po_count = sum(
                r[3]
                for r in result
                if r[0] == order.id and r[1] in po_states and r[2] == "no"
            )
            order.invoice_status_ti_po_count = sum(
                r[3] for r in result if r[0] == order.id and r[2] == "to invoice"
            )
            order.has_po_entries = bool(
                order.state_rfq_po_count or order.invoice_status_no_po_count or order.invoice_status_ti_po_count
            )

    @api.depends(
        "purchase_order_ids.amount_total",
        "purchase_order_ids.date_order",
        "purchase_order_ids.state",
    )
    def _compute_kanban_dashboard_graph(self):
        today = fields.Date.today()
        day_of_week = today.weekday()
        first_day_of_week = today - timedelta(days=day_of_week)
        format_month = lambda d: d.strftime("%b")

        for order_type in self:
            orders = order_type.purchase_order_ids.filtered(
                lambda o: o.state in ("draft", "sent", "to approve", "purchase", "done")
            )
            if not orders:
                w1 = first_day_of_week - timedelta(days=7)
                w3 = first_day_of_week + timedelta(days=7)
                w4 = first_day_of_week + timedelta(days=14)
                sample_values = [
                    {"label": _("Due"), "value": 30, "type": "past"},
                    {"label": f"{w1.day} {format_month(w1)}", "value": 15, "type": "past"},
                    {"label": _("This Week"), "value": 45, "type": "future"},
                    {"label": f"{w3.day} {format_month(w3)}", "value": 70, "type": "future"},
                    {"label": f"{w4.day} {format_month(w4)}", "value": 35, "type": "future"},
                    {"label": _("Not Due"), "value": 50, "type": "future"},
                ]
                graph_data = [{
                    "key": _("Purchases"),
                    "values": sample_values,
                    "title": _("Purchase Volume"),
                    "is_sample_data": True,
                }]
            else:
                w_minus_1 = first_day_of_week - timedelta(days=7)
                w_curr = first_day_of_week
                w_plus_1 = first_day_of_week + timedelta(days=7)
                w_plus_2 = first_day_of_week + timedelta(days=14)
                w_plus_3 = first_day_of_week + timedelta(days=21)

                val_older = sum(o.amount_total for o in orders if o.date_order and o.date_order.date() < w_minus_1)
                val_w_minus_1 = sum(o.amount_total for o in orders if o.date_order and w_minus_1 <= o.date_order.date() < w_curr)
                val_curr = sum(o.amount_total for o in orders if o.date_order and w_curr <= o.date_order.date() < w_plus_1)
                val_w_plus_1 = sum(o.amount_total for o in orders if o.date_order and w_plus_1 <= o.date_order.date() < w_plus_2)
                val_w_plus_2 = sum(o.amount_total for o in orders if o.date_order and w_plus_2 <= o.date_order.date() < w_plus_3)
                val_later = sum(o.amount_total for o in orders if o.date_order and o.date_order.date() >= w_plus_3)

                lbl_w_minus_1 = f"{w_minus_1.day} {format_month(w_minus_1)}"
                lbl_curr = _("This Week")
                lbl_w_plus_1 = f"{w_plus_1.day} {format_month(w_plus_1)}"
                lbl_w_plus_2 = f"{w_plus_2.day} {format_month(w_plus_2)}"

                values = [
                    {"label": _("Due"), "value": val_older, "type": "past"},
                    {"label": lbl_w_minus_1, "value": val_w_minus_1, "type": "past"},
                    {"label": lbl_curr, "value": val_curr, "type": "future"},
                    {"label": lbl_w_plus_1, "value": val_w_plus_1, "type": "future"},
                    {"label": lbl_w_plus_2, "value": val_w_plus_2, "type": "future"},
                    {"label": _("Not Due"), "value": val_later, "type": "future"},
                ]
                graph_data = [{
                    "key": _("Purchases"),
                    "values": values,
                    "title": _("Purchase Volume"),
                    "is_sample_data": False,
                }]

            order_type.kanban_dashboard_graph = json.dumps(graph_data)

    def action_create_rfq(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Request for Quotation"),
            "res_model": "purchase.order",
            "view_mode": "form",
            "views": [(False, "form")],
            "context": {
                "default_order_type": self.id,
                "quotation_only": True,
            },
        }
