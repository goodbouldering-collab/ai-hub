import unittest
import re
from bs4 import BeautifulSoup
from core.home_updates import apply_home_updates, latest_published_posts


def card(slug, published, title='記事 &amp; 続き'):
    return f'<a class="tr-card" href="./{slug}.html"><div class="tr-title">{title}</div><div class="tr-date">{published}</div></a>'


class HomeUpdatesTests(unittest.TestCase):
    def test_public_index_sorted_deduplicated_and_codex_excluded(self):
        index = card('older', '2026-09-18') + card('newest', '2026-09-28') + card('older', '2026-09-18') + card('oldest', '2026-08-30') + card('codex-update-log', '2026-09-30')
        self.assertEqual([post['href'] for post in latest_published_posts(index)], ['/blog/newest.html', '/blog/older.html'])

    def test_rejects_incomplete_public_index_and_external_links(self):
        with self.assertRaises(ValueError):
            latest_published_posts(card('one', '2026-09-28') + card('two', '2026-09-18').replace('./two.html', 'https://example.com/two.html'))

    def test_missing_list_is_inserted_below_hero(self):
        shell = '<head></head><main><section id="ai-news">news</section><section id="speaker">profile</section></main>'
        result = apply_home_updates(shell, card('newest', '2026-10-08') + card('older', '2026-10-07'), 'css')
        self.assertLess(result.index('id="blog"'), result.index('id="speaker"'))
        self.assertNotIn("id='blog-carousel'", result)
        home = BeautifulSoup(result, 'html.parser')
        self.assertIsNotNone(home.select_one('#ai-news > #blog.home-updates__blog'))
        self.assertFalse(home.select('#ai-news section'))
        self.assertFalse(home.select('#latest-blog'))
        self.assertEqual(apply_home_updates(result, card('newest', '2026-10-08') + card('older', '2026-10-07'), 'css'), result)

    def test_daily_news_refresh_preserves_text_list(self):
        shell = '<head></head><main><section id="ai-news">old news</section><section id="packages">courses</section><section id="blog">old cards</section><section id="speaker">profile</section></main>'
        index = card('newest', '2026-10-08') + card('older', '2026-10-07')
        first = apply_home_updates(shell, index, 'css')
        refreshed = re.sub(r'<section id="ai-news">.*?</section>', '<section id="ai-news">new news</section>', first, flags=re.S)
        result = BeautifulSoup(apply_home_updates(refreshed, index, 'css'), 'html.parser')
        self.assertEqual(len(result.select('#blog')), 1)
        self.assertEqual(len(result.select('#latest-blog')), 0)
        self.assertEqual(result.select_one('#ai-news .home-updates__news').get_text(), 'new news')
        self.assertEqual(result.select_one('#ai-news').find_next_sibling()['id'], 'packages')

    def test_idempotent_transform_preserves_other_content_and_escapes_titles(self):
        shell = '<head><style>keep</style></head><main><section id="top">hero</section><section id="ai-news">news</section><section id="latest-blog">large carousel</section><section id="speaker">profile</section></main>'
        index = card('newest', '2026-09-28', '&lt;AI&gt; &amp; "news"') + card('older', '2026-09-18')
        result = apply_home_updates(shell, index, 'css')
        self.assertEqual(apply_home_updates(result, index, 'css'), result)
        self.assertIn('<section id="speaker">profile</section>', result)
        self.assertIn('<section id="top">hero</section>', result)
        self.assertIn('&lt;AI&gt; &amp; &quot;news&quot;', result)
        self.assertNotIn('large carousel', result)
        self.assertEqual(result.count('id="latest-blog"'), 0)
        self.assertEqual(result.count('id="blog"'), 1)
        self.assertNotIn("id='blog-carousel'", result)
        home = BeautifulSoup(result, 'html.parser')
        self.assertIsNotNone(home.select_one('#ai-news > #blog.home-updates__blog'))
        self.assertFalse(home.select('#ai-news section'))
        self.assertFalse(home.select('#latest-blog'))
        self.assertLess(result.index('id="blog"'), result.index('id="speaker"'))
        self.assertEqual(len(home.select("#blog li a")), 2)
        self.assertEqual(result.count('id="home-updates-style"'), 1)


if __name__ == '__main__':
    unittest.main()
