from odoo import api, fields, models, _


class SaleOrderType(models.Model):
    _name = "sale.order.type"
    _description = "Type of sale order"
    _order = "sequence, id"

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref("sale.seq_sale_order", raise_if_not_found=False)
        if seq_type:
            return [
                ("code", "=", seq_type.code),
                ("company_id", "in", [False, self.env.company.id]),
            ]
        return [("company_id", "in", [False, self.env.company.id])]

    @api.model
    def _default_sequence_id(self):
        seq_type = self.env.ref("sale.seq_sale_order", raise_if_not_found=False)
        return seq_type.id if seq_type else False

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=10)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Entry Sequence",
        copy=False,
        domain=lambda self: self._get_domain_sequence_id(),
        default=lambda self: self._default_sequence_id(),
        required=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Payment Terms",
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
    )
    incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        string="Incoterm",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Equipo de Ventas",
        help="Equipo de ventas asociado por defecto a este tipo de venta / sucursal.",
    )
    user_id = fields.Many2one(
        related="team_id.user_id",
        string="Líder del Equipo",
        readonly=True,
    )

    # === Plan de Recurrencia / Suscripción (Estilo Odoo 18 Enterprise) ===
    is_periodic = fields.Boolean(
        string="Es Venta Periódica / Suscripción",
        default=False,
        help="Permite gestionar este tipo como una suscripción, contrato o póliza de ingresos recurrentes.",
    )
    billing_period_value = fields.Integer(
        string="Período de Facturación",
        default=1,
        help="Valor numérico del intervalo de recurrencia (ej. 1, 2, 3, 6, 12).",
    )
    billing_period_unit = fields.Selection(
        selection=[
            ("days", "Días"),
            ("week", "Semanas"),
            ("month", "Meses"),
            ("year", "Años"),
        ],
        string="Unidad de Período",
        default="month",
        required=True,
    )
    billing_period_display = fields.Char(
        string="Frecuencia",
        compute="_compute_billing_period_display",
        store=True,
    )
    billing_first_day = fields.Boolean(
        string="Alinear al Primer Día del Período",
        default=False,
        help="Alinea las facturas y cobros de esta suscripción en el primer día de cada mes o período.",
    )
    billing_day_of_month = fields.Integer(
        string="Día de Cobro / Facturación Habitual",
        default=1,
        help="Día del mes habitual en que se emite la factura o se realiza el cobro de esta suscripción (1 al 31).",
    )
    auto_close_limit = fields.Integer(
        string="Días de Gracia / Cierre Automático",
        default=15,
        help="Días de tolerancia tras el vencimiento antes de alertar o cerrar la suscripción impaga.",
    )
    invoice_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Plantilla de Correo para Facturación Automática",
        domain="[('model', '=', 'sale.order')]",
        help="Plantilla de correo para envío automático al cliente al generarse su renovación.",
    )

    # === Flujo de Efectivo y Métricas Financieras (MRR) ===
    cash_flow_impact = fields.Boolean(
        string="Proyectar en Flujo de Efectivo",
        default=True,
        help="Si está marcado, este tipo de venta recurrente se contempla en las proyecciones de ingresos de tesorería.",
    )
    estimated_recurring_revenue = fields.Monetary(
        string="Ingreso Estimado por Período",
        currency_field="currency_id",
        help="Monto promedio proyectado de ingresos por período para el flujo de efectivo.",
    )
    mrr_revenue = fields.Monetary(
        string="Ingreso Mensual Recurrente (MRR)",
        currency_field="currency_id",
        compute="_compute_mrr_revenue",
        store=True,
        help="Ingreso recurrente normalizado a base mensual para cálculo homogéneo de ingresos.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("is_periodic", "billing_period_value", "billing_period_unit")
    def _compute_billing_period_display(self):
        unit_names = {
            "days": ("Día", "Días"),
            "week": ("Semana", "Semanas"),
            "month": ("Mes", "Meses"),
            "year": ("Año", "Años"),
        }
        for record in self:
            if not record.is_periodic:
                record.billing_period_display = "A demanda"
                continue
            val = record.billing_period_value or 1
            unit = record.billing_period_unit or "month"
            singular, plural = unit_names.get(unit, (unit, unit))
            unit_str = singular if val == 1 else plural
            record.billing_period_display = f"{val} {unit_str}"

    @api.depends("is_periodic", "estimated_recurring_revenue", "billing_period_value", "billing_period_unit")
    def _compute_mrr_revenue(self):
        for record in self:
            if not record.is_periodic or not record.estimated_recurring_revenue:
                record.mrr_revenue = 0.0
                continue
            val = record.billing_period_value or 1
            unit = record.billing_period_unit or "month"
            if unit == "year":
                record.mrr_revenue = record.estimated_recurring_revenue / (12.0 * val)
            elif unit == "month":
                record.mrr_revenue = record.estimated_recurring_revenue / (1.0 * val)
            elif unit == "week":
                record.mrr_revenue = (record.estimated_recurring_revenue * 4.3333) / (1.0 * val)
            elif unit == "days":
                record.mrr_revenue = (record.estimated_recurring_revenue * 30.4167) / (1.0 * val)
            else:
                record.mrr_revenue = record.estimated_recurring_revenue


