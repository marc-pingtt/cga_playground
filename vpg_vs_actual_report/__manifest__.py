# -*- coding: utf-8 -*-
{
    'name': 'VPG vs Actual Sales Report',
    'version': '15.0.1.0',
    'summary': 'VPG vs Actual Sales Report',
    'sequence': 4,
    'description': """ VPG vs Actual Sales Report """,
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/reporting_menuitem.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/approval_product_line.xml',
        'report/vpg_sale_report.xml'
    ],
    'assets': {
        'web.assets_backend': ['vpg_vs_actual_report/static/src/js/vpg_sales.js'],
        'web.assets_qweb': [
            'vpg_vs_actual_report/static/src/xml/report_view.xml',
        ],

    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
