import unittest
from core.focused_ux import decorate_focused_ux,replace_admin_hub
from bs4 import BeautifulSoup

class FocusedUX(unittest.TestCase):
    def test_decorating_twice_keeps_one_script(self):
        html='<html><head>\n</head><body><main><a href="/ai-news/">ニュース</a></main></body></html>'
        decorated=decorate_focused_ux(html)
        self.assertEqual(decorated,decorate_focused_ux(decorated))
        soup=BeautifulSoup(decorated,'html.parser')
        self.assertEqual(len(soup.select('#focused-ux-script')),1)
        self.assertEqual(soup.a['href'],'/ai-news/')
    def test_only_home_metrics_are_removed(self):
        html='<head></head><aside class="hero-advantage">比較</aside><aside>連絡</aside><form action="/api/contact"><input name="name"></form>'
        self.assertIn('hero-advantage',decorate_focused_ux(html))
        result=decorate_focused_ux(html,home=True)
        self.assertNotIn('hero-advantage',result)
        self.assertIn('<aside>連絡</aside>',result)
        self.assertIn('<form action="/api/contact"><input name="name"></form>',result)
    def test_admin_keeps_header_and_logout_with_non_js_links(self):
        html='<head></head><body><header><a href="/admin/blog">記事</a></header><main>旧画面</main><script src="/admin/admin-menu.js"></script></body>'
        result=replace_admin_hub(html);soup=BeautifulSoup(result,'html.parser')
        self.assertEqual(result,replace_admin_hub(result))
        self.assertEqual(soup.header.a['href'],'/admin/blog')
        self.assertEqual(len(soup.select('.ux-task-card')),10)
        self.assertTrue(all(a.get('href','').startswith('/') for a in soup.select('.ux-task-card')))
        self.assertIsNotNone(soup.select_one('[href="/admin/logout"]'))
        self.assertTrue(soup.select_one('.ux-task-controls').has_attr('hidden'))
        self.assertIsNotNone(soup.select_one('script[src="/admin/admin-menu.js"]'))
    def test_missing_admin_main_fails_closed(self):
        with self.assertRaises(AssertionError):replace_admin_hub('<head></head><body>unexpected</body>')
if __name__=='__main__':unittest.main()
