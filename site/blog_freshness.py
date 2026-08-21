"""ブログの公開日・更新日とNEW表示を一か所で判定する。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Mapping


BLOG_NEW_WINDOW_DAYS = 7
JAPAN_TIMEZONE = timezone(timedelta(hours=9))


def _parse_date(value: object) -> date | None:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(JAPAN_TIMEZONE).date()
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(JAPAN_TIMEZONE)
        return parsed.date()


def _reference_date(today: date | None) -> date:
    return today or datetime.now(JAPAN_TIMEZONE).date()


def _effective_date_and_action(
    meta: Mapping[str, object],
    *,
    today: date | None = None,
) -> tuple[date | None, str]:
    reference_date = _reference_date(today)
    modified = _parse_date(meta.get("date_modified"))
    if modified is not None and modified <= reference_date:
        return modified, "更新"
    published = _parse_date(meta.get("date"))
    if published is not None and published <= reference_date:
        return published, "公開"
    return None, ""


def effective_blog_date(
    meta: Mapping[str, object],
    *,
    today: date | None = None,
) -> date | None:
    """有効な更新日を優先し、無効・未来なら公開日へ戻す。"""
    effective_date, _ = _effective_date_and_action(meta, today=today)
    return effective_date


def is_new_blog(
    meta: Mapping[str, object],
    *,
    today: date | None = None,
) -> bool:
    """公開・更新から7日以内の記事だけをNEW扱いにする。"""
    reference_date = _reference_date(today)
    effective_date = effective_blog_date(meta, today=reference_date)
    if effective_date is None:
        return False
    age_days = (reference_date - effective_date).days
    return 0 <= age_days <= BLOG_NEW_WINDOW_DAYS


def blog_date_label(
    meta: Mapping[str, object],
    *,
    today: date | None = None,
) -> str:
    """公開と更新を区別した短い日付表記を返す。"""
    effective_date, action = _effective_date_and_action(meta, today=today)
    if effective_date is None:
        return ""
    return f"{effective_date.month}月{effective_date.day}日{action}"
