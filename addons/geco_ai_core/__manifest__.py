# -*- coding: utf-8 -*-
{
    'name': 'GECO AI Core Engine',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Centralized Artificial Intelligence Engine for GECOERP',
    'description': """
GECO AI Core Engine
===================
The master brain of GECOERP. Handles secure API key storage, routes all AI requests to OpenAI/Gemini, and audits token consumption across all modules.
    """,
    'author': 'GECO',
    'depends': ['base', 'mail', 'web', 'base_setup'],
    'external_dependencies': {
        'python': ['openai', 'pandas', 'numpy', 'scikit-learn'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'data/mail_template_data.xml',
        'views/geco_ai_log_views.xml',
        'views/geco_ai_test_wizard_views.xml',
        'views/res_config_settings_views.xml',
        'views/geco_ai_menus.xml',
        'views/geco_ai_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'geco_ai_core/static/src/xml/dashboard_template.xml',
            'geco_ai_core/static/src/js/geco_ai_dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
