"""
data/history.db に入っている過去記事を Supabase ai_watch.articles へ一括投入する一回きりスクリプト。

前提:
    - ルート直下の .env に SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY が入っていること
    - requirements.txt の supabase>=2.5.0 がインストール済みであること

使い方:
    python scripts/migrate_sqlite_to_supabase.py
"""
from __future__ import annotations
import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "history.db"


def to_iso(ts: str) -> str:
    """SQLite の 'YYYY-MM-DD HH:MM:SS' を ISO8601 (UTCと解釈) に変換。"""
    return ts.replace(" ", "T") + "Z" if ts and "T" not in ts else ts


def main() -> int:
    load_dotenv(ROOT / ".env")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY が .env に無い")
        return 1

    client = create_client(url, key)
    tbl = client.schema("ai_watch").table("articles")

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} が見つからない")
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT hash, source, category, title, url, body, published, first_seen, last_seen FROM articles"
    ).fetchall()]
    conn.close()
    print(f"SQLite から {len(rows)} 件読み出し")

    payload = [
        {
            "hash": r["hash"],
            "source": r["source"],
            "category": r["category"],
            "title": r["title"],
            "url": r["url"],
            "body": r["body"],
            "published": r["published"],
            "first_seen": to_iso(r["first_seen"]),
            "last_seen": to_iso(r["last_seen"]),
        }
        for r in rows
    ]

    CHUNK = 100
    total = 0
    for i in range(0, len(payload), CHUNK):
        batch = payload[i : i + CHUNK]
        res = tbl.upsert(batch, on_conflict="hash").execute()
        total += len(batch)
        print(f"  投入 {total}/{len(payload)}")

    # 件数照合
    count_res = tbl.select("hash", count="exact").execute()
    print(f"Supabase 側の件数: {count_res.count}")
    print("完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
