"""
過去取得ログを保持し、新着(前回以降に初めて見た記事)を抽出する。

ストレージは 2 系統:
  - D1: ARTICLE_STORE=d1 を明示した場合だけ、台帳・正本ガード付きの既存Wranglerログインを使う
  - SQLite: 既定のローカル履歴 data/history.db。D1障害時には戻さない

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
    """既存インタフェース互換のファサード。保存先を明示選択し、旧Supabase設定では停止。"""

    def __init__(self, db_path: Path):
        backend = os.environ.get("ARTICLE_STORE", "sqlite")
        if backend == "d1":
            from .d1_history import D1HistoryStore
            self._inner = D1HistoryStore()
            self.backend = "d1"
            print("  [store] Cloudflare D1 (central target guard required)")
            return
        if backend != "sqlite":
            raise RuntimeError("ARTICLE_STORE must be sqlite or d1")
        if os.environ.get("SUPABASE_URL") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
            raise RuntimeError("旧Supabase履歴設定を検出しました。D1移行を確認するまで自動切替しません。")
        self._inner = _SqliteStore(db_path)
        self.backend = "sqlite"
        print(f"  [store] SQLite ({db_path})")

    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]:
        return self._inner.upsert(articles)

    def close(self) -> None:
        self._inner.close()
