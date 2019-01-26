# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

from gecoerp import api, fields, models
from gecoerp.exceptions import UserError
from gecoerp.addons.iap.models import iap

DEFAULT_ENDPOINT = 'https://iap-sms.gecoerp.com'


class SmsApi(models.AbstractModel):
    _name = 'sms.api'

    @api.model
    def _send_sms(self, numbers, message):
        """ Send sms
        """
        account = self.env['iap.account'].get('sms')
        params = {
            'account_token': account.account_token,
            'numbers': numbers,
            'message': message,
        }
        endpoint = self.env['ir.config_parameter'].sudo().get_param('sms.endpoint', DEFAULT_ENDPOINT)
        r = iap.jsonrpc(endpoint + '/iap/message_send', params=params)
        return True
