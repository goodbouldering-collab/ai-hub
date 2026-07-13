#!/usr/bin/env python3
"""公開中の全実績にURLとサイト画像が出力されたことを検証する。"""

from __future__ import annotations

import html
import sys
from pathlib import Path
from urllib.parse import quote

import yaml


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "config" / "portfolio.yaml"
OUTPUT = ROOT / "site" / "dist" / "index.html"


def main() -> int:
    data = yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8")) or {}
    items = [item for item in data.get("portfolio") or [] if str(item.get("status") or "") == "live"]
    output = OUTPUT.read_text(encoding="utf-8")
    errors: list[str] = []
    seen_names: set[str] = set()

    for item in items:
        name = str(item.get("name") or "").strip()
        url = str(item.get("url") or "").strip()
        if not name or not url:
            errors.append(f"missing name/url: {item}")
            continue
        normalized_name = "".join(name.casefold().split())
        if normalized_name in seen_names:
            errors.append(f"duplicate name: {name}")
        seen_names.add(normalized_name)
        expected_image = str(item.get("thumbnail") or "").strip()
        if not expected_image:
            expected_image = "https://s.wordpress.com/mshots/v1/" + quote(url, safe="") + "?w=960"
        if html.escape(url, quote=True) not in output:
            errors.append(f"URL not rendered: {name} -> {url}")
        if html.escape(expected_image, quote=True) not in output:
            errors.append(f"site image not rendered: {name} -> {expected_image}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"verified {len(items)} live portfolio items with URL and site image")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
