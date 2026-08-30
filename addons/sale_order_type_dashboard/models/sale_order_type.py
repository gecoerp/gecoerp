import json
from datetime import timedelta
from odoo import api, fields, models, _


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    color = fields.Integer(string="Color Index", default=0)
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="order_type",
        string="Sale Orders",
    )
    state_quotation_count = fields.Integer(
        string="Quotations", compute="_compute_sale_counts"
    )
    invoice_status_no_count = fields.Integer(
        string="Nothing to Invoice", compute="_compute_sale_counts"
    )
    invoice_status_ti_count = fields.Integer(
        string="To Invoice", compute="_compute_sale_counts"
    )
    has_sale_entries = fields.Boolean(
        string="Has Entries", compute="_compute_sale_counts"
    )
    kanban_dashboard_graph = fields.Text(
        compute="_compute_kanban_dashboard_graph"
    )

    @api.depends(
        "sale_order_ids",
        "sale_order_ids.state",
        "sale_order_ids.invoice_status",
    )
    def _compute_sale_counts(self):
        quotation_states = ("draft", "sent")
        order_states = ("sale", "done")
        SaleOrder = self.env["sale.order"]
        fetch_data = SaleOrder.read_group(
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
        for s_type in self:
            s_type.state_quotation_count = sum(
                r[3] for r in result if r[0] == s_type.id and r[1] in quotation_states
            )
            s_type.invoice_status_no_count = sum(
                r[3]
                for r in result
                if r[0] == s_type.id and r[1] in order_states and r[2] == "no"
            )
            s_type.invoice_status_ti_count = sum(
                r[3] for r in result if r[0] == s_type.id and r[2] == "to invoice"
            )
            s_type.has_sale_entries = bool(
                s_type.state_quotation_count or s_type.invoice_status_no_count or s_type.invoice_status_ti_count
            )

    @api.depends(
        "sale_order_ids.amount_total",
        "sale_order_ids.date_order",
        "sale_order_ids.state",
    )
    def _compute_kanban_dashboard_graph(self):
        today = fields.Date.today()
        day_of_week = today.weekday()
        first_day_of_week = today - timedelta(days=day_of_week)
        format_month = lambda d: d.strftime("%b")

        for s_type in self:
            orders = s_type.sale_order_ids.filtered(
                lambda o: o.state in ("draft", "sent", "sale", "done")
            )
            if not orders:
                w1 = first_day_of_week - timedelta(days=7)
                w3 = first_day_of_week + timedelta(days=7)
                w4 = first_day_of_week + timedelta(days=14)
                sample_values = [
                    {"label": _("Due"), "value": 40, "type": "past"},
                    {"label": f"{w1.day} {format_month(w1)}", "value": 20, "type": "past"},
                    {"label": _("This Week"), "value": 60, "type": "future"},
                    {"label": f"{w3.day} {format_month(w3)}", "value": 85, "type": "future"},
                    {"label": f"{w4.day} {format_month(w4)}", "value": 45, "type": "future"},
                    {"label": _("Not Due"), "value": 65, "type": "future"},
                ]
                graph_data = [{
                    "key": _("Sales"),
                    "values": sample_values,
                    "title": _("Sale Volume"),
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
                    "key": _("Sales"),
                    "values": values,
                    "title": _("Sale Volume"),
                    "is_sample_data": False,
                }]

            s_type.kanban_dashboard_graph = json.dumps(graph_data)

    def action_create_quotation(self):
        self.ensure_one()
        ctx = {"default_order_type": self.id}
        if self.team_id:
            ctx["default_team_id"] = self.team_id.id
        return {
            "type": "ir.actions.act_window",
            "name": _("New Quotation"),
            "res_model": "sale.order",
            "view_mode": "form",
            "views": [(False, "form")],
            "context": ctx,
        }

    def action_open_team(self):
        self.ensure_one()
        if not self.team_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.team_id.name,
            "res_model": "crm.team",
            "res_id": self.team_id.id,
            "view_mode": "form",
            "views": [(False, "form")],
        }
