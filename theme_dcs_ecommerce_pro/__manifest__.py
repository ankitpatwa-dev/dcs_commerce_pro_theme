# Copyright 2026 DevsCodeSpace
# License OPL-1 (https://www.odoo.com/documentation/18.0/legal/licenses.html)
{
    'name': 'DCS Commerce Pro',
    'summary': 'Storefront eCommerce theme with live product search',
    'description': """
DCS Commerce Pro is a premium eCommerce theme for Odoo 18 by DevsCodeSpace.
It restyles the storefront and adds blocks built on Odoo's own website builder,
product data, pricing and cart.
""",
    'version': '18.0.1.0.0',
    'category': 'Theme/eCommerce',
    'author': 'DevsCodeSpace',
    'maintainer': 'DevsCodeSpace',
    'website': 'https://devscodespace.com',
    'license': 'OPL-1',
    'depends': ['website_sale', 'dcs_ecommerce_pro'],
    'data': [
        'data/ir_asset.xml',
        'views/layout.xml',
        'views/header.xml',
        'views/footer.xml',
        'views/snippets/s_dcs_hero_shelf.xml',
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'theme_dcs_ecommerce_pro/static/src/scss/fonts.scss',
            'theme_dcs_ecommerce_pro/static/src/scss/theme.scss',
        ],
        # Font previews in the editor's Theme tab
        'website.assets_wysiwyg': [
            'theme_dcs_ecommerce_pro/static/src/scss/fonts.scss',
        ],
    },
    'images': [
        'static/description/cover.png',
        'static/description/theme_dcs_ecommerce_pro_screenshot.jpg',
    ],
    'installable': True,
    'application': False,
}
