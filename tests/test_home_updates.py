import unittest
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

    def test_idempotent_transform_preserves_other_content_and_escapes_titles(self):
        shell = '<head><style>keep</style></head><main><section id="top">hero</section><section id="ai-news">news</section><section id="speaker">profile</section><section id="blog">large carousel</section></main>'
        index = card('newest', '2026-09-28', '&lt;AI&gt; &amp; "news"') + card('older', '2026-09-18')
        result = apply_home_updates(shell, index, 'css')
        self.assertEqual(apply_home_updates(result, index, 'css'), result)
        self.assertIn('<section id="speaker">profile</section>', result)
        self.assertIn('<section id="top">hero</section>', result)
        self.assertIn('&lt;AI&gt; &amp; &quot;news&quot;', result)
        self.assertNotIn('large carousel', result)
        self.assertEqual(result.count('id="blog"'), 1)
        self.assertEqual(result.count('id="home-updates-style"'), 1)


if __name__ == '__main__':
    unittest.main()
