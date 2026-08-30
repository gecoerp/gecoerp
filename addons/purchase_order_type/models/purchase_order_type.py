# Copyright (C) 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Type of purchase order"
    _order = "sequence"

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref("purchase.seq_purchase_order")
        return [
            ("code", "=", seq_type.code),
            ("company_id", "in", [False, self.env.company.id]),
        ]

    @api.model
    def _default_sequence_id(self):
        seq_type = self.env.ref("purchase.seq_purchase_order")
        return seq_type.id

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Entry Sequence",
        copy=False,
        domain=lambda self: self._get_domain_sequence_id(),
        default=lambda self: self._default_sequence_id(),
        required=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term", string="Payment Terms"
    )
    incoterm_id = fields.Many2one(comodel_name="account.incoterms", string="Incoterm")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # === Plan de Recurrencia / Suscripción (Estilo Odoo 18 Enterprise) ===
    is_periodic = fields.Boolean(
        string="Es Compra Periódica / Suscripción",
        default=False,
        help="Permite gestionar esta categoría como una suscripción o gasto fijo recurrente con aprovisionamiento de tesorería.",
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
        help="Alinea las compras y aprovisionamientos de este tipo en el primer día de cada mes o período.",
    )
    provision_day_of_month = fields.Integer(
        string="Día de Pago / Corte Habitual",
        default=1,
        help="Día del mes sugerido para el aprovisionamiento o pago recurrente (1 al 31).",
    )
    auto_close_limit = fields.Integer(
        string="Días de Gracia / Cierre Automático",
        default=15,
        help="Días de tolerancia tras el vencimiento antes de alertar o marcar como vencido.",
    )
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Plantilla de Correo para Recordatorio / Orden",
        domain="[('model', '=', 'purchase.order')]",
        help="Plantilla opcional utilizada para enviar notificaciones automáticas al proveedor o responsable.",
    )

    # === Flujo de Efectivo y Métricas Financieras (MRR) ===
    cash_flow_impact = fields.Boolean(
        string="Proyectar en Flujo de Efectivo",
        default=True,
        help="Si está marcado, este tipo de gasto fijo/recurrente se contempla en las proyecciones de tesorería y flujo de caja.",
    )
    estimated_periodic_amount = fields.Monetary(
        string="Provisión Estimada por Período",
        currency_field="currency_id",
        help="Monto promedio proyectado para cada período recurrente.",
    )
    mrr_amount = fields.Monetary(
        string="Gasto Mensual Recurrente (MRR)",
        currency_field="currency_id",
        compute="_compute_mrr_amount",
        store=True,
        help="Gasto normalizado mensual para análisis comparativo de costos recurrentes.",
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

    @api.depends("is_periodic", "estimated_periodic_amount", "billing_period_value", "billing_period_unit")
    def _compute_mrr_amount(self):
        for record in self:
            if not record.is_periodic or not record.estimated_periodic_amount:
                record.mrr_amount = 0.0
                continue
            val = record.billing_period_value or 1
            unit = record.billing_period_unit or "month"
            if unit == "year":
                record.mrr_amount = record.estimated_periodic_amount / (12.0 * val)
            elif unit == "month":
                record.mrr_amount = record.estimated_periodic_amount / (1.0 * val)
            elif unit == "week":
                record.mrr_amount = (record.estimated_periodic_amount * 4.3333) / (1.0 * val)
            elif unit == "days":
                record.mrr_amount = (record.estimated_periodic_amount * 30.4167) / (1.0 * val)
            else:
                record.mrr_amount = record.estimated_periodic_amount


