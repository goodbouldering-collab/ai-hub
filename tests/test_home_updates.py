import importlib.util
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bs4 import BeautifulSoup

from core.home_updates import apply_home_updates, latest_published_posts
from core.editorial_feed import public_posts
from core.studio_design import decorate_html
from scripts.build_ai_news_feature import render_feature

ROOT = Path(__file__).resolve().parents[1]


def card(slug, published, title='記事 &amp; 続き'):
    return (f'<a class="tr-card" href="./{slug}.html"><div class="tr-title">{title}</div>'
            f'<div class="tr-date">{published}</div><div class="tr-sum">仕事に使うヒント。</div></a>')


def news_feature(published='2026-10-10'):
    return f'<section id="ai-news"><time datetime="{published}">更新</time><p>今日のニュース</p></section>'


class HomeUpdatesTests(unittest.TestCase):
    def test_public_index_sorted_deduplicated_and_codex_excluded(self):
        index = card('older', '2026-09-18') + card('newest', '2026-09-28') + card('older', '2026-09-18') + card('oldest', '2026-08-30') + card('codex-update-log', '2026-09-30')
        self.assertEqual([post['href'] for post in latest_published_posts(index)], ['/blog/newest.html', '/blog/older.html'])

    def test_rejects_incomplete_public_index_and_external_links(self):
        with self.assertRaises(ValueError):
            latest_published_posts(card('one', '2026-09-28') + card('two', '2026-09-18').replace('./two.html', 'https://example.com/two.html'))

    def test_feed_below_independent_news_has_latest_three_articles(self):
        shell = '<head></head><main><section id="top">hero</section>' + news_feature() + '<section id="speaker">profile</section></main>'
        index = card('newest', '2026-10-08') + card('older', '2026-10-07') + card('oldest', '2026-09-30')
        result = apply_home_updates(shell, index, 'css')
        home = BeautifulSoup(result, 'html.parser')
        self.assertIsNotNone(home.select_one('#ai-news + #blog.editorial-feed'))
        self.assertEqual([row['href'] for row in home.select('#blog .editorial-feed__row')],
                         ['/blog/newest.html', '/blog/older.html', '/blog/oldest.html'])
        self.assertEqual(len(home.select('#blog .editorial-feed__row img')), 3)
        self.assertEqual(home.select_one('#blog .editorial-feed__more')['href'], '/blog/')
        self.assertEqual(len(home.select('#blog .editorial-feed__more')), 1)
        self.assertFalse(home.select('#ai-news section, #latest-blog, #blog-carousel'))
        self.assertLess(result.index('id="blog"'), result.index('id="speaker"'))
        self.assertEqual(apply_home_updates(result, index, 'css'), result)

    def test_daily_regeneration_preserves_layout_and_updates_news_date(self):
        shell = '<head></head><main>' + news_feature() + '<section id="packages">courses</section><section id="blog">old cards</section><section id="speaker">profile</section></main>'
        index = card('newest', '2026-10-08') + card('older', '2026-10-07')
        first = apply_home_updates(shell, index, 'css')
        refreshed = re.sub(r'<section\b[^>]*id="ai-news"[^>]*>.*?</section>', news_feature('2026-10-11'), first, flags=re.S)
        result = BeautifulSoup(apply_home_updates(refreshed, index, 'css'), 'html.parser')
        self.assertEqual(len(result.select('#blog')), 1)
        self.assertEqual(len(result.select('#blog .editorial-feed__row')), 2)
        self.assertEqual(result.select_one('#ai-news time')['datetime'], '2026-10-11')
        self.assertFalse(result.select('#latest-blog, #blog-carousel'))
        self.assertEqual(result.select_one('#ai-news').find_next_sibling()['id'], 'blog')

    def test_transform_preserves_other_content_and_escapes_titles(self):
        shell = '<head><style>keep</style></head><main><section id="top">hero</section>' + news_feature() + '<section id="latest-blog">large carousel</section><section id="speaker">profile</section></main>'
        index = card('newest', '2026-09-28', '&lt;AI&gt; &amp; "news"') + card('older', '2026-09-18')
        result = apply_home_updates(shell, index, 'css')
        self.assertEqual(apply_home_updates(result, index, 'css'), result)
        self.assertIn('<section id="speaker">profile</section>', result)
        self.assertIn('<section id="top">hero</section>', result)
        self.assertIn('&lt;AI&gt; &amp; &quot;news&quot;', result)
        self.assertNotIn('large carousel', result)
        home = BeautifulSoup(result, 'html.parser')
        self.assertEqual(len(home.select('#blog')), 1)
        self.assertEqual(len(home.select('#home-updates-style')), 1)
        self.assertEqual(len(home.select('#editorial-feed-style')), 1)
        self.assertEqual(len(home.select('#editorial-home-style')), 1)

    def test_newer_codex_update_controls_the_combined_news_date(self):
        news = {'date': '2026-10-09', 'items': [{'title': '以前のニュース'}]}
        feature = render_feature(news, '10月10日更新', '2026-10-10')
        self.assertIn('datetime="2026-10-10"', feature)
        self.assertIn('10月10日更新', feature)
        index = card('newest', '2026-10-08') + card('older', '2026-10-07')
        home = BeautifulSoup(apply_home_updates('<head></head>' + feature, index, 'css'), 'html.parser')
        self.assertEqual(home.select_one('#ai-news time')['datetime'], '2026-10-10')

    def test_normal_blog_index_keeps_approved_articles_and_content_dates(self):
        spec = importlib.util.spec_from_file_location('editorial_site_builder', ROOT / 'site/build_site.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        approved_source = (ROOT / 'site/templates/ai-news/blog.html').read_text(encoding='utf-8')
        expected = [{key: post[key] for key in ('href', 'title', 'date', 'summary')}
                    for post in public_posts(approved_source)]
        with TemporaryDirectory() as folder:
            temporary = Path(folder)
            source = temporary / 'source'
            source.mkdir()
            (source / 'unpublished-local.md').write_text(
                '---\ntitle: まだ公開していない記事\ndate: 2026-10-11\n---\nローカル本文', encoding='utf-8')
            with patch.object(builder, 'BLOG_DIR', source), patch.object(builder, 'DIST', temporary / 'dist'):
                builder.build_blog()
                index = (builder.DIST / 'blog/index.html').read_text(encoding='utf-8')
        actual = [{key: post[key] for key in ('href', 'title', 'date', 'summary')}
                  for post in public_posts(index)]
        self.assertEqual(actual, expected)
        self.assertNotIn('unpublished-local.html', index)
        soup = BeautifulSoup(index, 'html.parser')
        self.assertEqual(len(soup.select('.editorial-feed__row')), len(expected))
        self.assertFalse(soup.select('.editorial-feed__news, a[href="/ai-news/"]'))
        with TemporaryDirectory() as folder:
            temporary = Path(folder)
            codex = temporary / 'content/ai-news/codex-update-log.md'
            codex.parent.mkdir(parents=True)
            codex.write_text('---\ndate: 2026-08-21\ndate_modified: 2026-10-10\n---\nCodex', encoding='utf-8')
            with patch.object(builder, 'ROOT', temporary):
                self.assertEqual(builder._editorial_news_date({'date': '2026-10-09'}), '2026-10-10')
                self.assertEqual(builder._editorial_news_date({'date': '2026-10-12'}), '2026-10-12')
        self.assertEqual(soup.title.get_text(), 'AI相談')

    def test_redecoration_keeps_new_art_and_compact_course_structure(self):
        source = (ROOT / 'site/templates/ai-news/home.html').read_text(encoding='utf-8')
        source = source.replace('{{AI_NEWS_FEATURE}}', news_feature())
        index = (ROOT / 'site/templates/ai-news/blog.html').read_text(encoding='utf-8')
        approved = apply_home_updates(source, index, 'css')
        result = decorate_html(approved, home=True)
        soup = BeautifulSoup(result, 'html.parser')
        self.assertEqual(len(soup.select('#blog .editorial-feed__row')), 3)
        self.assertEqual(len(soup.select('.compact-course-card > .editorial-course-lead')), 6)
        self.assertEqual(len(soup.select('[data-editorial-course="20261011"]')), 6)
        self.assertEqual(len(soup.select('#editorial-home-style')), 1)
        for image in soup.select('#restored-hero-image img, .compact-course-visual, .focus-step-visual'):
            self.assertIn('/editorial-20261011/', image['src'])
        self.assertEqual(decorate_html(result, home=True), result)


if __name__ == '__main__':
    unittest.main()