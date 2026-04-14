"""
ソースから記事を取得するモジュール。
sources.yaml の type に応じて取得方法を切り替える。
新しい type を追加するときはここに関数を1つ足すだけ。
"""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import yaml


@dataclass
class Article:
    source: str
    category: str
    title: str
    url: str
    body: str
    published: str
    fetched_at: str
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            key = f"{self.source}|{self.url}|{self.title}".encode("utf-8")
            self.hash = hashlib.sha256(key).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_sources(config_path) -> list[dict]:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [s for s in data.get("sources", []) if s.get("enabled", True)]


def _entry_datetime(entry) -> datetime | None:
    """エントリから公開日時を datetime で取り出す。取れなければ None。"""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def fetch_rss(source: dict, max_age_hours: int | None = None) -> list[Article]:
    parsed = feedparser.parse(source["url"])
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    limit = source.get("limit", 20)
    cutoff: datetime | None = None
    if max_age_hours:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    articles: list[Article] = []
    skipped_old = 0
    for entry in parsed.entries[:limit]:
        title = getattr(entry, "title", "").strip()
        url = getattr(entry, "link", "").strip()
        if not title or not url:
            continue

        entry_dt = _entry_datetime(entry)
        if cutoff and entry_dt and entry_dt < cutoff:
            skipped_old += 1
            continue

        body = (
            getattr(entry, "summary", "")
            or getattr(entry, "description", "")
            or ""
        ).strip()
        published = (
            getattr(entry, "published", None)
            or getattr(entry, "updated", None)
            or ""
        )
        articles.append(
            Article(
                source=source["name"],
                category=source.get("category", "未分類"),
                title=title,
                url=url,
                body=body,
                published=str(published),
                fetched_at=now,
            )
        )
    if skipped_old:
        print(f"    (古い記事 {skipped_old}件をスキップ)")
    return articles


DISPATCH = {
    "rss": fetch_rss,
    # 将来の拡張ポイント:
    # "web_scrape": fetch_web_scrape,
    # "x_api": fetch_x_api,
    # "youtube": fetch_youtube,
}


def collect_all(config_path, max_age_hours: int | None = None) -> list[Article]:
    sources = load_sources(config_path)
    results: list[Article] = []
    for src in sources:
        fn = DISPATCH.get(src["type"])
        if not fn:
            print(f"[warn] unknown source type: {src['type']} ({src['name']})")
            continue
        try:
            if src["type"] == "rss":
                items = fn(src, max_age_hours=max_age_hours)
            else:
                items = fn(src)
            print(f"[+] {src['name']}: {len(items)}件取得")
            results.extend(items)
        except Exception as e:
            print(f"[!] {src['name']} 取得失敗: {e}")
    return results
