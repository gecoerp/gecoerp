# -*- coding: utf-8 -*-
import json

from odoo import api, models, _
from odoo.exceptions import UserError
import openai

# Si el modelo corta la respuesta por falta de espacio (finish_reason == 'length' /
# FinishReason.MAX_TOKENS), reintentamos una sola vez con el doble de presupuesto,
# hasta este tope — evita respuestas cortadas a media frase sin disparar el costo
# indefinidamente si algo sale mal.
MAX_TOKENS_RETRY_CAP = 8000


class GecoAiEngine(models.AbstractModel):
    _name = 'geco.ai.core'
    _description = 'GECO AI Master Engine'

    @api.model
    def _build_openai_tools(self, tools):
        return [
            {
                'type': 'function',
                'function': {
                    'name': t['name'],
                    'description': t.get('description') or '',
                    'parameters': t.get('inputSchema') or {'type': 'object', 'properties': {}},
                },
            }
            for t in tools
        ]

    @api.model
    def _build_gemini_tools(self, tools):
        return [{
            'function_declarations': [
                {
                    'name': t['name'],
                    'description': t.get('description') or '',
                    'parameters': t.get('inputSchema') or {'type': 'object', 'properties': {}},
                }
                for t in tools
            ],
        }]

    @api.model
    def generate_text(self, system_prompt, user_prompt, module_caller='Unknown', max_tokens=2500, tools=None):
        """
        API Interna Global para consumir IA desde cualquier módulo de GECOERP.
        Registra el consumo en geco.ai.log.

        Si se pasa 'tools' (lista de dicts con name/description/inputSchema, formato
        MCP tal como lo devuelve geco_mcp.tool.get_tools()), el modelo puede optar por
        invocar una herramienta en lugar de responder directamente. En ese caso el
        método retorna un dict {'text': str|None, 'tool_calls': list|None} en vez del
        string plano habitual, para no romper a los llamadores existentes que no
        pasan 'tools'.
        """
        provider = self.env['ir.config_parameter'].sudo().get_param('geco_ai.provider', 'openai')
        result_text = ""
        tokens_prompt = 0
        tokens_comp = 0
        model_used = ""
        tool_calls = None

        if provider == 'openai':
            api_key = self.env['ir.config_parameter'].sudo().get_param('geco_ai.openai_api_key')
            if not api_key:
                raise UserError(_("OpenAI API Key is missing. Configure it in GECO AI Engine settings."))

            client = openai.OpenAI(api_key=api_key)
            model_used = "gpt-4o-mini"
            current_max_tokens = max_tokens
            try:
                for attempt in range(2):
                    request_kwargs = {
                        'model': model_used,
                        'messages': [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        'max_tokens': current_max_tokens,
                    }
                    if tools:
                        request_kwargs['tools'] = self._build_openai_tools(tools)
                    response = client.chat.completions.create(**request_kwargs)
                    message = response.choices[0].message
                    if hasattr(response, 'usage') and response.usage:
                        tokens_prompt += response.usage.prompt_tokens
                        tokens_comp += response.usage.completion_tokens
                    if tools and message.tool_calls:
                        tool_calls = [
                            {
                                'name': tc.function.name,
                                'arguments': json.loads(tc.function.arguments or '{}'),
                            }
                            for tc in message.tool_calls
                        ]
                        result_text = json.dumps({'tool_calls': tool_calls}, default=str)
                        break
                    result_text = message.content or ""
                    truncated = response.choices[0].finish_reason == 'length'
                    if truncated and attempt == 0 and current_max_tokens < MAX_TOKENS_RETRY_CAP:
                        current_max_tokens = min(current_max_tokens * 2, MAX_TOKENS_RETRY_CAP)
                        continue
                    break
            except Exception as e:
                raise UserError(_("OpenAI Connection Error: %s") % str(e))

        elif provider == 'gemini':
            try:
                from google import genai
                from google.genai import types as genai_types
            except ImportError:
                raise UserError(_("The 'google-genai' Python package is not installed. Please install it to use Gemini: pip install google-genai"))

            api_key = self.env['ir.config_parameter'].sudo().get_param('geco_ai.gemini_api_key')
            if not api_key:
                raise UserError(_("Gemini API Key is missing. Configure it in GECO AI Engine settings."))

            client = genai.Client(api_key=api_key)
            model_used = 'gemini-2.5-flash'
            current_max_tokens = max_tokens
            try:
                for attempt in range(2):
                    config_kwargs = {
                        'system_instruction': system_prompt,
                        'max_output_tokens': current_max_tokens,
                    }
                    if tools:
                        config_kwargs['tools'] = self._build_gemini_tools(tools)
                    response = client.models.generate_content(
                        model=model_used,
                        contents=user_prompt,
                        config=genai_types.GenerateContentConfig(**config_kwargs)
                    )
                    candidate = response.candidates[0] if response.candidates else None
                    parts = candidate.content.parts if candidate and candidate.content else []
                    found_calls = []
                    text_chunks = []
                    for part in (parts or []):
                        function_call = getattr(part, 'function_call', None)
                        if function_call:
                            raw_args = getattr(function_call, 'args', None)
                            if isinstance(raw_args, dict):
                                arguments = raw_args
                            elif raw_args:
                                try:
                                    arguments = dict(raw_args)
                                except Exception:
                                    arguments = {}
                            else:
                                arguments = {}
                            found_calls.append({'name': function_call.name, 'arguments': arguments})
                        elif getattr(part, 'text', None):
                            text_chunks.append(part.text)
                    if hasattr(response, 'usage_metadata') and response.usage_metadata:
                        tokens_prompt += getattr(response.usage_metadata, 'prompt_token_count', 0) or 0
                        tokens_comp += getattr(response.usage_metadata, 'candidates_token_count', 0) or 0
                    if tools and found_calls:
                        tool_calls = found_calls
                        result_text = json.dumps({'tool_calls': tool_calls}, default=str)
                        break
                    result_text = "".join(text_chunks) or (response.text or "")
                    truncated = (
                        candidate is not None
                        and candidate.finish_reason == genai_types.FinishReason.MAX_TOKENS
                    )
                    if truncated and attempt == 0 and current_max_tokens < MAX_TOKENS_RETRY_CAP:
                        current_max_tokens = min(current_max_tokens * 2, MAX_TOKENS_RETRY_CAP)
                        continue
                    break
            except Exception as e:
                raise UserError(_("Gemini Connection Error: %s") % str(e))

        # Calcular el costo en USD basado en 1 Millón de tokens
        cost_input_1m = float(self.env['ir.config_parameter'].sudo().get_param('geco_ai.cost_input_1m', 5.0))
        cost_output_1m = float(self.env['ir.config_parameter'].sudo().get_param('geco_ai.cost_output_1m', 15.0))

        cost_usd = (tokens_prompt * cost_input_1m / 1000000.0) + (tokens_comp * cost_output_1m / 1000000.0)

        # Registrar el Log de Consumo
        self.env['geco.ai.log'].sudo().create({
            'module_caller': module_caller,
            'provider': provider,
            'model_used': model_used,
            'prompt': f"SYSTEM:\\n{system_prompt}\\n\\nUSER:\\n{user_prompt}",
            'response': result_text,
            'tokens_prompt': tokens_prompt,
            'tokens_completion': tokens_comp,
            'tokens_total': tokens_prompt + tokens_comp,
            'cost_estimate': cost_usd,
        })

        # Comprobar límite de tokens y enviar alerta
        token_limit = int(self.env['ir.config_parameter'].sudo().get_param('geco_ai.token_limit', 0))
        alert_email = self.env['ir.config_parameter'].sudo().get_param('geco_ai.alert_email', '')

        if token_limit > 0 and alert_email:
            # Calcular el consumo mensual actual (desde el inicio del mes)
            import datetime
            first_day = datetime.date.today().replace(day=1)
            total_consumed = sum(self.env['geco.ai.log'].sudo().search([
                ('create_date', '>=', first_day)
            ]).mapped('tokens_total'))

            # Si supera el 90%
            if total_consumed >= (token_limit * 0.90):
                # Usar una bandera para no enviar correos en cada request,
                # solo si no se ha enviado hoy. (Para no hacer spam,
                # comprobamos si ya hay un correo enviado hoy)
                today_str = str(datetime.date.today())
                last_alert = self.env['ir.config_parameter'].sudo().get_param('geco_ai.last_alert_date', '')
                if last_alert != today_str:
                    template = self.env.ref('geco_ai_core.email_template_geco_ai_token_alert', raise_if_not_found=False)
                    if template:
                        usage_percent = round((total_consumed / token_limit) * 100, 2)
                        ctx = {
                            'alert_email': alert_email,
                            'token_limit': f"{token_limit:,}",
                            'current_tokens': f"{total_consumed:,}",
                            'usage_percent': usage_percent,
                        }
                        template.with_context(ctx).send_mail(self.env.user.id, force_send=True)
                        self.env['ir.config_parameter'].sudo().set_param('geco_ai.last_alert_date', today_str)

        if tools:
            return {'text': None if tool_calls else result_text, 'tool_calls': tool_calls}
        return result_text
