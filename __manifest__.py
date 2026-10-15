# -*- coding: utf-8 -*-

{
    'name': 'Coffee Shop Cashier & Stock Alert',
    'version': '1.0',
    'category': 'Sales/Point of Sale',

    'summary': (
        'Custom POS and Stock Management for Coffee Shops '
        'with Email Alerts'
    ),

    'description': """
        This module extends Odoo Point of Sale and Stock/Inventory
        for Coffee Shops.

        Key Features:
        - Manage product stock threshold levels for coffee shop ingredients.
        - Send email notifications automatically when stock drops below threshold.
        - Detailed sales report exported to Excel.
        - Detailed stock status report exported to Excel.
        - Integrated Coffee Shop Dashboard with key metrics.
        - Custom QRIS payment screen.
    """,

    'author': 'Handoko Bimawidjaya',

    'depends': [
        'point_of_sale',
        'stock',
        'mail',
    ],

    'data': [
        'security/ir.model.access.csv',

        'data/coffee_shop_data.xml',
        'data/mail_template_data.xml',
        'report/pos_order_receipt.xml',
        'report/pos_session_sales_details.xml',

        'views/product_template_views.xml',
        'views/pos_order_customer_name_views.xml',
        'views/res_config_settings_views.xml',
        'views/coffee_shop_menus.xml',

        'wizard/coffee_shop_sales_report_wizard_views.xml',
        'wizard/coffee_shop_stock_report_wizard_views.xml',
    ],

    'external_dependencies': {
        'python': [
            'openpyxl',
        ],
    },

    'assets': {
        'point_of_sale._assets_pos': [
        'coffee_shop_cashier/static/src/js/qris_payment_screen.js',
        'coffee_shop_cashier/static/src/js/product_card_quantity.js',
        'coffee_shop_cashier/static/src/js/receipt_customer_name.js',
        'coffee_shop_cashier/static/src/js/customer_name_pos.js',
        'coffee_shop_cashier/static/src/js/closing_cash_out.js',
        'coffee_shop_cashier/static/src/js/cash_payment_recommendations.js',
        'coffee_shop_cashier/static/src/xml/qris_payment_screen.xml',
        'coffee_shop_cashier/static/src/xml/product_card_quantity.xml',
        'coffee_shop_cashier/static/src/xml/receipt_customer_name.xml',
        'coffee_shop_cashier/static/src/xml/customer_name_pos.xml',
        'coffee_shop_cashier/static/src/xml/closing_cash_out.xml',
        'coffee_shop_cashier/static/src/xml/cash_payment_recommendations.xml',
        'coffee_shop_cashier/static/src/xml/ticket_screen_columns.xml',
        'coffee_shop_cashier/static/src/css/qris_payment_screen.css',
        'coffee_shop_cashier/static/src/css/cash_payment_recommendations.css',
        'coffee_shop_cashier/static/src/css/product_card_quantity.css',
        'coffee_shop_cashier/static/src/css/ticket_screen_columns.css',
        'coffee_shop_cashier/static/src/css/thermal_receipt.css',
        ],
    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
