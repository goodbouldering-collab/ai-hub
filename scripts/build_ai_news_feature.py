"""Build the standalone news resource and its hero-adjacent home entry.

The templates preserve the verified public layout during the Cloudflare migration.
Use --base-assets only with the immutable release manifest; never use dirty public/.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.course_menu import apply_course_menu
from core.hero_copy import apply_hero_copy
from core.diagnosis_copy import apply_diagnosis_copy
from core.daily_news import normalize_daily_ai_news, render_daily_ai_news
from core.studio_design import decorate_public_tree

TEMPLATES = ROOT / "site/templates/ai-news"
URL = "https://aiclimb.aiclimb.workers.dev/ai-news/"


def remove_old_cards(text: str) -> str:
    return re.sub(r"<a\b[^>]*href=['\"][^'\"]*\bcodex-update-log(?:\.html)?['\"][^>]*>.*?</a>", "", text, flags=re.S)


def apply_compact_style(document: str, css: str) -> str:
    """Replace our own style when tomorrow's shell includes today's release."""
    document = re.sub(r"<style\b[^>]*id=['\"]ai-news-compact-style['\"][^>]*>.*?</style>", "", document, flags=re.S)
    if document.count("</head>") != 1:
        raise ValueError("Expected one document head for the news style")
    return document.replace("</head>", f"<style id='ai-news-compact-style'>{css}</style></head>")


def render_feature(news: dict, label: str) -> str:
    headlines = "".join(
        f'<li><a href="/ai-news/#news-{rank}"><span aria-hidden="true">0{rank}</span>'
        f'<span>{html.escape(item["title"])}</span><b aria-hidden="true">↗</b></a></li>'
        for rank, item in enumerate(news["items"][:3], 1)
    )
    return (
        '<section id="ai-news" class="ai-news-feature" aria-labelledby="ai-news-feature-title">'
        '<div class="ai-news-feature__intro">'
        '<div class="ai-news-feature__heading"><h2 id="ai-news-feature-title">今日のAIニュース5とCodex</h2>'
        f'<time datetime="{news["date"]}">{label}</time></div></div>'
        f'<div class="ai-news-feature__reading"><ol>{headlines}</ol>'
        '<a class="ai-news-feature__more" href="/ai-news/">もっと見る'
        '<b aria-hidden="true">→</b></a></div></section>'
    )


def build(output: Path, base_assets: Path | None = None, *, preserve_baseline_presentation: bool = False) -> dict:
    if preserve_baseline_presentation and base_assets is None:
        raise ValueError("Preserving published presentation requires a verified asset baseline")
    news = normalize_daily_ai_news(json.loads((ROOT / "content/daily-ai-news.json").read_text(encoding="utf-8")))
    raw = (ROOT / "content/ai-news/codex-update-log.md").read_text(encoding="utf-8")
    _, header, body = raw.split("---", 2)
    meta = yaml.safe_load(header)
    modified = max(news["date"], str(meta["date_modified"]))
    updated = date.fromisoformat(modified)
    label = f"{updated.month}月{updated.day}日更新"
    news_html = render_daily_ai_news(news)
    for rank in range(1, 6):
        news_html = news_html.replace("<li class='daily-ai-news__item", f"<li id='news-{rank}' class='daily-ai-news__item", 1)
    # The research window belongs to the dated JSON, not the page template.
    original_news = json.loads((ROOT / "content/daily-ai-news.json").read_text(encoding="utf-8"))
    note = original_news.get("research_note", "")
    if note:
        marker = "</div><ol class='daily-ai-news__list'>"
        news_html = news_html.replace(marker, "<details class='ai-news-research'><summary>調査範囲・出典について</summary>"
                                      f"<p>{html.escape(note)}</p></details>" + marker)
    codex_html = markdown.markdown(body, extensions=["extra", "sane_lists", "attr_list"])
    codex_html = codex_html.replace("<h2>過去のアップデート要約</h2>", "<h2 id='過去のアップデート要約'>過去のアップデート要約</h2>")
    article = (TEMPLATES / "page.html").read_text(encoding="utf-8")
    article = article.replace("{{NEWS_AND_CODEX}}", news_html + codex_html).replace("{{UPDATE_LABEL}}", label).replace("{{UPDATE_DATE}}", modified)
    compact_css = (TEMPLATES / "compact.css").read_text(encoding="utf-8")
    article = apply_compact_style(article, compact_css)
    assert "{{" not in article, "Unfilled article template"
    home = (TEMPLATES / "home.html").read_text(encoding="utf-8")
    if "{{AI_NEWS_FEATURE}}" in home:
        assert home.count("{{AI_NEWS_FEATURE}}") == 1
        home = home.replace("{{AI_NEWS_FEATURE}}", render_feature(news, label))
    else:
        home, count = re.subn(r"<section\b[^>]*class=['\"][^'\"]*codex-update-guide[^'\"]*['\"][^>]*>.*?</section>", "", home, flags=re.S)
        assert count == 1, "Expected one old news banner"
        home = remove_old_cards(home)
        hero = re.search(r"<section\b[^>]*id=['\"]top['\"][^>]*>.*?</section>", home, re.S)
        assert hero, "Hero not found"
        home = home[:hero.end()] + render_feature(news, label) + home[hero.end():]
        css = (TEMPLATES / "feature.css").read_text(encoding="utf-8")
        home = home.replace("</head>", f"<style id='ai-news-feature-style'>{css}</style></head>")
    home = apply_diagnosis_copy(apply_hero_copy(apply_course_menu(apply_compact_style(home, compact_css))))
    blog = remove_old_cards((TEMPLATES / "blog.html").read_text(encoding="utf-8"))
    sitemap = (TEMPLATES / "sitemap.xml").read_text(encoding="utf-8")
    sitemap, count = re.subn(r"<url><loc>[^<]*/blog/codex-update-log\.html</loc>.*?</url>", f"<url><loc>{URL}</loc><lastmod>{modified}</lastmod><priority>0.9</priority></url>", sitemap, flags=re.S)
    assert count == 1
    results = {"index.html": home, "ai-news/index.html": article, "blog/index.html": blog, "sitemap.xml": sitemap,
               "_redirects": "/blog/codex-update-log /ai-news/ 301\n/blog/codex-update-log.html /ai-news/ 301\n/blog/codex-update-log/ /ai-news/ 301\n"}
    if base_assets:
        manifest = json.loads((ROOT / "content/ai-news/release-baseline.json").read_text(encoding="utf-8"))["assets"]
        actual = {p.relative_to(base_assets).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in base_assets.rglob("*") if p.is_file()}
        assert actual == manifest, "Published asset baseline differs; stop instead of mixing changes"
        assert not output.exists(), "Release output must be a fresh directory"
        shutil.copytree(base_assets, output)
    for name, value in results.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        line_ending = "\r\n" if preserve_baseline_presentation and b"\r\n" in (base_assets / name).read_bytes() else "\n"
        target.write_text(value, encoding="utf-8", newline=line_ending)
    # Keep the old file in the immutable baseline; _redirects takes priority.
    # Daily content updates can retain the exact already-published theme.
    # A separate design release still uses the current decorator by default.
    themed = [] if preserve_baseline_presentation else decorate_public_tree(output)
    if preserve_baseline_presentation:
        changed = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()
                   and hashlib.sha256(p.read_bytes()).hexdigest() != manifest.get(p.relative_to(output).as_posix())}
        assert changed <= set(results), f"Unexpected public changes: {sorted(changed - set(results))}"
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    return {"source_sha": sha, "url": URL, "news_date": news["date"], "codex_fingerprint": meta["source_fingerprint"],
            "themed_documents": len(themed),
            "files": {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in results}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--base-assets", type=Path)
    parser.add_argument("--preserve-baseline-presentation", action="store_true", help="Keep the verified live theme for a content-only release")
    args = parser.parse_args()
    print(json.dumps(build(args.output.resolve(), args.base_assets.resolve() if args.base_assets else None, preserve_baseline_presentation=args.preserve_baseline_presentation), ensure_ascii=False, indent=2))
