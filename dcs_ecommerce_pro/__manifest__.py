# Copyright 2026 DevsCodeSpace
# License OPL-1 (https://www.odoo.com/documentation/18.0/legal/licenses.html)
{
    'name': 'DCS Commerce Pro - Storefront Core',
    'summary': 'Storefront building blocks shared by the DCS Commerce Pro theme',
    'description': """
Shared storefront code for the DCS Commerce Pro theme: header action hooks,
storefront styling scoped to websites that use the theme, and (in later
releases) product sources, badges and quick view.
""",
    'version': '18.0.1.0.0',
    'category': 'Website/Website',
    'author': 'DevsCodeSpace',
    'maintainer': 'DevsCodeSpace',
    'website': 'https://devscodespace.com',
    'license': 'OPL-1',
    'depends': ['website_sale'],
    'data': [
        'views/header_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'dcs_ecommerce_pro/static/src/scss/storefront.scss',
        ],
        'web.assets_tests': [
            'dcs_ecommerce_pro/static/tests/tours/**/*',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
}
