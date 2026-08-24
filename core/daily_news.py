"""Validate and render the daily AI news block used by the Codex article."""

from __future__ import annotations

from datetime import date
import html
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REQUIRED_ITEM_FIELDS = (
    "title",
    "url",
    "source",
    "published",
    "plain_summary",
    "story_example",
)


def _clean_text(value: Any, *, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError("ニュース項目は文字列である必要があります")
    cleaned = " ".join(value.split())
    if not cleaned or len(cleaned) > maximum:
        raise ValueError("ニュース項目の文字数が不正です")
    return cleaned


def _clean_url(value: Any) -> str:
    url = _clean_text(value, maximum=500)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("ニュースURLはHTTP(S)である必要があります")
    return url


def normalize_daily_ai_news_item(item: Any) -> dict[str, str]:
    """Validate one candidate so a failed summary can be skipped safely."""
    if not isinstance(item, dict) or any(field not in item for field in REQUIRED_ITEM_FIELDS):
        raise ValueError("日次ニュース項目の必須フィールドが不足しています")
    return {
        "title": _clean_text(item["title"], maximum=140),
        "url": _clean_url(item["url"]),
        "source": _clean_text(item["source"], maximum=100),
        "published": _clean_text(item["published"], maximum=100),
        "plain_summary": _clean_text(item["plain_summary"], maximum=180),
        "story_example": _clean_text(item["story_example"], maximum=180),
    }


def normalize_daily_ai_news(payload: Any) -> dict[str, Any]:
    """Return a compact validated payload or raise without partial output."""
    if not isinstance(payload, dict):
        raise ValueError("日次ニュースはJSONオブジェクトである必要があります")
    date_text = _clean_text(payload.get("date"), maximum=10)
    try:
        date.fromisoformat(date_text)
    except ValueError as exc:
        raise ValueError("日次ニュースの日付が不正です") from exc

    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 10:
        raise ValueError("日次ニュースは10件必要です")

    clean_items: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for item in items:
        clean_item = normalize_daily_ai_news_item(item)
        if clean_item["url"] in seen_urls:
            raise ValueError("日次ニュースURLが重複しています")
        seen_urls.add(clean_item["url"])
        clean_items.append(clean_item)
    return {"date": date_text, "items": clean_items}


def load_daily_ai_news(path: Path) -> dict[str, Any]:
    """Load the last successful snapshot; malformed data stays off the page."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return normalize_daily_ai_news(payload)
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def render_daily_ai_news(payload: dict) -> str:
    """Render ten concise cards. Any invalid item hides the whole block."""
    try:
        clean = normalize_daily_ai_news(payload)
    except ValueError:
        return ""

    news_date = date.fromisoformat(clean["date"])
    date_label = f"{news_date.year}年{news_date.month}月{news_date.day}日"
    parts = [
        "<section class='daily-ai-news' aria-labelledby='daily-ai-news-title'>",
        "<div class='daily-ai-news__header'>",
        "<p class='daily-ai-news__eyebrow'>毎朝更新・仕事の場面から読む</p>",
        "<h2 id='daily-ai-news-title'>今日のAIニュース10</h2>",
        "<p class='daily-ai-news__lead'>むずかしいAIニュースを、何が変わるかと「たとえば」の場面で、わかりやすく10件にしぼりました。</p>",
        f"<p class='daily-ai-news__date'><time datetime='{clean['date']}'>{date_label}</time> 時点</p>",
        "</div><ol class='daily-ai-news__list'>",
    ]
    for rank, item in enumerate(clean["items"], start=1):
        title = html.escape(item["title"])
        url = html.escape(item["url"], quote=True)
        source = html.escape(item["source"])
        plain_summary = html.escape(item["plain_summary"])
        story_example = html.escape(item["story_example"])
        parts.extend(
            [
                "<li class='daily-ai-news__item'>",
                f"<span class='daily-ai-news__rank' aria-hidden='true'>{rank}</span>",
                "<div class='daily-ai-news__copy'>",
                f"<h3><a href='{url}' target='_blank' rel='noopener'>{title}</a></h3>",
                f"<p><strong>わかりやすく</strong>{plain_summary}</p>",
                f"<p class='daily-ai-news__story'><strong>使う場面</strong>{story_example}</p>",
                f"<p class='daily-ai-news__source'>情報元：{source}</p>",
                "</div></li>",
            ]
        )
    parts.extend(
        [
            "</ol>",
            "<p class='daily-ai-news__action'>気になるニュースを1つ選び、「自分ならどこで使うか」を一言で書き出してみてください。</p>",
            "</section>",
        ]
    )
    return "".join(parts)


def prepend_daily_ai_news(meta: dict, body_html: str, payload: dict) -> str:
    if str(meta.get("content_series") or "") != "codex-update-log":
        return body_html
    rendered = render_daily_ai_news(payload)
    return rendered + body_html if rendered else body_html
