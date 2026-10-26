# Copyright 2026 DevsCodeSpace
# License OPL-1
from odoo import models

HEADER_STOREFRONT = 'theme_dcs_ecommerce_pro.template_header_storefront'
FOOTER_STOREFRONT = 'theme_dcs_ecommerce_pro.template_footer_storefront'


class ThemeUtils(models.AbstractModel):
    _inherit = 'theme.utils'

    @property
    def _header_templates(self):
        return [HEADER_STOREFRONT] + super()._header_templates

    @property
    def _footer_templates(self):
        return [FOOTER_STOREFRONT] + super()._footer_templates

    def _theme_dcs_ecommerce_pro_post_copy(self, mod):
        self.enable_view(HEADER_STOREFRONT)
        self.enable_view(FOOTER_STOREFRONT)
        self.enable_view('website.option_footer_scrolltop')
