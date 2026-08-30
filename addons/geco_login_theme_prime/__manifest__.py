# -*- coding: utf-8 -*-
{
    'name': 'GECO - Tema de Login Prime',
    'version': '18.0.1.0.0',
    'summary': 'Diseño moderno, split-screen y responsive para la pantalla de inicio de sesión',
    'description': """
Módulo de personalización estética para la pantalla de inicio de sesión (/web/login).
Transforma la interfaz predeterminada en un diseño Split-Screen con héroe corporativo, tarjeta elevadada (Glassmorphism), iconos en inputs y un estilo visual premium.
    """,
    'category': 'Customizations/UI',
    'author': 'GECO',
    'depends': ['web'],
    'data': [
        'views/login_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'geco_login_theme_prime/static/src/css/login_theme.css',
            'geco_login_theme_prime/static/src/js/login_theme.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
