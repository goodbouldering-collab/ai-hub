"""A daily release must not silently publish a pending site redesign."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from scripts import build_ai_news_feature as builder


class PublishedPresentationTests(unittest.TestCase):
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
            for name in ('content/daily-ai-news.json', 'content/ai-news/codex-update-log.md'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(builder.ROOT / name, target)
            with patch.object(builder, 'ROOT', root), patch.object(builder.subprocess, 'check_output', return_value='test-sha'), patch.object(builder, 'decorate_public_tree', return_value=[]):
                base = root / 'base'
                builder.build(base)
            home = base / 'index.html'
            home.write_bytes(home.read_bytes().replace(b'\n', b'\r\n'))
            (base / 'published.css').write_text('/* exact live CSS */', encoding='utf-8')
            hashes = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
            (root / 'content/ai-news/release-baseline.json').write_text(json.dumps({'assets': hashes}), encoding='utf-8')
            with patch.object(builder, 'ROOT', root), patch.object(builder.subprocess, 'check_output', return_value='test-sha'), patch.object(builder, 'decorate_public_tree', side_effect=AssertionError('Pending design must not run')):
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
