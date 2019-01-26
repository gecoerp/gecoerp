# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

from gecoerp import fields, models


class Website(models.Model):

    _inherit = "website"

    channel_id = fields.Many2one('im_livechat.channel', string='Website Live Chat Channel')
