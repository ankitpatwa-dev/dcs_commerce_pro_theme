# Copyright 2026 DevsCodeSpace
# License OPL-1
import re

from lxml import html

from odoo.tests import HttpCase, tagged
from odoo.tools import config

THEME = 'theme_dcs_ecommerce_pro'


def has_class(name):
    return f"contains(concat(' ', normalize-space(@class), ' '), ' {name} ')"


def q(doc, path):
    """XPath with a `.cls` shorthand: '//header//*[.o_x]' -> class test."""
    import re as _re
    path = _re.sub(r'\[\.([\w-]+)\]', lambda m: f'[{has_class(m.group(1))}]', path)
    return doc.xpath(path)
HEADER = f'{THEME}.template_header_storefront'
FOOTER = f'{THEME}.template_footer_storefront'


@tagged('post_install', '-at_install')
class TestDcsCommerceTheme(HttpCase):
    """Phase 2 foundation: theme application, per-website isolation, header,
    footer, presets, blocks (R1) and website values (R2)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.theme = cls.env.ref(f'base.module_{THEME}')
        cls.website = cls.env.ref('website.default_website')
        cls.other = cls.env['website'].create({
            'name': 'Other shop (no theme)',
            'domain': f"http://localhost:{config['http_port']}",
        })
        cls.website.theme_id = cls.theme
        cls.theme.with_context(apply_new_theme=True)._theme_load(cls.website)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _view(self, key, website):
        return self.env['ir.ui.view'].with_context(active_test=False).search([
            ('key', '=', key), ('website_id', '=', website.id),
        ])

    def _get_page(self, url='/', other=False):
        if other:
            url = f"http://localhost:{config['http_port']}{url}"
        res = self.url_open(url)
        self.assertEqual(res.status_code, 200, url)
        return res.text

    def _frontend_css(self, page_html):
        doc = html.fromstring(page_html)
        hrefs = [h for h in doc.xpath('//link[@rel="stylesheet"]/@href') if 'web.assets_frontend' in h]
        self.assertTrue(hrefs, "frontend bundle link found")
        css = ''
        for href in hrefs:
            res = self.url_open(href)
            self.assertEqual(res.status_code, 200, href)
            css += res.text
        return css

    # ------------------------------------------------------------------ #
    # Theme application and isolation
    # ------------------------------------------------------------------ #

    def test_views_are_website_specific(self):
        for key in (HEADER, FOOTER, f'{THEME}.layout_guard', f'{THEME}.snippets',
                    f'{THEME}.s_dcs_hero_shelf'):
            self.assertEqual(len(self._view(key, self.website)), 1, key)
            self.assertFalse(self._view(key, self.other), key)
        self.assertFalse(self.env['ir.ui.view'].with_context(active_test=False).search([
            ('key', '=like', f'{THEME}.%'), ('website_id', '=', False),
        ]), "no generic (all-website) theme views")

    def test_header_and_footer_selected(self):
        self.assertTrue(self._view(HEADER, self.website).active)
        self.assertTrue(self._view(FOOTER, self.website).active)
        default_header = self.env['website'].with_context(website_id=self.website.id).viewref(
            'website.template_header_default')
        self.assertFalse(default_header.active, "Odoo's default header is switched off on the theme website")

    def test_homepage_storefront(self):
        page = self._get_page('/')
        doc = html.fromstring(page)
        wrapwrap = doc.get_element_by_id('wrapwrap')
        self.assertIn('o_dcs_ecom', wrapwrap.get('class').split())
        # Header: announcement, brand, product search, account, cart, menu row
        self.assertTrue(q(doc, '//header//*[.o_dcs_announcement]'))
        search = q(doc, '//header//*[.o_dcs_header_search]//input[.search-query]')
        self.assertTrue(search)
        self.assertEqual(search[0].get('data-search-type'), 'products')
        self.assertEqual(q(doc, '//header//*[.o_dcs_header_search]//form')[0].get('action'), '/shop')
        self.assertTrue(q(doc, '//header//*[.o_dcs_header_actions]//*[.o_wsale_my_cart]'))
        self.assertTrue(q(doc, '//header//*[.o_dcs_header_actions]//a[starts-with(@href, "/web/login")]'))
        self.assertTrue(q(doc, '//header//*[.o_dcs_header_menu]//*[@id="top_menu"]'))
        # Mobile header still present (Odoo's own, with eCommerce's cart)
        self.assertTrue(q(doc, '//header//nav[.o_header_mobile]//*[.o_wsale_my_cart]'))
        # Footer
        self.assertTrue(q(doc, '//*[@id="footer"][.o_dcs_footer]//*[.o_dcs_footer_service]'))

    def test_other_website_untouched(self):
        page = self._get_page('/', other=True)
        doc = html.fromstring(page)
        self.assertNotIn('o_dcs_ecom', doc.get_element_by_id('wrapwrap').get('class') or '')
        self.assertFalse(q(doc, '//*[.o_dcs_header_bar] | //*[.o_dcs_footer]'))
        self.assertNotIn(f'/{THEME}/static/src', page)

    def test_footer_links_resolve(self):
        doc = html.fromstring(self._get_page('/'))
        hrefs = {a.get('href') for a in q(doc, '//*[@id="footer"][.o_dcs_footer]//a[starts-with(@href, "/")]')}
        self.assertTrue(hrefs)
        for href in sorted(hrefs):
            if href.startswith('/website/social/'):
                # Odoo redirects these to the network URLs set in Website
                # settings; unset networks are hidden by the social block.
                continue
            res = self.url_open(href)
            self.assertLess(res.status_code, 400, href)

    # ------------------------------------------------------------------ #
    # Presets and assets (R2, fonts)
    # ------------------------------------------------------------------ #

    def test_assets_and_presets(self):
        css = self._frontend_css(self._get_page('/'))
        compact = re.sub(r'\s+', '', css)
        # R2: website values reach the CSS the editor reads for the Theme tab
        self.assertIn("--header-template:'dcs-storefront'", compact)
        self.assertIn("--footer-template:'dcs-storefront'", compact)
        self.assertIn("--color-palettes-name:'dcs-shelf'", compact)
        # Palette 'dcs-shelf' primary
        self.assertRegex(compact.lower(), r'--o-color-1:#8a1c52')
        # Local fonts, no Google request
        self.assertIn(f'/{THEME}/static/src/fonts/dm-sans-latin.woff2', css)
        self.assertNotIn('fonts.googleapis.com', css)
        # Theme and core styles present
        self.assertIn('.o_dcs_header_bar', css)
        self.assertIn('.o_dcs_well', css)

    def test_other_website_assets(self):
        page = self._get_page('/', other=True)
        doc = html.fromstring(page)
        hrefs = [h for h in doc.xpath('//link[@rel="stylesheet"]/@href') if 'web.assets_frontend' in h]
        css = ''.join(self.url_open(f"http://localhost:{config['http_port']}{h}").text for h in hrefs)
        self.assertNotIn(f'/{THEME}/static/src/fonts', css)
        self.assertNotIn('.o_dcs_header_bar', css)
        self.assertNotIn("'dcs-storefront'", css)

    # ------------------------------------------------------------------ #
    # Blocks (R1)
    # ------------------------------------------------------------------ #

    def _render_panel(self, website):
        return self.make_jsonrpc_request('/web/dataset/call_kw/ir.ui.view/render_public_asset', {
            'model': 'ir.ui.view',
            'method': 'render_public_asset',
            'args': ['website.snippets', {}],
            'kwargs': {'context': {'website_id': website.id, 'lang': 'en_US'}},
        })

    def test_snippet_panel_scoped_to_theme_website(self):
        """R1: blocks registered by the theme appear only in the editor of
        websites that use the theme."""
        self.authenticate('admin', 'admin')
        panel = self._render_panel(self.website)
        self.assertIn('data-snippet="s_dcs_hero_shelf"', panel)
        self.assertIn('DCS Commerce', panel)
        other_panel = self._render_panel(self.other)
        self.assertNotIn('s_dcs_hero_shelf', other_panel)
        self.assertNotIn('DCS Commerce', other_panel)

    def test_hero_markup(self):
        out = str(self.env['ir.qweb'].with_context(website_id=self.website.id)._render(
            f'{THEME}.s_dcs_hero_shelf'))
        doc = html.fromstring(out)
        self.assertEqual(len(doc.xpath('//h1')), 1)
        for img in doc.xpath('//img'):
            self.assertTrue(img.get('alt'))
            self.assertTrue(img.get('width') and img.get('height'), "dimensions set (no layout shift)")
        section = doc.xpath('//section')[0]
        self.assertEqual(section.get('data-snippet'), 's_dcs_hero_shelf')

    def test_hero_editor_tour(self):
        self.start_tour(self.env['website'].get_client_action_url('/'), 'dcs_hero_block', login='admin')
        # The editor session forces website 1; check as a fresh visitor.
        self.logout()
        self.assertIn('s_dcs_hero_shelf', self._get_page('/'))
        self.assertNotIn('s_dcs_hero_shelf', self._get_page('/', other=True))
