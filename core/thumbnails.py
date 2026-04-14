"""
記事のサムネ画像URLを取得する。
- YouTube: URL から video_id を抜いて img.youtube.com 直叩き
- 一般記事: og:image / twitter:image を HEAD+GET で拾う
キャッシュは data/thumb_cache.json にSHA256単位で保存して再取得しない。
"""
from __future__ import annotations
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

from .collector import Article


YT_ID_RE = re.compile(r"(?:v=|youtu\.be/|/shorts/|watch\?v=)([A-Za-z0-9_-]{11})")
OG_RE = re.compile(
    r"""<meta[^>]+(?:property|name)\s*=\s*["'](?:og:image|twitter:image)["'][^>]*content\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
OG_RE2 = re.compile(
    r"""<meta[^>]+content\s*=\s*["']([^"']+)["'][^>]+(?:property|name)\s*=\s*["'](?:og:image|twitter:image)["']""",
    re.IGNORECASE,
)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

_lock = threading.Lock()


def youtube_thumb(url: str) -> str | None:
    m = YT_ID_RE.search(url)
    if not m:
        return None
    return f"https://img.youtube.com/vi/{m.group(1)}/hqdefault.jpg"


def fetch_og_image(url: str, timeout: int = 8) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout, allow_redirects=True)
        if r.status_code != 200:
            return None
        head = r.text[:30000]
        m = OG_RE.search(head) or OG_RE2.search(head)
        if not m:
            return None
        img = m.group(1).strip()
        if img.startswith("//"):
            img = "https:" + img
        elif img.startswith("/"):
            p = urlparse(url)
            img = f"{p.scheme}://{p.netloc}{img}"
        return img
    except Exception:
        return None


class ThumbCache:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, str] = {}
        if path.exists():
            try:
                self.data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}

    def get(self, key: str) -> str | None:
        return self.data.get(key)

    def set(self, key: str, value: str) -> None:
        with _lock:
            self.data[key] = value

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def resolve_thumbnails(articles: list[Article], cache_path: Path) -> dict[str, str]:
    """hash -> thumbnail_url の辞書を返す。キャッシュで既知のものは再取得しない。"""
    cache = ThumbCache(cache_path)
    result: dict[str, str] = {}
    pending: list[Article] = []

    for a in articles:
        cached = cache.get(a.hash)
        if cached is not None:
            if cached:
                result[a.hash] = cached
            continue
        yt = youtube_thumb(a.url)
        if yt:
            cache.set(a.hash, yt)
            result[a.hash] = yt
            continue
        pending.append(a)

    if pending:
        print(f"[+] サムネ取得中: {len(pending)}件...")
        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(fetch_og_image, a.url): a for a in pending}
            for fut in as_completed(futs):
                a = futs[fut]
                img = fut.result() or ""
                cache.set(a.hash, img)
                if img:
                    result[a.hash] = img

    cache.save()
    return result
