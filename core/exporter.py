"""
NotebookLM に放り込めるクリーンなテキスト/Markdown を出力する。
- diff モード: 新着のみをハイライトした日次レポート
- full モード: 全ソース統合版 (NotebookLM ソース用)
- top10 JSON: Web サイトが読む構造化データ
"""
from __future__ import annotations
import json
from datetime import date, datetime, timedelta, timezone
import os
from pathlib import Path

from .collector import Article
from .daily_news import normalize_daily_ai_news, normalize_daily_ai_news_item
from .organizer import group_by_category
from .ranker import japan_attention_score


def _japan_today() -> date:
    # JST has no daylight-saving transition, so this works on Windows hosts
    # that do not ship the IANA time-zone database used by zoneinfo.
    return datetime.now(timezone(timedelta(hours=9))).date()


def export_daily_ai_news_snapshot(
    top_articles: list[Article],
    summary_map: dict,
    output_path: Path,
    *,
    today: date | None = None,
) -> Path | None:
    """Atomically publish ten valid candidates, keeping the last good snapshot on failure."""
    items: list[dict[str, object]] = []
    seen_urls: set[str] = set()
    ordered_articles = sorted(
        top_articles,
        key=lambda article: (
            japan_attention_score(summary_map.get(article.hash, {})),
            summary_map.get(article.hash, {}).get("final_score", 0),
        ),
        reverse=True,
    )
    for article in ordered_articles:
        info = summary_map.get(article.hash, {})
        candidate = {
            "title": info.get("title_ja") or article.title,
            "url": article.url,
            "source": article.source,
            "published": article.published or article.fetched_at,
            "plain_summary": info.get("plain_summary", ""),
            "story_example": info.get("story_example", ""),
            "japan_attention": info.get(
                "japan_attention",
                japan_attention_score(info),
            ),
        }
        try:
            clean_candidate = normalize_daily_ai_news_item(candidate)
        except ValueError:
            continue
        if clean_candidate["url"] in seen_urls:
            continue
        seen_urls.add(clean_candidate["url"])
        items.append(clean_candidate)
        if len(items) == 10:
            break

    payload = {
        "date": (today or _japan_today()).isoformat(),
        "items": items,
    }
    try:
        clean = normalize_daily_ai_news(payload)
    except ValueError as exc:
        print(f"[!] 日次AIニュースは前回成功分を維持: {exc}")
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(output_path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(clean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, output_path)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(f"[+] 日次AIニュース公開スナップショット: {output_path}")
    return output_path


def export_top10_json(
    top_articles: list[Article],
    summary_map: dict,
    thumb_map: dict,
    output_path: Path,
) -> Path:
    """build_site.py が読むトップ10のJSON。"""
    date_str = _japan_today().isoformat()
    items = []
    for a in top_articles:
        info = summary_map.get(a.hash, {})
        items.append({
            "hash": a.hash,
            "title": info.get("title_ja") or a.title,
            "orig_title": a.title,
            "summary": info.get("summary", ""),
            "plain_summary": info.get("plain_summary", ""),
            "story_example": info.get("story_example", ""),
            "japan_relevance": info.get("japan_relevance", 0),
            "codex_relevance": info.get("codex_relevance", 0),
            "url": a.url,
            "source": a.source,
            "category": a.category,
            "genre": info.get("genre", "industry"),
            "score": info.get("final_score", 0),
            "breakdown": info.get("breakdown", {}),
            "thumbnail": thumb_map.get(a.hash, ""),
            "published": a.published or "",
        })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"date": date_str, "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[+] Top10 JSON: {output_path}")
    return output_path


def _fmt_article(a: Article, summary_map: dict) -> str:
    info = summary_map.get(a.hash, {})
    summary = info.get("summary", "")
    note = info.get("consul_note", "")

    lines = [
        f"### [{a.source}] {a.title}",
        f"- URL: {a.url}",
        f"- 取得: {a.fetched_at}",
        f"- 公開: {a.published or '(不明)'}",
    ]
    if summary:
        lines.append(f"- 要約: {summary}")
    if note:
        lines.append(f"- コンサル観点: {note}")
    if a.body and not summary:
        body = a.body.replace("\n", " ").strip()
        if len(body) > 300:
            body = body[:300] + "..."
        lines.append(f"- 原文抜粋: {body}")
    return "\n".join(lines) + "\n"


