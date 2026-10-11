import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bs4 import BeautifulSoup

from core.editorial_feed import apply_blog_feed, apply_home_feed, public_posts, _config, _post_image
from core.home_updates import published_posts as legacy_public_posts


CSS = (Path(__file__).resolve().parents[1] / 'site/templates/ai-news/editorial-feed.css').read_text(encoding='utf-8')


def card(slug, published, title='仕事のヒント', summary='仕事を少し楽にする実践メモ。'):
    return (f'<a class="tr-card" href="./{slug}.html"><div class="tr-title">{title}</div>'
            f'<div class="tr-date">{published}</div><div class="tr-sum">{summary}</div></a>')


def blog_shell(cards):
    return ('<!doctype html><html><head><title>AI相談</title></head><body>'
            '<header class="site-header"><nav>navigation stays</nav></header>'
            '<header><h1>ブログ</h1></header><div class="content-wrap"><div class="tr-section">'
            '<p>Existing introduction stays.</p><div class="tr-grid">' + cards + '</div></div></div>'
            '<footer>footer stays</footer><script>existingScript();</script></body></html>')


def home_shell(published='2026-10-11'):
    return ('<html><head><style id="existing">keep</style></head><body><main>'
            '<section id="top">hero stays</section>'
            f'<section id="ai-news"><h2>今日のAIニュース5とCodex</h2><time datetime="{published}">更新</time></section>'
            '<section id="packages">courses stay</section>'
            '<section id="latest-blog">old list</section><section id="speaker">profile stays</section>'
            '</main></body></html>')


