# -*- coding: utf-8 -*-
from odoo import fields, models


class GecoWhatsappGatewayLog(models.Model):
    """Lee directo la tabla whatsapp_gateway_logs que escribe el microservicio
    de Node (comparte la misma base Postgres, en su propia tabla — ver
    whatsapp_service.py). _auto=False: GECOERP solo consulta, nunca administra
    ni modifica el esquema de esta tabla; eso lo hace el microservicio."""
    _name = 'geco.whatsapp.gateway.log'
    _description = 'Bitácora del microservicio de WhatsApp'
    _table = 'whatsapp_gateway_logs'
    _auto = False
    _order = 'id desc'

    account_id = fields.Char(string='Cuenta (microservicio)', readonly=True)
    direction = fields.Char(string='Tipo', readonly=True)
    content_type = fields.Char(string='Contenido', readonly=True)
    phone = fields.Char(string='Teléfono', readonly=True)
    success = fields.Boolean(string='Éxito', readonly=True)
    detail = fields.Text(string='Detalle', readonly=True)
    create_date = fields.Datetime(string='Fecha', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_gateway_logs (
                id SERIAL PRIMARY KEY,
                account_id VARCHAR,
                direction VARCHAR,
                content_type VARCHAR,
                phone VARCHAR,
                success BOOLEAN,
                detail TEXT,
                create_date TIMESTAMP
            );
        """)

