"""
SQLite で過去取得ログを保持し、新着(前回以降に初めて見た記事)を抽出する。
"""
from __future__ import annotations
import sqlite3
import time
from pathlib import Path

from .collector import Article


SCHEMA = """
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


class ArticleStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert(self, articles: list[Article]) -> tuple[list[Article], list[Article]]:
        """
        記事を保存し、(新着, 継続) のタプルで返す。
        新着 = DB に存在しなかったもの
        継続 = 既にあったもの (last_seen だけ更新)
        """
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
                    (
                        a.hash, a.source, a.category, a.title, a.url,
                        a.body, a.published, now, now,
                    ),
                )
                new_items.append(a)
            else:
                cur.execute(
                    "UPDATE articles SET last_seen = ? WHERE hash = ?",
                    (now, a.hash),
                )
                existing_items.append(a)
        self.conn.commit()
        return new_items, existing_items

    def close(self):
        self.conn.close()
