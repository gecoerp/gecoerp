# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

from gecoerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    team_id = fields.Many2one(
        'crm.team', 'Sales Channel',
        help='If set, this sales channel will be used for sales and assignations related to this partner')
