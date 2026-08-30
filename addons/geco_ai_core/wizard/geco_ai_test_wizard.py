# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class GecoAiTestWizard(models.TransientModel):
    _name = 'geco.ai.test.wizard'
    _description = 'GECO AI Engine Connection Test Wizard'

    provider = fields.Selection([
        ('openai', 'OpenAI (ChatGPT)'),
        ('gemini', 'Google Gemini')
    ], string='Proveedor a Probar', required=True, default=lambda self: self.env['ir.config_parameter'].sudo().get_param('geco_ai.provider', 'openai'))

    prompt = fields.Text(string='Mensaje de Prueba', required=True, default='Hola GECO AI, responde brevemente: ¿Quién eres?')
    
    response = fields.Text(string='Respuesta de la IA', readonly=True)
    
    status = fields.Selection([
        ('draft', 'Sin Probar'),
        ('success', 'Conexión Exitosa'),
        ('error', 'Error de Conexión')
    ], string='Estado de la Conexión', default='draft', readonly=True)

    status_message = fields.Text(string='Detalles del Estado / Error', readonly=True)

    def action_test_connection(self):
        self.ensure_one()
        self.status = 'draft'
        self.response = ''
        self.status_message = ''
        
        config_param = self.env['ir.config_parameter'].sudo()
        original_provider = config_param.get_param('geco_ai.provider', 'openai')
        
        try:
            config_param.set_param('geco_ai.provider', self.provider)
            
            system_prompt = "Eres un motor de inteligencia artificial llamado GECO AI integrado en GECOERP. Responde de manera muy breve en español."
            
            ai_response = self.env['geco.ai.core'].generate_text(
                system_prompt=system_prompt,
                user_prompt=self.prompt,
                module_caller='GECO AI Test Wizard',
                max_tokens=300
            )
            
            self.response = ai_response
            self.status = 'success'
            self.status_message = _("Conexión establecida exitosamente con el proveedor %s.") % self.provider.upper()
            
        except Exception as e:
            self.status = 'error'
            self.status_message = str(e)
            _logger.exception("Error al verificar conexión con GECO AI")
        finally:
            config_param.set_param('geco_ai.provider', original_provider)
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
