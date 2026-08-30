{
    "name": "Sale Order Type",
    "version": "18.0.1.0.0",
    "author": "GECO ERP",
    "license": "AGPL-3",
    "category": "Sales/Sales",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/sale_order_type_data.xml",
        "views/view_sale_order_type.xml",
        "views/view_sale_order.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
