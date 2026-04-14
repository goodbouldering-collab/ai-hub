"""
全記事から人気・注目度・好み学習を組み合わせてTop10を選ぶ。

スコア計算式:
  final_score = claude_score (0-100)
              + genre_affinity_bonus (好み学習, 0-40)
              + source_affinity_bonus (好み学習, 0-20)
              + freshness_bonus (0-10)
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from .collector import Article


TOP_N = 10


def load_preferences(path: Path) -> dict:
    """
    data/preferences.json の形式:
    {
      "genre_clicks": {"generative_ai": 15, "sns_algo": 3, ...},
      "source_clicks": {"ITmedia AI+": 8, ...},
      "total_clicks": 40,
      "updated_at": "2026-04-11T00:00:00Z"
    }
    """
    if not path.exists():
        return {"genre_clicks": {}, "source_clicks": {}, "total_clicks": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"genre_clicks": {}, "source_clicks": {}, "total_clicks": 0}


def genre_bonus(genre: str, prefs: dict) -> float:
    gc = prefs.get("genre_clicks", {})
    total = prefs.get("total_clicks", 0)
    if total < 5:
        return 0.0
    rate = gc.get(genre, 0) / total
    # 一様分布(1/6=0.167)を基準に、それを上回るジャンルにボーナス
    baseline = 1.0 / 6
    delta = max(0.0, rate - baseline)
    return min(40.0, delta * 200)


def source_bonus(source: str, prefs: dict) -> float:
    sc = prefs.get("source_clicks", {})
    total = prefs.get("total_clicks", 0)
    if total < 5:
        return 0.0
    clicks = sc.get(source, 0)
    return min(20.0, (clicks / max(total, 1)) * 80)


def freshness_bonus(article: Article) -> float:
    if not article.published:
        return 0.0
    try:
        dt = datetime.fromisoformat(article.published.replace("Z", "+00:00"))
    except Exception:
        return 0.0
    now = datetime.now(timezone.utc)
    hours = (now - dt).total_seconds() / 3600
    if hours <= 3:
        return 10.0
    if hours <= 12:
        return 6.0
    if hours <= 24:
        return 3.0
    return 0.0


def rank_articles(
    articles: list[Article],
    summary_map: dict,
    prefs_path: Path,
    top_n: int = TOP_N,
) -> tuple[list[Article], dict[str, dict]]:
    """
    summary_map に final_score / breakdown を書き込み、
    Top N 記事リストを返す。
    """
    prefs = load_preferences(prefs_path)
    scored: list[tuple[float, Article, dict]] = []

    for a in articles:
        info = summary_map.get(a.hash, {})
        base = float(info.get("score", 50))
        gb = genre_bonus(info.get("genre", ""), prefs)
        sb = source_bonus(a.source, prefs)
        fb = freshness_bonus(a)
        final = base + gb + sb + fb
        info["final_score"] = round(final, 1)
        info["breakdown"] = {
            "base": base,
            "genre_bonus": round(gb, 1),
            "source_bonus": round(sb, 1),
            "freshness": round(fb, 1),
        }
        summary_map[a.hash] = info
        scored.append((final, a, info))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [a for _, a, _ in scored[:top_n]]
    return top, summary_map
