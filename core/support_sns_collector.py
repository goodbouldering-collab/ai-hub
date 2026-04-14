"""
サポートSNS巡回。

現在 RSS を公式提供しているのは YouTube のみ。
それ以外 (X / Instagram / Threads / Facebook) は公式RSS非対応のため
「未対応」としてスキップ記録だけ残す。
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
SUPPORT_SNS_YAML = ROOT / "config" / "support_sns.yaml"
OUT_DIR = ROOT / "outputs" / "support_sns"

PLATFORMS = [
    "youtube", "x",
    "instagram_feed", "instagram_reel", "instagram_story",
    "threads", "facebook",
]


def load_config() -> dict:
    if not SUPPORT_SNS_YAML.exists():
        return {p: [] for p in PLATFORMS}
    data = yaml.safe_load(SUPPORT_SNS_YAML.read_text(encoding="utf-8")) or {}
    sns = data.get("support_sns") or {}
    return {p: sns.get(p, []) or [] for p in PLATFORMS}


def extract_youtube_channel_id(url: str) -> str | None:
    """
    YouTube チャンネルページから channel_id を抽出する。
    /channel/UCxxx 形式ならそのまま返す。
    /@handle 形式はページ HTML から externalId を取り出す。
    """
    m = re.search(r"/channel/([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(1)

    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        m = re.search(r'"channelId":"(UC[A-Za-z0-9_-]{20,})"', r.text)
        if m:
            return m.group(1)
        m = re.search(r'"externalId":"(UC[A-Za-z0-9_-]{20,})"', r.text)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def fetch_youtube_feed(account: dict, limit: int = 10) -> list[dict]:
    url = account.get("url", "")
    if not url:
        return []
    channel_id = extract_youtube_channel_id(url)
    if not channel_id:
        return []
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        feed = feedparser.parse(rss_url)
    except Exception:
        return []
    items: list[dict] = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published": entry.get("published", ""),
            "video_id": entry.get("yt_videoid", ""),
            "thumbnail": (
                entry.media_thumbnail[0]["url"]
                if getattr(entry, "media_thumbnail", None) else ""
            ),
        })
    return items


def run() -> dict:
    """全プラットフォームを巡回して outputs/support_sns/latest.json に保存。"""
    cfg = load_config()
    result: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platforms": {},
    }

    for platform in PLATFORMS:
        accounts = cfg.get(platform, [])
        entries: list[dict] = []
        if platform == "youtube":
            for acc in accounts:
                items = fetch_youtube_feed(acc)
                entries.append({
                    "account": acc,
                    "items": items,
                    "status": "ok" if items else "empty",
                })
        else:
            for acc in accounts:
                entries.append({
                    "account": acc,
                    "items": [],
                    "status": "unsupported",
                })
        result["platforms"][platform] = entries

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "latest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    r = run()
    total = sum(
        sum(len(e["items"]) for e in r["platforms"][p])
        for p in PLATFORMS
    )
    print(f"[+] support_sns collected: {total} items")
