# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

from gecoerp import models, api, _
from gecoerp.exceptions import UserError


class BankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def button_draft(self):
        self.state = 'open'


