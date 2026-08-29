"""Wait until the fixed Codex article fingerprint reaches Workers production."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import time
from typing import Any, Callable
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "content" / "blog" / "codex-update-log.md"
PRODUCTION_URL = "https://aiclimb.aiclimb.workers.dev/blog/codex-update-log.html"
PRODUCTION_HOST = "aiclimb.aiclimb.workers.dev"
PRODUCTION_PATH = "/blog/codex-update-log.html"
PRODUCTION_FINAL_PATHS = {PRODUCTION_PATH, "/blog/codex-update-log"}


def read_expected_fingerprint(article_path: Path = ARTICLE_PATH) -> str:
    text = article_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("Codex記事のfrontmatterがありません")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("Codex記事のfrontmatterを解析できません")
    meta = yaml.safe_load(parts[1]) or {}
    fingerprint = str(meta.get("source_fingerprint") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise ValueError("Codex記事のsource_fingerprintが不正です")
    return fingerprint


def wait_for_production(
    url: str,
    fingerprint: str,
    *,
    requester: Callable[..., Any] | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    attempts: int = 40,
    interval: float = 15,
) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() != PRODUCTION_HOST
        or parsed.path != PRODUCTION_PATH
    ):
        raise ValueError("検証先はCodex固定記事の本番URLだけです")
    if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise ValueError("検証するfingerprintが不正です")
    if attempts < 1 or interval < 0:
        raise ValueError("再試行設定が不正です")

    if requester is None:
        import requests

        requester = requests.get

    marker = f"<!-- source-fingerprint: {fingerprint} -->"
    last_status = "応答なし"
    for attempt in range(1, attempts + 1):
        try:
            response = requester(
                url,
                params={"verify": fingerprint[:12], "attempt": attempt},
                headers={"Cache-Control": "no-cache", "User-Agent": "AI-Sodan-Deploy-Verify/1.0"},
                timeout=20,
                allow_redirects=True,
            )
            final = urlparse(str(response.url))
            if (
                final.scheme != "https"
                or (final.hostname or "").lower() != PRODUCTION_HOST
                or final.path not in PRODUCTION_FINAL_PATHS
            ):
                raise ValueError("本番確認の転送先が固定記事ではありません")
            status = int(response.status_code)
            content_type = str(response.headers.get("Content-Type", "")).lower()
            last_status = f"HTTP {status}"
            if status == 200 and "text/html" in content_type and marker in str(response.text):
                return url
        except ValueError:
            raise
        except Exception as exc:  # network errors are retried until the deployment deadline
            last_status = type(exc).__name__
        if attempt < attempts:
            sleeper(interval)

    raise RuntimeError(f"Workers本番へ最新記事が反映されませんでした: {last_status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=PRODUCTION_URL)
    parser.add_argument("--article", type=Path, default=ARTICLE_PATH)
    parser.add_argument("--attempts", type=int, default=40)
    parser.add_argument("--interval", type=float, default=15)
    args = parser.parse_args(argv)

    fingerprint = read_expected_fingerprint(args.article)
    verified_url = wait_for_production(
        args.url,
        fingerprint,
        attempts=args.attempts,
        interval=args.interval,
    )
    print(f"Workers本番反映を確認しました: {verified_url} ({fingerprint[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
