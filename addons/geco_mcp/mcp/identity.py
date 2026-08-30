from odoo import api, models

from odoo.addons.geco_mcp.core.tool import mcp_tool
from odoo.addons.geco_mcp.tools.descriptions import model_field


class MCPMixin(models.AbstractModel):

    _inherit = 'geco_mcp.mixin'

    # ----------------------------------------------------------
    # Functions
    # ----------------------------------------------------------

    @api.model
    @mcp_tool(
        name='whoami',
        description=(
            'Get information about the current authenticated user: their '
            'name, login, language, timezone, active company, currency, '
            'country, security groups, and their own contact phone/mobile '
            '(partner_id, phone, mobile — may be empty if not set on their '
            'contact record). Also returns the full list of companies the '
            'user can access and the currently allowed company ids. Use '
            "this at the start of a conversation to understand who you are "
            "acting as, what permissions you have, and what company "
            "context you are in. ALSO use this whenever the user asks to "
            "send/share something with themselves ('a mí', 'envíamelo', "
            "'mándamelo') — it is the ONLY correct source for the current "
            "user's own phone number. Never invent, guess, or use a "
            "placeholder phone number for any purpose; if 'phone' and "
            "'mobile' both come back empty, tell the user their contact "
            "record has no phone number instead of making one up. To "
            "target a specific company on a subsequent tool call, pass "
            "context={'allowed_company_ids': [id]} in the tool arguments."
        ),
        input_schema={
            'type': 'object',
            'properties': {},
        },
        category='read',
    )
    def _mcp_whoami(self):
        user = self.env.user
        company = self.env.company
        partner = user.partner_id
        return {
            'uid': user.id,
            'login': user.login,
            'name': user.name,
            'lang': user.lang,
            'tz': user.tz or '',
            'partner_id': partner.id,
            'phone': partner.phone or '',
            'mobile': partner.mobile or '',
            'company_id': company.id,
            'company_name': company.name,
            'currency': company.currency_id.name,
            'country': company.country_id.name or '',
            'companies': [
                {
                    'id': c.id,
                    'name': c.name,
                    'currency': c.currency_id.name,
                    'country': c.country_id.name or '',
                }
                for c in user.company_ids.sorted('sequence')
            ],
            'groups': [
                g.full_name for g in user.groups_id.sorted('full_name')
            ],
        }

    @api.model
    @mcp_tool(
        name='get_access_rights',
        description=(
            "Check the current user's access rights on a model (read, "
            "write, create, unlink) and list all access control rules "
            "defined for it. Use this to understand why an operation "
            "might be forbidden or to verify permissions before "
            "attempting a write operation."
        ),
        input_schema={
            'type': 'object',
            'properties': {
                'model': model_field(),
            },
            'required': ['model'],
        },
        category='read',
    )
    def _mcp_get_access_rights(self, model):
        target = self._resolve_model(model)
        rights = {}
        for op in ('read', 'write', 'create', 'unlink'):
            try:
                target.check_access_rights(op, raise_exception=True)
                rights[op] = True
            except Exception:
                rights[op] = False
        rules = self.env['ir.model.access'].sudo().search_read(
            [('model_id.model', '=', model)],
            fields=[
                'name', 'group_id', 'perm_read', 'perm_write',
                'perm_create', 'perm_unlink',
            ],
        )
        return {
            'model': model,
            'current_user_rights': rights,
            'access_rules': rules,
        }
