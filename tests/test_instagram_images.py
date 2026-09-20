import unittest
from bs4 import BeautifulSoup
from core.instagram_feed import apply_instagram_feed, strip_instagram_feed, render_instagram_feed, HEAD
class InstagramImagesTest(unittest.TestCase):
    def test_only_six_linked_images(self):
        soup=BeautifulSoup(render_instagram_feed(),'html.parser')
        self.assertEqual(soup.get_text(strip=True),'')
        self.assertEqual(len(soup.select('a > img')),6)
        self.assertFalse(soup.select('iframe,button,h2,h3,p'))
        self.assertEqual(len({i['src'] for i in soup.select('img')}),6)
        for a in soup.select('a'):
            self.assertTrue(a['href'].startswith('https://www.instagram.com/p/'))
            self.assertIn('noopener',a['rel'])
    def test_replace_legacy_without_touching_other_content(self):
        original='<html><head><link id="instagram-feed-css" rel="stylesheet" href="/instagram-feed.css?v=20260919"><script id="instagram-feed-js" defer src="/instagram-feed.js?v=20260919"></script></head><body><header>keep</header><!-- BEGIN:INSTAGRAM_FEED --><iframe>old</iframe><!-- END:INSTAGRAM_FEED --><section id="ai-news">news</section></body></html>'
        result=apply_instagram_feed(original)
        self.assertEqual(strip_instagram_feed(result),strip_instagram_feed(original))
        self.assertEqual(apply_instagram_feed(result),result)
        self.assertEqual(result.count(HEAD),1)
    def test_missing_anchor_fails(self):
        with self.assertRaises(ValueError): apply_instagram_feed('<head></head>')
if __name__=='__main__': unittest.main()
