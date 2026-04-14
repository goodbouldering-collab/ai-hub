"""
記事をカテゴリ別にグルーピングする。将来的な重複除去・タグ付けの拠点。
"""
from __future__ import annotations
from collections import defaultdict

from .collector import Article


def group_by_category(articles: list[Article]) -> dict[str, list[Article]]:
    groups: dict[str, list[Article]] = defaultdict(list)
    for a in articles:
        groups[a.category].append(a)
    return dict(sorted(groups.items()))
