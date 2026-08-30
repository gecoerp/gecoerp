# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    geco_openai_api_key = fields.Char(
        string='OpenAI API Key',
        config_parameter='geco_ai.openai_api_key',
        help="Your secret API key from OpenAI (ChatGPT). Starts with 'sk-...'."
    )
    geco_gemini_api_key = fields.Char(
        string='Gemini API Key',
        config_parameter='geco_ai.gemini_api_key',
        help="Your secret API key from Google Generative AI (Gemini)."
    )
    geco_ai_provider = fields.Selection([
        ('openai', 'OpenAI (ChatGPT)'),
        ('gemini', 'Google Gemini')
    ], string='Default AI Provider', config_parameter='geco_ai.provider', default='openai')
    
    geco_ai_token_limit = fields.Integer(
        string='Monthly Token Limit',
        config_parameter='geco_ai.token_limit',
        default=0,
        help='Set to 0 for unlimited. An email will be sent when consumption reaches 90%.'
    )
    geco_ai_alert_email = fields.Char(
        string='Alert Email',
        config_parameter='geco_ai.alert_email',
        help='Email address to send token limit alerts.'
    )
    geco_ai_cost_input_1m = fields.Float(
        string='Costo 1M Tokens (Entrada - USD)',
        config_parameter='geco_ai.cost_input_1m',
        default=5.0,
        help='Costo en USD por 1 Millón de tokens de entrada (Prompt).'
    )
    geco_ai_cost_output_1m = fields.Float(
        string='Costo 1M Tokens (Salida - USD)',
        config_parameter='geco_ai.cost_output_1m',
        default=15.0,
        help='Costo en USD por 1 Millón de tokens de salida (Respuesta).'
    )
