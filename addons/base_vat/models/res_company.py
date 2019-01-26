# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

from gecoerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    vat_check_vies = fields.Boolean(string='Verify VAT Numbers')
