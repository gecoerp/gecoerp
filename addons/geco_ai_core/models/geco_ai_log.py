# -*- coding: utf-8 -*-
from odoo import api, fields, models

class GecoAiLog(models.Model):
    _name = 'geco.ai.log'
    _description = 'GECO AI Audit Log'
    _order = 'create_date desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True, readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Compañía',
        required=True, default=lambda self: self.env.company,
        index=True
    )
    module_caller = fields.Char(string='Calling Module', readonly=True)
    provider = fields.Selection([('openai', 'OpenAI'), ('gemini', 'Gemini')], string='Provider', readonly=True)
    model_used = fields.Char(string='AI Model', readonly=True)
    
    prompt = fields.Text(string='Prompt (Input)', readonly=True)
    response = fields.Text(string='Response (Output)', readonly=True)
    
    tokens_prompt = fields.Integer(string='Prompt Tokens', default=0, readonly=True)
    tokens_completion = fields.Integer(string='Completion Tokens', default=0, readonly=True)
    tokens_total = fields.Integer(string='Total Tokens', default=0, readonly=True)
    
    cost_estimate = fields.Float(string='Est. Cost (USD)', digits=(10, 6), default=0.0, readonly=True)
    cost_mxn = fields.Float(string='Costo (MXN)', digits=(10, 6), compute='_compute_cost_mxn', store=True)
    
    @api.depends('cost_estimate')
    def _compute_cost_mxn(self):
        for log in self:
            mxn_currency = self.env['res.currency'].search([('name', '=', 'MXN')], limit=1)
            usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            
            if mxn_currency and usd_currency:
                # convert from USD to MXN based on Gecoerp's currency rates
                log.cost_mxn = usd_currency._convert(log.cost_estimate, mxn_currency, self.env.company, log.create_date or fields.Date.today())
            else:
                log.cost_mxn = log.cost_estimate * 18.50 # fallback rate
    
    @api.depends('create_date', 'user_id', 'provider')
    def _compute_name(self):
        for log in self:
            log.name = f"{log.provider or 'AI'} - {log.user_id.name or 'System'} ({log.create_date})"
