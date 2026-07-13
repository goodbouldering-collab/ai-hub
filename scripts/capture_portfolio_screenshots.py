#!/usr/bin/env python3
"""公開中の実績サイトを撮影し、カード用の最新画像として保存する。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import Browser, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "config" / "portfolio.yaml"
SCREENSHOT_DIR = ROOT / "site" / "static" / "img" / "portfolio"
MANIFEST = SCREENSHOT_DIR / "manifest.json"
PUBLIC_PREFIX = "/img/portfolio"


def safe_slug(value: Any) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().casefold()).strip("-")
    if slug:
        return slug
    digest = hashlib.sha256(str(value or "portfolio").encode("utf-8")).hexdigest()[:12]
    return f"site-{digest}"


def screenshot_path(item: dict[str, Any]) -> tuple[Path, str]:
    slug = safe_slug(item.get("slug") or item.get("source_project") or item.get("name"))
    filename = f"{slug}.jpg"
    return SCREENSHOT_DIR / filename, f"{PUBLIC_PREFIX}/{filename}"


def normalize_url(value: Any) -> str:
    return str(value or "").strip().rstrip("/")


def selected_items(items: list[dict[str, Any]], only_url: str = "") -> list[dict[str, Any]]:
    live = [item for item in items if str(item.get("status") or "") == "live"]
    target = normalize_url(only_url)
    if not target:
        return live
    return [item for item in live if normalize_url(item.get("url")) == target]


def load_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {"screenshots": {}}
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"screenshots": {}}
    except (OSError, json.JSONDecodeError):
        return {"screenshots": {}}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dismiss_common_overlays(page: Any) -> None:
    """サイト本体を隠す一般的な同意・閉じるボタンだけを控えめに処理する。"""
    button_name = re.compile(
        r"^(?:×|✕|close|閉じる|同意する|すべて同意|すべて許可|accept|accept all)$",
        re.IGNORECASE,
    )
    try:
        page.keyboard.press("Escape")
    except PlaywrightError:
        pass
    try:
        page.evaluate(
            """() => {
                const vw = window.innerWidth;
                const vh = window.innerHeight;
                const modalName = /(modal|popup|overlay|lightbox|coupon)/i;
                for (const el of document.querySelectorAll('body *')) {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    const z = Number.parseInt(style.zIndex, 10) || 0;
                    const name = `${el.id || ''} ${String(el.className || '')}`;
                    const largeFixed = style.position === 'fixed'
                        && rect.width * rect.height >= vw * vh * 0.45
                        && z >= 1000;
                    const namedModal = modalName.test(name)
                        && (style.position === 'fixed' || z >= 1000)
                        && rect.width * rect.height >= vw * vh * 0.08;
                    if (largeFixed || namedModal || el.getAttribute('aria-modal') === 'true') {
                        el.style.setProperty('display', 'none', 'important');
                    }
                }
            }"""
        )
    except PlaywrightError:
        pass
    try:
        buttons = page.get_by_role("button", name=button_name)
        for index in range(min(buttons.count(), 5)):
            button = buttons.nth(index)
            if button.is_visible():
                button.click(timeout=1_500)
                page.wait_for_timeout(250)
    except PlaywrightError:
        pass
    try:
        close_elements = page.locator(
            "button, [role='button'], a, [class*='close' i]"
        ).filter(has_text=re.compile(r"^\s*(?:×|✕)\s*$"))
        for index in range(min(close_elements.count(), 5)):
            element = close_elements.nth(index)
            if element.is_visible():
                element.click(timeout=1_500, force=True)
                page.wait_for_timeout(250)
    except PlaywrightError:
        pass


def capture_one(
    browser: Browser,
    item: dict[str, Any],
    destination: Path,
    *,
    width: int,
    height: int,
    quality: int,
    timeout_ms: int,
    settle_ms: int,
) -> None:
    url = normalize_url(item.get("url"))
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=1,
        locale="ja-JP",
        color_scheme="light",
        ignore_https_errors=False,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 "
            "AI-Consult-Portfolio-Screenshot/1.0"
        ),
    )
    page = context.new_page()
    page.on("dialog", lambda dialog: dialog.dismiss())
    if "goodbouldering.com" in url:
        page.route("**/welcome-coupon.colorme.app/**", lambda route: route.abort())
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        if response is not None and response.status >= 400:
            raise RuntimeError(f"HTTP {response.status}")
        try:
            page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 8_000))
        except PlaywrightTimeoutError:
            pass
        page.evaluate("document.fonts && document.fonts.ready")
        page.wait_for_timeout(settle_ms)
        dismiss_common_overlays(page)
        page.add_style_tag(
            content=(
                "*,*::before,*::after{animation:none!important;transition:none!important;}"
                "html{scroll-behavior:auto!important;}"
            )
        )
        page.evaluate("window.scrollTo(0, 0)")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=f".{destination.stem}-", suffix=".jpg", dir=destination.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
        try:
            page.screenshot(
                path=str(temporary),
                type="jpeg",
                quality=quality,
                full_page=False,
                animations="disabled",
                caret="hide",
                scale="css",
            )
            if temporary.stat().st_size < 4_096:
                raise RuntimeError(f"screenshot too small: {temporary.stat().st_size} bytes")
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
    finally:
        context.close()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--only-url", default="", help="公開完了フックで指定されたURLだけを撮影")
    result.add_argument("--width", type=int, default=1280)
    result.add_argument("--height", type=int, default=720)
    result.add_argument("--quality", type=int, default=72)
    result.add_argument("--timeout-seconds", type=float, default=30.0)
    result.add_argument("--settle-ms", type=int, default=2_500)
    result.add_argument("--channel", default="", help="ローカル確認用。例: chrome")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    data = yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8")) or {}
    items = data.get("portfolio") or []
    targets = selected_items(items, args.only_url)
    if args.only_url and not targets:
        print(f"ERROR: live portfolio URL not found: {args.only_url}", file=sys.stderr)
        return 1
    if not targets:
        print("ERROR: no live portfolio items", file=sys.stderr)
        return 1

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    records = manifest.get("screenshots")
    if not isinstance(records, dict):
        records = {}
    failures: list[str] = []
    now = datetime.now(timezone.utc).isoformat()

    launch_options: dict[str, Any] = {"headless": True}
    if args.channel:
        launch_options["channel"] = args.channel

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_options)
        try:
            for item in targets:
                name = str(item.get("name") or item.get("slug") or "site")
                destination, public_path = screenshot_path(item)
                url = normalize_url(item.get("url"))
                try:
                    capture_one(
                        browser,
                        item,
                        destination,
                        width=args.width,
                        height=args.height,
                        quality=args.quality,
                        timeout_ms=int(args.timeout_seconds * 1_000),
                        settle_ms=args.settle_ms,
                    )
                    item["thumbnail"] = public_path
                    records[safe_slug(item.get("slug") or item.get("name"))] = {
                        "name": name,
                        "url": url,
                        "path": public_path,
                        "captured_at": now,
                        "sha256": sha256_file(destination),
                        "bytes": destination.stat().st_size,
                        "width": args.width,
                        "height": args.height,
                        "status": "captured",
                    }
                    print(f"captured: {name} -> {public_path} ({destination.stat().st_size} bytes)")
                except (PlaywrightError, OSError, RuntimeError) as exc:
                    if destination.exists() and destination.stat().st_size >= 4_096:
                        item["thumbnail"] = public_path
                        previous = records.get(safe_slug(item.get("slug") or item.get("name")), {})
                        if not isinstance(previous, dict):
                            previous = {}
                        records[safe_slug(item.get("slug") or item.get("name"))] = {
                            **previous,
                            "name": name,
                            "url": url,
                            "path": public_path,
                            "status": "retained",
                            "last_error": str(exc),
                            "last_attempt_at": now,
                        }
                        print(f"retained previous image: {name}: {exc}", file=sys.stderr)
                    else:
                        failures.append(f"{name}: {exc}")
        finally:
            browser.close()

    manifest = {
        "generated_at": now,
        "viewport": {"width": args.width, "height": args.height},
        "screenshots": dict(sorted(records.items())),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PORTFOLIO.write_text(
        "# AI相談 — 実績サイト\n"
        "# scripts/sync_portfolio.py が Vercel の公開サイトと手動登録フックを統合する正本。\n"
        "# 同名・同slug・同URL・同Vercel project IDは1件へ統合し、旧URLは aliases に残す。\n"
        "# status: live の項目だけが公開トップ「すべての実績」に表示される。\n\n"
        + yaml.safe_dump({"portfolio": items}, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )

    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"portfolio screenshots ready: {len(targets)} target(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
