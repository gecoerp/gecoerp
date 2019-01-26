# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
GECOERP Web core module.
========================

This module provides the core of the GECOERP Web Client.
        """,
    'depends': ['base'],
    'auto_install': True,
    'data': [
        'views/webclient_templates.xml',
        'views/report_templates.xml',
    ],
    'qweb': [
        "static/src/xml/base.xml",
        "static/src/xml/kanban.xml",
        "static/src/xml/rainbow_man.xml",
        "static/src/xml/report.xml",
        "static/src/xml/web_calendar.xml",
    ],
    'bootstrap': True,  # load translations for login screen
}
