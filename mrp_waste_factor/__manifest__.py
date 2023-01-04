# -*- coding: utf-8 -*-
{
    'name': 'Waste Factor',
    'version': '15.0.1.0',
    'summary': 'Waste Factor',
    'sequence': 4,
    'description': """ Waste Factor """,
    'category': 'Manufacturing',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mrp',
        'account'
    ],
    'data': [
        'views/product_product.xml',
        'views/mrp_production.xml',
        'views/mrp_bom.xml',
        'views/account_move_line.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
