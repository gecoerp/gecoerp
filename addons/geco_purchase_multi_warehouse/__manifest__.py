# -*- coding: utf-8 -*-
{
    'name': 'Multi Warehouse in Purchase',
    'version': '18.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Multi Warehouse in Purchase lines with separate pickings',
    'description': """
Multi Warehouse in Purchase
===========================
Allows setting a different delivery warehouse/picking type on each purchase order line.
Upon order confirmation, separate stock pickings are generated per warehouse.
    """,
    'author': 'GECO (portado de INKERP)',
    'depends': ['purchase', 'purchase_stock'],
    'data': [
        'views/purchase_order_view.xml',
        'views/purchase_order_report.xml',
        'views/stock_picking_type.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
