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


class _SupabaseStore:
    """
    Supabase (ai_watch.articles) に保存する実装。
    1回 insert を試み、重複(23505)なら既存扱い+last_seen更新、という戦略を取る。
    """

    def __init__(self):
        from supabase import create_client  # 遅延 import (未インストール環境でも SQLite 経路は動く)

        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        self.client = create_client(url, key)
        # ai_watch スキーマをデフォルトに切り替え
        self.tbl = self.client.schema("ai_watch").table("articles")

    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]:
        if not articles:
            return [], []

        hashes = [a.hash for a in articles]
        # 既存ハッシュを一括取得
        res = self.tbl.select("hash").in_("hash", hashes).execute()
        existing_hashes = {row["hash"] for row in (res.data or [])}

        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        new_items: list[Article] = []
        existing_items: list[Article] = []
        to_insert: list[dict] = []

        for a in articles:
            if a.hash in existing_hashes:
                existing_items.append(a)
            else:
                new_items.append(a)
                to_insert.append({
                    "hash": a.hash,
                    "source": a.source,
                    "category": a.category,
                    "title": a.title,
                    "url": a.url,
                    "body": a.body,
                    "published": a.published,
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                })

        if to_insert:
            # 念のため upsert(on hash) で競合耐性を持たせる
            self.tbl.upsert(to_insert, on_conflict="hash").execute()

        if existing_items:
            self.tbl.update({"last_seen": now_iso}).in_(
                "hash", [a.hash for a in existing_items]
            ).execute()

        return new_items, existing_items

    def close(self) -> None:
        pass


def _use_supabase() -> bool:
    return bool(os.environ.get("SUPABASE_URL")) and bool(os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))


class ArticleStore:
    """既存インタフェース互換のファサード。環境変数で保存先を自動選択。"""

    def __init__(self, db_path: Path):
        if _use_supabase():
            try:
                self._inner: _Store = _SupabaseStore()
                self.backend = "supabase"
                print(f"  [store] Supabase (ai_watch.articles)")
                return
            except Exception as e:
                print(f"  [store] Supabase 初期化失敗 → SQLite にフォールバック: {e}")

        self._inner = _SqliteStore(db_path)
        self.backend = "sqlite"
        print(f"  [store] SQLite ({db_path})")

    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]:
        return self._inner.upsert(articles)

    def close(self) -> None:
        self._inner.close()
