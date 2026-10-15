"""Verify the standalone resource, category removal and persistent home entry."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


def verify(read):
    home = BeautifulSoup(read("index.html"), "html.parser")
    page = BeautifulSoup(read("ai-news/index.html"), "html.parser")
    blog = BeautifulSoup(read("blog/index.html"), "html.parser")
    sitemap = read("sitemap.xml")
    hero = home.select_one("main #top")
    feature = home.select_one("main #ai-news")
    diagnoses = home.select_one('#diagnosis-start')
    assert diagnoses and hero.select_one("#diagnosis-start") == diagnoses, "Diagnoses must be inside the hero"
    assert home.select_one("#blog > .editorial-feed__heading + .editorial-feed__list > #ai-news"), "Combined news must be the first blog entry"
    assert hero.select_one('#hero-glass-art img'), "Preserve the current glass hero"
    assert not home.select('.home-learning-links, #restored-hero-image')
    assert hero.select_one(".focus-lead + .focus-trust + .focus-actions"), "Trust points must follow the lead"
    assert [a['href'] for a in diagnoses.select(':scope > a')] == ['/seo-llmo-diagnosis/', '/ai-agent-readiness/']
    assert len(diagnoses.select(':scope > .diagnosis-action')) == 3
    assert diagnoses.select_one('button.diagnose-open[aria-controls="diagnoseModal"]')
    assert feature.select_one('.tr-title').get_text() == '今日のAIニュース4とCodex'
    assert feature.select_one('a')['href'] == '/ai-news/'
    news_image = feature.select_one('img[src][alt]')
    assert news_image, 'Preserve the published normal-article news image'
    rows = home.select('#blog .editorial-feed__row:not(.editorial-feed__news)')
    assert len(rows) == 3, 'Preserve the latest three blog articles'
    assert len(home.select('#blog .editorial-feed__row')) == 4
    assert all(row.select_one('img[src][alt]') for row in rows)
    assert len(home.select('#blog')) == 1
    assert home.select_one('#blog.editorial-feed--home')
    assert home.select('#blog a[href="/ai-news/"]')
    assert not home.select('#blog-carousel, #latest-blog')
    assert not feature.select('section'), "Daily refresh must not truncate a nested section"
    expected = sorted(blog.select('a.tr-card'), key=lambda card: card.select_one('time')['datetime'], reverse=True)[:3]
    for link, card in zip(rows, expected):
        assert link['href'] == urljoin('/blog/', card['href'])
        assert link.select_one('.tr-title').get_text() == card.select_one('.tr-title').get_text()
        assert link.select_one('time')['datetime'] == card.select_one('time')['datetime']
    assert len(blog.select('.editorial-feed__news')) == 1
    assert blog.select_one(".tr-grid > li:first-child a")["href"] == "/ai-news/"
    assert all(row.select_one('img[src][alt]') for row in blog.select('.editorial-feed__row:not(.editorial-feed__news)'))
    assert len(blog.select('.editorial-feed__row')) == len(blog.select('a.tr-card')) + 1
    assert len(home.select('.compact-course-card[data-editorial-course]')) == 7
    assert home.select_one('#reel-course'), "Preserve the published reel course"
    for card in home.select('.compact-course-card'):
        assert card.select_one('.editorial-course-lead .compact-course-meta strong')
        assert card.select_one(':scope > .studio-course-body .compact-course-tail')
    assert not any('/soft-' in img.get('src', '') or '/lesson-' in img.get('src', '') for img in home.select('img'))
    assert not home.select('a[href*="/blog/codex-update-log"]')
    assert not blog.select('a[href*="codex-update-log"]')
    assert "/blog/codex-update-log" not in sitemap
    assert "https://aiclimb.aiclimb.workers.dev/ai-news/" in sitemap
    assert page.select_one('link[rel="canonical"]')["href"] == "https://aiclimb.aiclimb.workers.dev/ai-news/"
    assert len(page.select(".daily-ai-news__item")) == 4
    assert not page.select('main img, .news-thumbnail')
    archive_image = blog.select_one('.editorial-feed__news img[src][alt]')
    assert archive_image and archive_image['src'] == news_image['src'], 'Home and archive news images must match'
    assert not page.select_one("main > header .speaker-meta")
    assert page.select_one("#codex-update-guide-title").get_text() == "Codex新機能と活用例"
    assert ".codex-update-guide #codex-update-guide-title," in str(page)
    assert not page.select_one("a[aria-current='page'][href='/#blog']")
    from datetime import date
    updated = date.fromisoformat(feature.select_one('time')['datetime'])
    assert page.select_one(".blog-update-label").get_text() == f"{updated.month}月{updated.day}日更新"
    assert len(page.select(".content-toc")) == 0
    assert page.select_one("#過去のアップデート要約")
    return {"diagnoses_in_hero": True, "news_pinned_in_blog": True, "home_entries": 4, "news_items": 4,
            "latest_blogs": 3, "archive_entries": len(blog.select('.editorial-feed__row')),
            "ordinary_blog_images_preserved": True, "news_and_codex_images": False, "news_entry_images_preserved": True, "compact_courses": 7,
            "codex_blog_card_removed": True, "article_content_checks": True}



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--assets", type=Path)
    group.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.assets:
        print(json.dumps(verify(lambda name: (args.assets / name).read_text(encoding="utf-8")), indent=2))
    else:
        base = "https://aiclimb.aiclimb.workers.dev/"
        paths = {"index.html": "", "ai-news/index.html": "ai-news/", "blog/index.html": "blog/"}
        def read(name):
            response = requests.get(urljoin(base, paths.get(name, name)), timeout=45)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        results = verify(read)
        results["redirects"] = {}
        for path in ("blog/codex-update-log", "blog/codex-update-log.html", "blog/codex-update-log/"):
            response = requests.get(urljoin(base, path), allow_redirects=False, timeout=30)
            assert response.status_code == 301, (path, response.status_code)
            assert urljoin(base, response.headers["location"]) == urljoin(base, "ai-news/")
            results["redirects"][path] = response.status_code
        results["routes"] = {}
        for path, status in (("health", 200), ("blog/2026-08-30-switchbot-ai-mind-clip.html", 200), ("admin", 200), ("api/admin/ping", 401)):
            response = requests.get(urljoin(base, path), timeout=45)
            assert response.status_code == status, (path, response.status_code)
            results["routes"][path] = response.status_code
        print(json.dumps(results, ensure_ascii=False, indent=2))
