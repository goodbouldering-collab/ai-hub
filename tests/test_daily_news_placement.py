import unittest
from bs4 import BeautifulSoup
from scripts.build_ai_news_feature import place_news_in_blog


class DailyNewsPlacementTests(unittest.TestCase):
    def test_nested_news_moves_without_truncating_hero_or_blog(self):
        hero = '<section id="top"><section id="diagnosis-start">diagnosis</section>art</section>'
        news = '<section id="ai-news"><time datetime="2026-10-13">更新</time><ol><li>headline</li></ol></section>'
        source = hero + '<section id="blog"><header class="editorial-feed__heading">blog</header>' + news + '<ol class="editorial-feed__list"><li>article</li></ol></section>'
        output = place_news_in_blog(source)
        soup = BeautifulSoup(output, 'html.parser')
        self.assertIn(hero, output)
        self.assertIsNotNone(soup.select_one('#blog > .editorial-feed__list > #ai-news .tr-title'))
        self.assertIn('今日のAIニュース4とCodex', soup.select_one('#blog').get_text())
        self.assertTrue(soup.select_one('#blog').get_text().endswith('article'))
        self.assertEqual(len(soup.select('#ai-news img')), 1)
        self.assertEqual(place_news_in_blog(output), output)

    def test_missing_or_duplicate_entries_fail_closed(self):
        for source in ('<section id="top"></section>', '<section id="ai-news"></section>',
                       '<section id="top"></section><section id="ai-news"></section><section id="ai-news"></section>'):
            with self.assertRaises(ValueError):
                place_news_in_blog(source)
