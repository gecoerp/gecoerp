from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Type",
        ondelete="restrict",
        domain="[('company_id', 'in', [False, company_id])]",
        compute="_compute_partner_order_type",
        store=True,
        readonly=False,
    )

    # === Campos de Recurrencia / Suscripción (Estilo Enterprise) ===
    is_subscription = fields.Boolean(
        related="order_type.is_periodic",
        string="Es Venta / Suscripción Recurrente",
        store=True,
    )
    subscription_state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("in_progress", "En Progreso / Activa"),
            ("paused", "Pausada"),
            ("closed", "Cerrada"),
        ],
        string="Estado de la Suscripción",
        default="in_progress",
    )
    start_date = fields.Date(
        string="Fecha de Inicio",
        default=fields.Date.context_today,
    )
    next_invoice_date = fields.Date(
        string="Próxima Fecha de Facturación / Cobro",
    )
    end_date = fields.Date(
        string="Fecha de Finalización",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_set_sale_type(self):
        sale_type = (
            self.partner_id.sale_type
            or self.partner_id.commercial_partner_id.sale_type
        )
        if sale_type:
            self.order_type = sale_type

    @api.onchange("order_type")
    def onchange_order_type(self):
        for order in self:
            if order.order_type.payment_term_id:
                order.payment_term_id = order.order_type.payment_term_id.id
            if order.order_type.pricelist_id:
                order.pricelist_id = order.order_type.pricelist_id.id
            if order.order_type.warehouse_id and hasattr(order, "warehouse_id"):
                order.warehouse_id = order.order_type.warehouse_id.id
            if order.order_type.incoterm_id:
                order.incoterm = order.order_type.incoterm_id.id
            if order.order_type.team_id:
                order.team_id = order.order_type.team_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if not values.get("order_type") and values.get("partner_id"):
                partner = self.env["res.partner"].browse(values["partner_id"])
                if partner.sale_type:
                    values["order_type"] = partner.sale_type.id

            if values.get("order_type") and not values.get("team_id"):
                sale_type = self.env["sale.order.type"].browse(values["order_type"])
                if sale_type.team_id:
                    values["team_id"] = sale_type.team_id.id

            if values.get("name", _("New")) in (_("New"), "/", "New", False) and values.get("order_type"):
                sale_type = self.env["sale.order.type"].browse(values["order_type"])
                if sale_type.sequence_id:
                    seq_date = None
                    if values.get("date_order"):
                        seq_date = fields.Datetime.context_timestamp(
                            self, fields.Datetime.to_datetime(values["date_order"])
                        )
                    values["name"] = sale_type.sequence_id.next_by_id(sequence_date=seq_date) or _("New")

        return super().create(vals_list)

    @api.constrains("company_id", "order_type")
    def _check_sale_type_company(self):
        for order in self:
            if order.order_type and order.order_type.company_id and order.company_id:
                if order.order_type.company_id != order.company_id:
                    raise ValidationError(_("Document's company and sale type's company mismatch"))

    @api.depends("partner_id")
    def _compute_partner_order_type(self):
        for record in self:
            if record.partner_id and not record.order_type:
                record.order_type = record.partner_id.sale_type
            elif record.partner_id and record.order_type:
                record.order_type = record.order_type
            else:
                record.order_type = False
