#!/usr/bin/env python3
"""公開中の全実績にURLとサイト画像が出力されたことを検証する。"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "config" / "portfolio.yaml"
OUTPUT = ROOT / "site" / "dist" / "index.html"
STATIC = ROOT / "site" / "static"
DIST = ROOT / "site" / "dist"
MANIFEST = STATIC / "img" / "portfolio" / "manifest.json"


def main() -> int:
    data = yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8")) or {}
    items = [item for item in data.get("portfolio") or [] if str(item.get("status") or "") == "live"]
    output = OUTPUT.read_text(encoding="utf-8")
    errors: list[str] = []
    seen_names: set[str] = set()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    records = manifest.get("screenshots") or {}

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
        if not expected_image.startswith("/img/portfolio/") or not expected_image.endswith(".jpg"):
            errors.append(f"local screenshot missing from portfolio data: {name} -> {expected_image or '(empty)'}")
            continue
        source_image = STATIC / expected_image.lstrip("/")
        built_image = DIST / expected_image.lstrip("/")
        if not source_image.exists() or source_image.stat().st_size < 4_096:
            errors.append(f"source screenshot missing/invalid: {name} -> {source_image}")
        elif source_image.read_bytes()[:2] != b"\xff\xd8":
            errors.append(f"source screenshot is not JPEG: {name} -> {source_image}")
        if not built_image.exists() or built_image.stat().st_size != source_image.stat().st_size:
            errors.append(f"built screenshot missing/stale: {name} -> {built_image}")
        slug = str(item.get("slug") or "").strip()
        record = records.get(slug)
        if not isinstance(record, dict) or record.get("path") != expected_image:
            errors.append(f"screenshot manifest missing/stale: {name} -> {slug}")
        if html.escape(url, quote=True) not in output:
            errors.append(f"URL not rendered: {name} -> {url}")
        if html.escape(expected_image, quote=True) not in output:
            errors.append(f"site image not rendered: {name} -> {expected_image}")

    if "s.wordpress.com/mshots" in output:
        errors.append("external MShots fallback still exists in generated HTML")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"verified {len(items)} live portfolio items with URL and captured screenshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
