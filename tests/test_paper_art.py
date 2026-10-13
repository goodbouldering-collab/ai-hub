import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from core.paper_art import apply_paper_art, ROOT

class PaperArtTests(unittest.TestCase):
    def test_only_illustrations_change_and_reapplying_preserves_style_order(self):
        source='''<html><head></head><body><img src="/design-system/studio/images/hero-workshop-1672.webp"><img src="/img/speaker.webp"><a href="/booking"><img src="/design-system/studio/images/photo-20261011/agent.webp" srcset="old.webp 2x"></a></body></html>'''
        result=apply_paper_art(source)
        soup=BeautifulSoup(result,'html.parser')
        self.assertEqual([i['src'] for i in soup.select('img')][:2],['/design-system/studio/images/hero-workshop-1672.webp','/img/speaker.webp'])
        art=soup.select_one('a img')
        self.assertNotIn('srcset',art.attrs)
        self.assertTrue((ROOT/'site/static'/art['src'].lstrip('/')).is_file())
        self.assertEqual(soup.a['href'],'/booking')
        other=result.replace('</head>','<style id="other">x{}</style></head>')
        self.assertEqual(apply_paper_art(other),other)

    def test_frozen_home_keeps_hero_news_and_all_course_links(self):
        soup=BeautifulSoup((ROOT/'site/templates/ai-news/home.html').read_text(encoding='utf8'),'html.parser')
        self.assertIn('hero-workshop',soup.select_one('#top img')['src'])
        self.assertEqual(len(soup.select('#packages .compact-course-card')),7)
        self.assertFalse(soup.select('#ai-news img'))
        for image in soup.select('img[src*="paper-20261014"]'):
            self.assertTrue((ROOT/'site/static'/image['src'].lstrip('/')).is_file())
