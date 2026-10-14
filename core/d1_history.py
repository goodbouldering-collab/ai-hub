"""D1 history through the existing Wrangler login and central target guard.

No service-role/API token is read. Errors abort before publishing a new digest.
"""
from __future__ import annotations
import json
import subprocess
from collections import Counter
from pathlib import Path


class D1HistoryStore:
    def upsert(self, articles):
        if not articles:
            return [], []
        root = Path(__file__).resolve().parents[1]
        fresh, existing = [], []
        for start in range(0, len(articles), 200):
            batch = articles[start:start + 200]
            rows = [{key: getattr(article, key) for key in
                     ('hash', 'source', 'category', 'title', 'url', 'body', 'published')}
                    for article in batch]
            try:
                result = subprocess.run(
                    ['node', str(root / 'scripts/auxiliary-history.mjs'), 'upsert'],
                    input=json.dumps(rows, ensure_ascii=False), text=True, encoding='utf-8',
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, check=True,
                    cwd=root,
                )
                receipt = json.loads(result.stdout)
                new_counts = Counter(receipt['newHashes'])
                existing_counts = Counter(receipt['existingHashes'])
                if new_counts + existing_counts != Counter(article.hash for article in batch):
                    raise ValueError('Unexpected history receipt')
            except (subprocess.SubprocessError, ValueError, KeyError, TypeError, OSError):
                raise RuntimeError('D1記事履歴を確認できません。公開を止め、保存先と移行状態を確認してください。') from None
            for article in batch:
                if new_counts[article.hash]:
                    fresh.append(article)
                    new_counts[article.hash] -= 1
                else:
                    existing.append(article)
        return fresh, existing

    def close(self):
        pass
