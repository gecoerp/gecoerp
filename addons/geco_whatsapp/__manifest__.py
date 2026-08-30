# -*- coding: utf-8 -*-
{
    'name': 'GECO WhatsApp',
    'summary': 'Send and receive WhatsApp messages via a WhatsApp-Web.js microservice',
    'description': (
        'Integrates GECOERP with an external whatsapp-web.js microservice to send '
        'documents (invoices, quotations) and free-text messages over WhatsApp, and '
        'to log incoming/outgoing messages directly in each contact\'s own chatter '
        '(auto-creating the contact for unregistered numbers). Triggered manually '
        'from the document form, from the contact record, or via the GECO AI Copilot.'
    ),
    'author': 'Antigravity',
    'category': 'Productivity',
    'version': '18.0.1.0.0',
    'depends': ['geco_mcp', 'account', 'sale', 'purchase', 'mail', 'base_geolocalize'],
    'data': [
        'security/ir.model.access.csv',
        'security/geco_whatsapp_security.xml',
        'wizard/whatsapp_compose_views.xml',
        'views/res_partner_views.xml',
        'views/whatsapp_chat_views.xml',
        'views/whatsapp_account_views.xml',
        'views/whatsapp_log_views.xml',
        'views/whatsapp_gateway_log_views.xml',
        'views/whatsapp_ignore_views.xml',
        'views/whatsapp_template_views.xml',
        'data/whatsapp_template_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'geco_whatsapp/static/src/js/whatsapp_qr_dialog.js',
            'geco_whatsapp/static/src/xml/whatsapp_qr_dialog.xml',
            'geco_whatsapp/static/src/css/whatsapp_qr_dialog.css',
            'geco_whatsapp/static/src/js/whatsapp_phone_button.js',
            'geco_whatsapp/static/src/xml/whatsapp_phone_button.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
