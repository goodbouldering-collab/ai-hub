"""A daily release must not silently publish a pending site redesign."""
import hashlib
import json
import re
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from scripts import build_ai_news_feature as builder


class PublishedPresentationTests(unittest.TestCase):
    def test_preserves_cascade_order_with_later_site_styles(self):
        shell = "<head><style id='ai-news-compact-style'>old</style><style id='site'>override</style></head>"
        self.assertEqual(builder.apply_compact_style(shell, 'new'), shell.replace('>old<', '>new<'))

    def test_rebased_shell_replaces_only_news_style(self):
        shell = '<html><head><style id="other">keep</style></head><body>keep</body></html>'
        first = builder.apply_compact_style(shell, 'old rules')
        second = builder.apply_compact_style(first, 'new rules')
        self.assertEqual(second.count('ai-news-compact-style'), 1)
        self.assertNotIn('old rules', second)
        self.assertIn('<style id="other">keep</style>', second)
        self.assertIn('<body>keep</body>', second)
        self.assertEqual(builder.apply_compact_style(second, 'new rules'), second)

    def test_preservation_requires_a_baseline(self):
        with self.assertRaisesRegex(ValueError, 'verified asset baseline'):
            builder.build(Path('unused'), preserve_baseline_presentation=True)

    def test_preserves_published_css_crlf_and_rejects_tampered_baseline(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('content/daily-ai-news.json', 'content/ai-news/codex-update-log.md', 'site/static/design-system/studio/focused-ux.js'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(builder.ROOT / name, target)
            shutil.copytree(builder.ROOT / 'site/static/design-system/studio/images/paper-20261014', root / 'site/static/design-system/studio/images/paper-20261014')
            with patch.object(builder, 'ROOT', root), patch.object(builder.subprocess, 'check_output', return_value='test-sha'), patch.object(builder, 'decorate_public_tree', return_value=[]), patch.object(builder, 'apply_page_art_tree', return_value=[]):
                base = root / 'base'
                builder.build(base)
            home = base / 'index.html'
            home.write_bytes(home.read_bytes().replace(b'\n', b'\r\n'))
            (base / 'published.css').write_text('/* exact live CSS */', encoding='utf-8')
            hashes = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
            (root / 'content/ai-news/release-baseline.json').write_text(json.dumps({'assets': hashes}), encoding='utf-8')
            # Daily releases first rebase their shell from the last live page.
            templates = root / 'templates'
            shutil.copytree(builder.TEMPLATES, templates)
            shell = re.sub(r'<section\b[^>]*id=[\'\"]ai-news[\'\"][^>]*>.*?</section>', '{{AI_NEWS_FEATURE}}', home.read_text(encoding='utf-8'), flags=re.S)
            if '{{AI_NEWS_FEATURE}}' not in shell:
                # The approved four-item edition places news inside the blog
                # list. Rebase the fixture with a temporary feature placeholder;
                # the builder integrates it back into the same list.
                from core.editorial_feed import _ElementSpans
                news_spans = _ElementSpans(shell, element_id='ai-news').spans
                self.assertEqual(len(news_spans), 1)
                start, end = news_spans[0]
                shell = shell[:start] + '{{AI_NEWS_FEATURE}}' + shell[end:]
            (templates / 'home.html').write_text(shell, encoding='utf-8')
            with patch.object(builder, 'ROOT', root), patch.object(builder, 'TEMPLATES', templates), patch.object(builder.subprocess, 'check_output', return_value='test-sha'), patch.object(builder, 'decorate_public_tree', side_effect=AssertionError('Pending design must not run')), patch.object(builder, 'apply_page_art_tree', side_effect=AssertionError('Pending image replacement must not run')), patch.object(builder, 'apply_hero_copy', side_effect=AssertionError('Daily updates must preserve live style order')), patch.object(builder, 'apply_instagram_feed', side_effect=AssertionError('Daily updates must preserve live integrations')):
                output = root / 'release'
                builder.build(output, base, preserve_baseline_presentation=True)
                self.assertEqual(home.read_bytes(), (output / 'index.html').read_bytes())
                self.assertEqual((base / 'published.css').read_bytes(), (output / 'published.css').read_bytes())
                (base / 'published.css').write_text('tampered', encoding='utf-8')
                with self.assertRaisesRegex(AssertionError, 'baseline differs'):
                    builder.build(root / 'rejected', base, preserve_baseline_presentation=True)
                self.assertFalse((root / 'rejected').exists())


if __name__ == '__main__':
    unittest.main()
