# -*- coding: utf-8 -*-
{
    'name': 'GECOERP Modern UI Theme Core',
    'version': '18.0.1.0.0',
    'category': 'Themes/Backend',
    'summary': 'Executive, modern Slate & Glass navbar, sidebar drawer and UI redesign for GECOERP',
    'description': """
GECOERP Modern UI Theme Core
============================
Transforms the standard Odoo navbar and interface into a high-end SaaS Enterprise experience:
* Lateral Drawer / Sidebar Menu with live fuzzy search and fast app navigation.
* Executive Slate & Deep Navy navigation bar with smooth gradients and glass effects.
* Official GECOERP logo badge and hamburger quick-launcher.
* Modern pill-style menu navigation with subtle hover animations.
* Polished dropdowns, rounded cards, and elevated dashboard aesthetics.
    """,
    'author': 'GECOERP',
    'website': 'https://www.gecoerp.com',
    'license': 'LGPL-3',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'geco_ui_theme_core/static/src/scss/navbar.scss',
            'geco_ui_theme_core/static/src/scss/sidebar.scss',
            'geco_ui_theme_core/static/src/scss/theme.scss',
            'geco_ui_theme_core/static/src/xml/navbar.xml',
            'geco_ui_theme_core/static/src/xml/sidebar.xml',
            'geco_ui_theme_core/static/src/js/sidebar_menus.js',
            'geco_ui_theme_core/static/src/js/search_apps.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
}
