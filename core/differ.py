"""
過去取得ログを保持し、新着(前回以降に初めて見た記事)を抽出する。

ストレージは 2 系統:
  - Supabase (推奨・本番 / GitHub Actions): SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY が揃っていれば自動で使う
  - SQLite (フォールバック): 上記が無ければ従来どおり data/history.db を使う

呼び出し側(run.py)は従来どおり `ArticleStore(DB)` で生成し、`upsert()` / `close()` を呼ぶだけでよい。
"""
from __future__ import annotations
import os
import sqlite3
import time
from pathlib import Path
from typing import Protocol

from .collector import Article


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    hash TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    body TEXT,
    published TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_first_seen ON articles(first_seen);
CREATE INDEX IF NOT EXISTS idx_category ON articles(category);
"""


class _Store(Protocol):
    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]: ...
    def close(self) -> None: ...


class _SqliteStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.executescript(SQLITE_SCHEMA)
        self.conn.commit()

    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        new_items: list[Article] = []
        existing_items: list[Article] = []
        cur = self.conn.cursor()
        for a in articles:
            cur.execute("SELECT hash FROM articles WHERE hash = ?", (a.hash,))
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    """INSERT INTO articles
                    (hash, source, category, title, url, body, published, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (a.hash, a.source, a.category, a.title, a.url, a.body, a.published, now, now),
                )
                new_items.append(a)
            else:
                cur.execute("UPDATE articles SET last_seen = ? WHERE hash = ?", (now, a.hash))
                existing_items.append(a)
        self.conn.commit()
        return new_items, existing_items

    def close(self) -> None:
        self.conn.close()


class ArticleStore:
    """Local history only. Retired cloud configuration fails before opening any DB."""

    def __init__(self, db_path: Path):
        backend = os.environ.get("ARTICLE_STORE", "sqlite")
        if backend != "sqlite":
            raise RuntimeError("ARTICLE_STORE must be sqlite; D1 migration is not yet accepted.")
        if os.environ.get("SUPABASE_URL") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
            raise RuntimeError("Retired Supabase history configuration detected. Confirm history migration before changing the backend.")
        self._inner: _Store = _SqliteStore(db_path)
        self.backend = "sqlite"
        print(f"  [store] SQLite ({db_path})")

    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]:
        return self._inner.upsert(articles)

    def close(self) -> None:
        self._inner.close()
