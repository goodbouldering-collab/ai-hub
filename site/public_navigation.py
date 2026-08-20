"""公開ページのPC・モバイルで共用するメニュー定義。"""
from __future__ import annotations

import html
from typing import Final


PUBLIC_NAV_ITEMS: Final[tuple[tuple[str, str, str], ...]] = (
    ("home", "ホーム", "/#top"),
    ("app-site", "AIアプリサイト", "/ai-app-site/"),
    ("works", "実績", "/#all-works"),
    ("blog", "ブログ", "/#blog"),
    ("lectures", "資料", "/#lectures"),
    ("faq", "FAQ", "/#faq"),
    ("salon", "AIオンラインサロン", "/#seven-day-courses"),
)
ADMIN_NAV_ITEM: Final[tuple[str, str, str]] = ("admin", "管理ページ", "/admin")


def _current_attributes(item_id: str, current_id: str | None) -> tuple[str, str]:
    if item_id == current_id:
        return " nav-current", " aria-current='page'"
    return "", ""


def render_desktop_navigation(current_id: str | None = None) -> str:
    """PC固定ヘッダー用の公開リンクと管理ページリンクを生成する。"""
    parts: list[str] = []
    for item_id, label, href in PUBLIC_NAV_ITEMS:
        current_class, current_attribute = _current_attributes(item_id, current_id)
        salon_class = " nav-salon" if item_id == "salon" else ""
        parts.append(
            "<a class='nav-link nav-essential"
            f"{salon_class}{current_class}' href='{html.escape(href, quote=True)}'"
            f"{current_attribute}>{html.escape(label)}</a>"
        )

    item_id, label, href = ADMIN_NAV_ITEM
    current_class, current_attribute = _current_attributes(item_id, current_id)
    parts.append(
        "<a class='nav-link nav-essential nav-admin"
        f"{current_class}' href='{html.escape(href, quote=True)}'"
        f"{current_attribute}>{html.escape(label)}</a>"
    )
    return "".join(parts)


def render_mobile_navigation(current_id: str | None = None) -> str:
    """ハンバーガーメニュー用の同一公開リンクと管理ページリンクを生成する。"""
    parts = ["<nav class='mobile-public-links' aria-label='公開ページメニュー'>"]
    for item_id, label, href in PUBLIC_NAV_ITEMS:
        _, current_attribute = _current_attributes(item_id, current_id)
        parts.append(
            f"<a href='{html.escape(href, quote=True)}'{current_attribute}>"
            f"<span>{html.escape(label)}</span>"
            "<span class='mobile-link-arrow' aria-hidden='true'>›</span></a>"
        )

    _, label, href = ADMIN_NAV_ITEM
    parts.extend(
        (
            "</nav><div class='mobile-nav-admin'><span class='mobile-nav-label'>管理</span>",
            f"<a class='mobile-admin-link' href='{html.escape(href, quote=True)}'>"
            f"<span class='mobile-admin-link-copy'><strong>{html.escape(label)}</strong>"
            "<small>運営者ログイン</small></span>",
            "<span class='mobile-link-arrow' aria-hidden='true'>›</span></a></div>",
        )
    )
    return "".join(parts)
