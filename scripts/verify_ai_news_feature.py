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
    assert hero.find_next_sibling() == feature, "News entry must immediately follow the hero"
    assert feature.select_one('#ai-news-feature-title').get_text() == '今日のAIニュース5とCodex'
    headlines = feature.select('ol li a')
    assert len(headlines) == 3
    for rank, link in enumerate(headlines, 1):
        assert link['href'] == f'/ai-news/#news-{rank}'
        assert link.select('span')[-1].get_text() == page.select_one(f'#news-{rank} h3 a').get_text()
    rows = home.select('#blog .editorial-feed__row')
    assert len(rows) == 3, "Home must retain the latest three blog articles"
    assert feature.find_next_sibling()['id'] == 'blog'
    assert all(row.select_one('img[src][alt]') for row in rows)
    assert len(home.select('#blog')) == 1
    assert home.select_one('#blog.editorial-feed--home')
    assert not home.select('#blog a[href="/ai-news/"]')
    assert not home.select('#blog-carousel, #latest-blog')
    assert not feature.select('section'), "Daily refresh must not truncate a nested section"
    expected = sorted(blog.select('a.tr-card'), key=lambda card: card.select_one('time')['datetime'], reverse=True)[:3]
    for link, card in zip(rows, expected):
        assert link['href'] == urljoin('/blog/', card['href'])
        assert link.select_one('.tr-title').get_text() == card.select_one('.tr-title').get_text()
        assert link.select_one('time')['datetime'] == card.select_one('time')['datetime']
    more = feature.select_one('a.ai-news-feature__more[href="/ai-news/"]')
    assert more and 'もっと見る' in more.get_text()
    assert not blog.select('.editorial-feed__news, a[href="/ai-news/"]')
    assert all(row.select_one('img[src][alt]') for row in blog.select('.editorial-feed__row'))
    assert len(blog.select('.editorial-feed__row')) == len(blog.select('a.tr-card'))
    assert len(home.select('.compact-course-card[data-editorial-course]')) == 6
    for card in home.select('.compact-course-card'):
        assert card.select_one('.editorial-course-lead .compact-course-meta strong')
        assert card.select_one(':scope > .studio-course-body .compact-course-tail')
    assert not any('/soft-' in img.get('src', '') or '/lesson-' in img.get('src', '') for img in home.select('img'))
    assert not home.select('a[href*="/blog/codex-update-log"]')
    assert not blog.select('a[href*="codex-update-log"]')
    assert "/blog/codex-update-log" not in sitemap
    assert "https://aiclimb.aiclimb.workers.dev/ai-news/" in sitemap
    assert page.select_one('link[rel="canonical"]')["href"] == "https://aiclimb.aiclimb.workers.dev/ai-news/"
    assert len(page.select(".daily-ai-news__item")) == 5
    assert not page.select_one("main > header .speaker-meta")
    assert page.select_one("#codex-update-guide-title").get_text() == "Codex新機能と活用例"
    assert ".codex-update-guide #codex-update-guide-title," in str(page)
    assert not page.select_one("a[aria-current='page'][href='/#blog']")
    from datetime import date
    updated = date.fromisoformat(feature.select_one('time')['datetime'])
    assert page.select_one(".blog-update-label").get_text() == f"{updated.month}月{updated.day}日更新"
    assert len(page.select(".content-toc")) == 0
    assert page.select_one("#過去のアップデート要約")
    return {"hero_adjacent": True, "home_entries": 3, "news_items": 5,
            "latest_blogs": 3, "archive_entries": len(blog.select('.editorial-feed__row')),
            "all_entries_have_images": True, "compact_courses": 6,
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
