import contextlib
import inspect
import json
import logging
import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.safe_eval import json as safe_json
from odoo.tools import config
from odoo.http import request

from odoo.addons.geco_mcp.core.tool import _build_method_index, get_tool_index

from odoo.addons.geco_mcp.tools.encoder import encode_request, encode_response, RecordEncoder
from odoo.addons.geco_mcp.tools.exception import MCPScopeDenied
from odoo.addons.geco_mcp.tools.logger import LoggerProxy
from odoo.addons.geco_mcp.tools.protocol import ToolContent

_logger = logging.getLogger(__name__)


class MCPTool(models.Model):

    _name = 'geco_mcp.tool'
    _description = "MCP Tool"
    _order = 'sequence, name'

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    is_auto_synced = fields.Boolean(
        string="Auto-sincronizada",
        default=False,
        readonly=True,
        index=True,
        help="Generada automáticamente a partir de un método Python decorado con "
             "@mcp_tool — se actualiza sola en cada arranque/actualización de módulos. "
             "Para cambiar su comportamiento, edita el código fuente, no este registro.",
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    category = fields.Selection(
        selection=[
            ('read', "Read"),
            ('write', "Write"),
        ],
        string="Category",
        required=True,
        default='read',
    )

    registry = fields.Selection(
        selection=[
            ('mcp', "MCP"),
        ],
        string="Registry",
        help="Restrict the tool to a single surface.",
    )

    description = fields.Text(
        string="Description",
        required=True,
    )

    input_schema = fields.Text(
        string="Input Schema",
        help="JSON Schema defining the tool parameters.",
    )

    code = fields.Text(
        string="Python Code",
        required=True,
        default=(
            "# Available variables:\n"
            "#   env         - Odoo Environment (with caller context applied)\n"
            "#   arguments   - dict of tool arguments from the AI client\n"
            "#   json        - json module\n"
            "#   UserError   - odoo.exceptions.UserError\n"
            "#   logger      - logging.Logger for this tool\n"
            "#\n"
            "# Set 'result' to a JSON-serializable value to return it.\n"
            "result = {}\n"
        ),
    )

    # ----------------------------------------------------------
    # Helper
    # ----------------------------------------------------------

    @api.model
    def _serialize_result(self, result):
        if isinstance(result, ToolContent):
            return result
        if not isinstance(result, str):
            return json.dumps(
                result, indent=2, cls=RecordEncoder
            )
        return result

    @api.model
    def _check_scope(self, category, enforce_scope):
        if enforce_scope == 'read' and category != 'read':
            raise MCPScopeDenied(_('Access denied: key scope is read-only'))

    @api.model
    def _call(self, name, arguments, env, enforce_scope=None):
        status, text, info, error = 'ok', None, {}, None
        arguments = dict(arguments or {})
        model_name = arguments.get('model')
        start = time.monotonic()
        try:
            text, info, model_name = self._execute(
                name, arguments, env, enforce_scope,
            )
            return text, info
        except Exception as exc:
            status = (
                'denied'
                if isinstance(exc, MCPScopeDenied)
                else 'error'
            )
            error = str(exc)
            raise
        finally:
            if config.get('mcp_logging', True):
                self.env['geco_mcp.log'].log(**self._tool_log_values(
                    name=name,
                    env=env,
                    request_data=encode_request(arguments),
                    model_name=model_name,
                    status=status,
                    text=text,
                    info=info,
                    error=error,
                    duration_ms=int((time.monotonic() - start) * 1000),
                ))

    @api.model
    def _execute(self, name, arguments, env, enforce_scope):
        if not (entry := get_tool_index(env).get(name)):
            raise UserError(_("Tool not found: %s", name))
        self._check_scope(entry['category'], enforce_scope)
        if isinstance(context_override := arguments.pop('context', None), dict):
            env = env(context={**env.context, **context_override})
        # Mismo try/except para 'db' y 'method' — antes solo 'method' convertía un
        # TypeError de argumentos inválidos en un UserError legible; 'db' lo dejaba
        # propagar crudo. Importa especialmente ahora que varias tools Python reales
        # (whoami, search_read, create_records, ...) se auto-sincronizan como shims
        # 'db' — deben comportarse idéntico a como lo hacían siendo 'method'.
        try:
            if entry['kind'] == 'db':
                raw_result, text = self.sudo().browse(entry['id'])._run(arguments, env)
            else:
                func = inspect.unwrap(
                    getattr(type(env[entry['model']]), entry['method'])
                )
                raw_result = func(env[entry['model']], **arguments)
                text = self._serialize_result(raw_result)
        except TypeError as exc:
            raise UserError(_(
                "Invalid arguments for tool %(name)s: %(error)s",
                name=name, error=exc,
            ))
        except ValueError as exc:
            # safe_eval envuelve CUALQUIER excepción del código ejecutado en un
            # ValueError propio (gecoerp/tools/safe_eval.py:412-413), con el tipo
            # original embebido en el texto — así que un TypeError real (típicamente
            # argumentos inválidos en un shim de tool auto-sincronizada) nunca llega
            # como TypeError al catch de arriba en el camino 'db'. Se homologa SOLO
            # ese caso específico (por el prefijo exacto que safe_eval genera) al
            # mismo UserError legible que ya recibe 'method'; cualquier otro
            # ValueError genuino de una tool de BD personalizada se deja propagar
            # tal cual, sin reinterpretar su significado real.
            if entry['kind'] == 'db' and str(exc).startswith("<class 'TypeError'>"):
                raise UserError(_(
                    "Invalid arguments for tool %(name)s: %(error)s",
                    name=name, error=exc,
                ))
            raise
        return (
            text,
            self._extract_record_info(arguments, raw_result),
            arguments.get('model') or entry.get('model')
        )

    @api.model
    def _tool_log_values(
        self,
        *,
        name,
        env,
        request_data,
        model_name,
        status,
        text,
        info,
        error,
        duration_ms,
    ):
        values = {
            'method': 'tools/call',
            'tool_name': name,
            'user_id': env.uid,
            'model_name': model_name,
            'status': status,
            'duration_ms': duration_ms,
            'request_data': request_data,
        }
        if status == 'ok':
            values['response_data'] = encode_response(text)
            values['res_id'] = info.get('res_id')
            values['res_ids'] = info.get('res_ids')
        else:
            values['error_message'] = error
            values['response_data'] = error
        with contextlib.suppress(Exception):
            if key := getattr(request, '_mcp_key', None):
                values['key_id'] = key.id
            values['ip_address'] = (
                request.httprequest.remote_addr
                if request else None
            )
        return values

    @api.model
    def _extract_record_info(self, arguments, result):
        info = {}
        ids = arguments.get('ids')
        if isinstance(ids, int):
            ids = [ids]
        single_id = arguments.get('id')
        if isinstance(single_id, int):
            ids = [single_id]
        if ids:
            info['res_ids'] = list(ids)
            if len(info['res_ids']) == 1:
                info['res_id'] = info['res_ids'][0]
            return info
        if isinstance(result, dict) and isinstance(result.get('id'), int):
            info['res_id'] = result['id']
            info['res_ids'] = [result['id']]
        return info

    def _get_input_schema(self):
        return json.loads(self.input_schema) if self.input_schema else {
            'type': 'object',
            'properties': {},
        }

    def _get_eval_context(self, arguments, env):
        context = arguments.pop('context', None)
        if context and isinstance(context, dict):
            env = env(context={**env.context, **context})
        return {
            'env': env,
            'arguments': arguments,
            'json': safe_json,
            'callable': callable,
            'getattr': getattr,
            'hasattr': hasattr,
            'UserError': UserError,
            'logger': LoggerProxy(f'{__name__} ({self.name})'),
        }

    def _notify_tools_changed(self):
        with contextlib.suppress(Exception):
            self.env['geco_mcp.notification'].push_to_all_sessions(
                'notifications/tools/list_changed',
            )

    def _run(self, arguments, env):
        eval_context = self._get_eval_context(arguments, env)
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)
        raw_result = eval_context.get('result')
        return raw_result, self._serialize_result(raw_result)

    # ----------------------------------------------------------
    # Functions
    # ----------------------------------------------------------

    @api.model
    def get_tools(self, registry=None):
        return [
            {
                'name': name,
                'description': entry['description'],
                'inputSchema': entry['input_schema'],
            }
            for name, entry in get_tool_index(self.env, registry=registry).items()
        ]

    @api.model
    def get_playground_tools(self):
        return [
            {
                'name': name,
                'description': entry['description'],
                'inputSchema': entry['input_schema'],
                'category': entry['category'],
                'kind': entry['kind'],
                'registry': entry.get('registry') or None,
                'is_auto_synced': entry.get('is_auto_synced', False),
            }
            for name, entry in get_tool_index(self.env).items()
        ]

    # ----------------------------------------------------------
    # Auto-sync from @mcp_tool decorated methods
    # ----------------------------------------------------------

    def _register_hook(self):
        try:
            self._sync_auto_tools()
        except Exception:
            _logger.exception("geco_mcp: fallo sincronizando tools automáticas")
        return super()._register_hook()

    def _sync_auto_tools(self):
        """Refleja en geco_mcp.tool cada método Python decorado con @mcp_tool, para
        que la pantalla admin muestre el catálogo real sin intervención manual.
        Corre en cada carga completa del registry (install/upgrade/restart) — debe
        ser rápido e idempotente."""
        Tool = self.env['geco_mcp.tool'].sudo()
        method_index = _build_method_index(self.env)
        existing_by_name = {
            r.name: r for r in Tool.with_context(active_test=False).search([])
        }
        seen_names = set()

        for name, meta in method_index.items():
            seen_names.add(name)
            current = existing_by_name.get(name)

            if current and not current.is_auto_synced:
                # Fila manual con el mismo nombre: shadow intencional de un admin —
                # no crear un duplicado, solo dejar constancia en el log.
                _logger.warning(
                    "geco_mcp: '%s' tiene una fila manual en geco_mcp.tool que "
                    "shadowea la tool Python homónima — se respeta, no se sincroniza.",
                    name,
                )
                continue

            vals = {
                'name': name,
                'description': meta['description'],
                'input_schema': json.dumps(meta['input_schema']),
                'category': meta['category'],
                'registry': meta['registry'],
                # Shim de passthrough: ejecuta exactamente el mismo método real que
                # ya llamaría el dispatcher si esta fila no existiera — nunca una
                # reimplementación, para no poder desincronizarse del código fuente.
                # meta['method'] ya es el nombre real del atributo Python (ej.
                # '_mcp_whoami') — NO anteponer otro guion bajo aquí.
                'code': "result = env['%s'].%s(**arguments)\n" % (
                    meta['model'], meta['method'],
                ),
                'is_auto_synced': True,
            }
            if current:
                # Solo escribir si algo realmente cambió — evita spamear
                # notifications/tools/list_changed a cada sesión MCP conectada en
                # cada arranque de servidor cuando nada se modificó.
                diff = {k: v for k, v in vals.items() if current[k] != v}
                if diff:
                    current.write(diff)
                if not current.active:
                    current.write({'active': True})
            else:
                Tool.create({**vals, 'active': True})

        # Tools auto-sincronizadas cuyo método ya no existe (módulo desinstalado,
        # método renombrado/eliminado) — se desactivan, nunca se borran, para no
        # perder el historial de geco_mcp.log que las referencia.
        stale = Tool.search([
            ('is_auto_synced', '=', True),
            ('name', 'not in', list(seen_names)),
            ('active', '=', True),
        ])
        if stale:
            stale.write({'active': False})

    # ----------------------------------------------------------
    # Constraints
    # ----------------------------------------------------------

    @api.constrains('code')
    def _check_code(self):
        for record in self.sudo().filtered('code'):
            message = test_python_expr(
                expr=record.code.strip(), mode="exec",
            )
            if message:
                raise ValidationError(message)

    @api.constrains('input_schema')
    def _check_input_schema(self):
        for record in self.sudo().filtered('input_schema'):
            try:
                json.loads(record.input_schema)
            except (TypeError, ValueError) as exc:
                raise ValidationError(_(
                    "Tool %(name)s has invalid Input Schema JSON: %(error)s",
                    name=record.name, error=exc,
                ))

    # ----------------------------------------------------------
    # ORM
    # ----------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._notify_tools_changed()
        return records

    def write(self, vals):
        result = super().write(vals)
        self._notify_tools_changed()
        return result

    def unlink(self):
        result = super().unlink()
        self._notify_tools_changed()
        return result
