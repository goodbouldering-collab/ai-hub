import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from core.collector import Article
from core.differ import ArticleStore

ROOT = Path(__file__).resolve().parents[1]

class RetiredHistoryTests(unittest.TestCase):
    def test_sqlite_preserves_new_existing_and_reopen(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            path = Path(directory) / 'history.db'
            article = Article('fixture', 'test', 'Synthetic', 'https://example.invalid/a', 'body', '', '')
            store = ArticleStore(path)
            self.assertEqual(store.backend, 'sqlite')
            self.assertEqual(store.upsert([article]), ([article], []))
            store.close()
            reopened = ArticleStore(path)
            self.assertEqual(reopened.upsert([article]), ([], [article]))
            reopened.close()

    def test_retired_config_never_imports_sdk_or_opens_database(self):
        for configuration in ({'SUPABASE_URL': 'https://example.invalid'}, {'SUPABASE_SERVICE_ROLE_KEY': 'synthetic'}, {'ARTICLE_STORE': 'supabase'}, {'ARTICLE_STORE': 'd1'}, {'ARTICLE_STORE': ''}):
            with self.subTest(configuration=tuple(configuration)), tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, configuration, clear=True), patch('sqlite3.connect', side_effect=AssertionError('unexpected DB open')), patch.dict(sys.modules, {'supabase': None}):
                with self.assertRaises(RuntimeError):
                    ArticleStore(Path(directory) / 'history.db')
                self.assertFalse((Path(directory) / 'history.db').exists())

    def test_importer_is_terminal_before_optional_imports(self):
        result = subprocess.run([sys.executable, '-I', '-S', str(ROOT / 'scripts/migrate_sqlite_to_supabase.py')], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(b'ModuleNotFoundError', result.stderr)
        self.assertEqual(result.stdout, b'')

if __name__ == '__main__':
    unittest.main()