def export_diff_report(
    new_items: list[Article],
    existing_items: list[Article],
    summary_map: dict,
    output_dir: Path,
) -> Path:
    """新着をハイライトした日次ダイジェストを出力。"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(new_items) + len(existing_items)
    lines = [
        f"# AIハブ {date_str}",
        "",
        f"> 生成日時: {time_str}",
        f"> 新着: {len(new_items)}件 / 継続: {len(existing_items)}件 / 合計: {total}件",
        "",
        "---",
        "",
    ]

    if new_items:
        lines.append("## 🆕 新着 (前回取得以降)")
        lines.append("")
        for cat, items in group_by_category(new_items).items():
            lines.append(f"### カテゴリ: {cat} ({len(items)}件)")
            lines.append("")
            for a in items:
                lines.append(_fmt_article(a, summary_map))
        lines.append("---")
        lines.append("")
    else:
        lines.append("## 🆕 新着")
        lines.append("")
        lines.append("前回取得以降、新しい記事はありませんでした。")
        lines.append("")
        lines.append("---")
        lines.append("")

    if existing_items:
        lines.append("## 📚 継続ソース (参照用・一覧のみ)")
        lines.append("")
        for cat, items in group_by_category(existing_items).items():
            lines.append(f"### {cat} ({len(items)}件)")
            for a in items:
                lines.append(f"- [{a.source}] {a.title} — {a.url}")
            lines.append("")

    content = "\n".join(lines)

    dated = output_dir / f"{date_str}.md"
    latest = output_dir / "latest.md"
    dated.write_text(content, encoding="utf-8")
    latest.write_text(content, encoding="utf-8")
    print(f"[+] 日次ダイジェスト: {dated}")
    return dated


def export_nlm_paste(
    articles: list[Article],
    summary_map: dict,
    output_dir: Path,
) -> Path:
    """
    NotebookLM に丸ごと貼り付けるためのシンプルテキスト。
    各記事 = タイトル + 要約1段落 + 出典URL の3行のみ。メタ情報は一切なし。
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# AIハブ {date_str} (過去24時間・AI+SNSアルゴリズム動向)")
    lines.append("")

    grouped = group_by_category(articles)
    for cat, items in grouped.items():
        lines.append(f"## {cat}")
        lines.append("")
        for a in items:
            info = summary_map.get(a.hash, {})
            summary = info.get("summary", "").strip()
            title_ja = info.get("title_ja", "").strip() or a.title
            if not summary:
                body = (a.body or "").replace("\n", " ").strip()
                summary = body[:200] + ("..." if len(body) > 200 else "")
            lines.append(f"### {title_ja}")
            if title_ja != a.title:
                lines.append(f"原題: {a.title}")
            lines.append(summary)
            lines.append(f"出典: {a.url}")
            lines.append("")
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"

    dated = output_dir / f"nlm_{date_str}.txt"
    latest = output_dir / "nlm_latest.txt"
    dated.write_text(content, encoding="utf-8")
    latest.write_text(content, encoding="utf-8")
    print(f"[+] NLM直貼り版: {dated}")
    return dated


def export_full_source(
    all_items: list[Article],
    summary_map: dict,
    output_dir: Path,
) -> Path:
    """全ソースを統合したNotebookLM用の長文テキストを出力。"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# AIハブ 全ソース統合版 {date_str}",
        f"# 生成日時: {time_str}",
        f"# 記事数: {len(all_items)}件",
        "",
        "このファイルは NotebookLM などに丸ごと投入して使うことを想定しています。",
        "",
        "=" * 70,
        "",
    ]

    for cat, items in group_by_category(all_items).items():
        lines.append(f"## カテゴリ: {cat} ({len(items)}件)")
        lines.append("")
        for a in items:
            lines.append(_fmt_article(a, summary_map))
        lines.append("=" * 70)
        lines.append("")

    content = "\n".join(lines)
    out = output_dir / f"{date_str}_full.txt"
    out.write_text(content, encoding="utf-8")
    print(f"[+] 統合版: {out}")
    return out
