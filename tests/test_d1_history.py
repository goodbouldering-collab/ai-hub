import json
import os
import subprocess
import runpy
import socket
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from core.differ import ArticleStore
from core.d1_history import D1HistoryStore


class D1HistoryTests(unittest.TestCase):
    def article(self):
        return SimpleNamespace(hash='1234567890abcdef', source='fixture', category='test',
                               title='synthetic', url='https://example.org', body='fixture', published='')

    def test_default_sqlite_retains_first_seen_and_source(self):
        with patch.dict(os.environ, {}, clear=True):
            store = ArticleStore(Path(':memory:'))
            try:
                article = self.article()
                self.assertEqual(store.backend, 'sqlite')
                self.assertEqual(store.upsert([article]), ([article], []))
                self.assertEqual(store.upsert([article]), ([], [article]))
            finally:
                store.close()

    def test_legacy_env_stops_without_reading_values_or_reintroducing_supabase(self):
        with patch.dict(os.environ, {'SUPABASE_URL': 'synthetic'}, clear=True):
            with self.assertRaisesRegex(RuntimeError, '旧Supabase'):
                ArticleStore(Path('must-not-create.db'))

    def test_explicit_d1_uses_guarded_cli_with_stdin_and_preserves_duplicate_classification(self):
        article = self.article()
        reply = SimpleNamespace(stdout=json.dumps({'newHashes': [article.hash], 'existingHashes': [article.hash]}))
        with patch.dict(os.environ, {'ARTICLE_STORE': 'd1'}, clear=True), patch('core.d1_history.subprocess.run', return_value=reply) as run:
            store = ArticleStore(Path('must-not-create.db'))
            self.assertEqual(store.backend, 'd1')
            self.assertEqual(store.upsert([article, article]), ([article], [article]))
            args, kwargs = run.call_args
            self.assertTrue(args[0][1].endswith('auxiliary-history.mjs'))
            self.assertEqual(len(json.loads(kwargs['input'])), 2)
            self.assertNotIn('synthetic', ' '.join(args[0]))

    def test_d1_failure_and_invalid_receipt_do_not_fallback(self):
        for failure in [subprocess.CalledProcessError(1, 'node'), SimpleNamespace(stdout='{}')]:
            with patch('core.d1_history.subprocess.run', **({'side_effect': failure} if isinstance(failure, Exception) else {'return_value': failure})):
                with self.assertRaisesRegex(RuntimeError, 'D1記事履歴'):
                    D1HistoryStore().upsert([self.article()])

    def test_retired_importer_exits_before_any_network_or_secret_module(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/migrate_sqlite_to_supabase.py'
        with patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')) as network:
            module = runpy.run_path(str(script))
            self.assertEqual(module['main'](), 2)
            network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