class EditorialFeedTests(unittest.TestCase):
    def setUp(self):
        self.index = blog_shell(
            card('older', '2026-10-05') + card('newest', '2026-10-09') +
            card('oldest', '2026-09-28') + card('codex-update-log', '2026-10-11'))
        self.posts = public_posts(self.index)

    def test_only_published_unique_cards_are_used(self):
        index = self.index.replace('</body>',
            card('newest', '2026-10-09') +
            card('external', '2026-10-10').replace('./external.html', 'https://other.example/post.html') +
            '<a href="./unpublished-draft.html">draft</a></body>')
        self.assertEqual([p['href'] for p in public_posts(index)],
                         ['/blog/newest.html', '/blog/older.html', '/blog/oldest.html'])
        with self.assertRaises(ValueError):
            public_posts(blog_shell(card('bad-date', 'not-a-date')))

    def test_home_keeps_news_independent_and_latest_three_blogs(self):
        result = apply_home_feed(home_shell(), self.posts, CSS)
        soup = BeautifulSoup(result, 'html.parser')
        rows = soup.select('#blog .editorial-feed__row')
        self.assertEqual([row['href'] for row in rows],
                         ['/blog/newest.html', '/blog/older.html', '/blog/oldest.html'])
        self.assertEqual(len(soup.select('#blog img')), 3)
        self.assertFalse(soup.select('#blog .tr-sum'))
        self.assertNotIn('仕事を少し楽にする実践メモ。', str(soup.select_one('#blog')))
        self.assertEqual(soup.select_one('#ai-news time')['datetime'], '2026-10-11')
        self.assertEqual(soup.select_one('#blog .editorial-feed__more')['href'], '/blog/')
        self.assertEqual(soup.select_one('#blog .editorial-feed__more').get_text(strip=True), 'もっと見る→')
        self.assertEqual(len(soup.select('#blog .editorial-feed__more')), 1)
        self.assertFalse(soup.select('#ai-news section, #latest-blog'))
        self.assertEqual(len(soup.select('#blog')), 1)

    def test_home_is_idempotent_and_daily_regeneration_uses_new_date(self):
        first = apply_home_feed(home_shell(), self.posts, CSS)
        self.assertEqual(apply_home_feed(first, self.posts, CSS), first)
        fresh = re.sub(r'<section id="ai-news".*?</section>',
                       '<section id="ai-news"><time datetime="2026-10-12">更新</time></section>',
                       first, flags=re.S)
        result = BeautifulSoup(apply_home_feed(fresh, self.posts, CSS), 'html.parser')
        self.assertEqual(result.select_one('#ai-news time')['datetime'], '2026-10-12')
        self.assertEqual(len(result.select('#blog .editorial-feed__row')), 3)
        self.assertEqual(len(result.select('#editorial-feed-style')), 1)

    def test_home_preserves_other_sections_and_rejects_missing_inputs(self):
        result = apply_home_feed(home_shell(), self.posts, CSS)
        for fragment in ('<section id="top">hero stays</section>',
                         '<section id="packages">courses stay</section>',
                         '<section id="speaker">profile stays</section>',
                         '<style id="existing">keep</style>'):
            self.assertIn(fragment, result)
        with self.assertRaises(ValueError):
            apply_home_feed(home_shell().replace('datetime="2026-10-11"', ''), self.posts, CSS)
        with self.assertRaises(ValueError):
            apply_home_feed(home_shell(), self.posts[:1], CSS)

    def test_archive_preserves_public_metadata_and_shell_without_codex_duplicate(self):
        before = legacy_public_posts(self.index)
        result = apply_blog_feed(self.index, '2026-10-11', CSS)
        self.assertEqual(legacy_public_posts(result), before)
        self.assertEqual(apply_blog_feed(result, '2026-10-11', CSS), result)
        soup = BeautifulSoup(result, 'html.parser')
        self.assertEqual(len(soup.select('.editorial-feed__row')), 3)
        self.assertEqual(len(soup.select('.editorial-feed__news')), 0)
        self.assertEqual(len(soup.select('a.tr-card')), 3)
        self.assertEqual(len(soup.select('.editorial-feed__row img')), 3)
        self.assertNotIn('/codex-update-log.html', result)
        self.assertEqual(soup.title.get_text(), 'AI相談')
        self.assertIn('href="./newest.html"', result)
        for fragment in ('<header class="site-header"><nav>navigation stays</nav></header>',
                         '<p>Existing introduction stays.</p>',
                         '<footer>footer stays</footer><script>existingScript();</script>'):
            self.assertIn(fragment, result)

    def test_titles_and_summaries_are_escaped_without_losing_text(self):
        title = '&lt;AI&gt; &amp; "私の仕事"'
        summary = '&lt;img src=x onerror=bad()&gt; &amp; 続きを読む'
        index = blog_shell(card('one', '2026-10-09', title, summary) + card('two', '2026-10-08'))
        result = apply_blog_feed(index, '2026-10-11', CSS)
        soup = BeautifulSoup(result, 'html.parser')
        first = soup.select('a.tr-card')[0]
        self.assertEqual(first.select_one('.tr-title').get_text(), '<AI> & "私の仕事"')
        self.assertEqual(first.select_one('.tr-sum').get_text(), '<img src=x onerror=bad()> & 続きを読む')
        self.assertEqual(len(first.select('img')), 1)
        self.assertEqual(legacy_public_posts(result), legacy_public_posts(index))

    def test_future_public_article_image_and_safe_fallback(self):
        post = {'href': '/blog/future-post.html', 'title': '次の記事', 'date': '2026-10-12',
                'summary': '新しい実践', 'image': '/img/future.webp', 'image_alt': '次の記事の図'}
        with TemporaryDirectory() as directory, patch('core.editorial_feed.ROOT', Path(directory)):
            config = _config()
            self.assertEqual(_post_image(post, config), ('/img/future.webp', '次の記事の図'))
            post['image'] = 'javascript:alert(1)'
            self.assertEqual(_post_image(post, config), (config['fallback']['image'], config['fallback']['alt']))
            content = Path(directory) / 'content/blog'
            content.mkdir(parents=True)
            (content / 'future-post.md').write_text('---\nimage: /img/frontmatter.webp\nimage_alt: 記事の画像\n---\n', encoding='utf-8')
            self.assertEqual(_post_image(post, config), ('/img/frontmatter.webp', '記事の画像'))

    def test_archive_dates_accept_display_labels_and_prefer_machine_values(self):
        cards = card('japanese', '2026年10月9日 更新') + card('suffix', '2026-10-05 更新')
        cards += card('machine', '昨日更新').replace('<div class="tr-date">', '<div class="tr-date" data-date="2026-10-10">')
        original = blog_shell(cards)
        posts = public_posts(original)
        self.assertEqual([post['date'] for post in posts], ['2026-10-10', '2026-10-09', '2026-10-05'])
        result = apply_blog_feed(original, '2026-10-11', CSS)
        soup = BeautifulSoup(result, 'html.parser')
        self.assertEqual([node.get_text() for node in soup.select('a.tr-card .tr-date')],
                         ['昨日更新', '2026年10月9日 更新', '2026-10-05 更新'])
        self.assertEqual([post['date'] for post in public_posts(result)], ['2026-10-10', '2026-10-09', '2026-10-05'])
        self.assertEqual(apply_blog_feed(result, '2026-10-11', CSS), result)

    def test_mobile_keeps_image_left_and_titles_readable(self):
        mobile = CSS.split('@media (max-width: 680px)', 1)[1]
        self.assertIn('grid-template-columns: 160px minmax(0, 1fr)', CSS)
        self.assertIn('grid-template-columns: 96px minmax(0, 1fr)', mobile)
        self.assertIn('width: 96px; height: 80px', mobile)
        self.assertIn('font-size: 16px', mobile)
        self.assertIn('overflow-wrap: anywhere', CSS)
        self.assertIn('focus-visible', CSS)
        self.assertNotIn('animation:', CSS)


if __name__ == '__main__':
    unittest.main()