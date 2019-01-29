# -*- coding: utf-8 -*-
# Part of Odoo, GECOERP. See LICENSE file for full copyright and licensing details.
{
    'name': 'Website Google Map',
    'category': 'Website',
    'summary': '',
    'version': '1.0',
    'description': """
GECOERP Website Google Map
==========================

        """,
    'depends': ['base_geolocalize', 'website_partner'],
    'data': [
        'views/google_map_templates.xml',
    ],
    'installable': True,
}
