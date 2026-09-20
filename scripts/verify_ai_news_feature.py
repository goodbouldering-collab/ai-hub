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
    assert not feature.select(".ai-news-feature__description"), "Intro description must be removed"
    heading = feature.select_one(".ai-news-feature__heading")
    assert heading and heading.select_one("#ai-news-feature-title") and heading.select_one("time"), "Title and update date must share the heading row"
    assert len(feature.select("li")) == 3
    for link in feature.select('li a'):
        assert page.select_one("#" + link["href"].split("#")[1]), "Headline destination missing"
    assert feature.select_one('a.ai-news-feature__more[href="/ai-news/"]')
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
    assert page.select_one(".blog-update-label").get_text() == feature.select_one("time").get_text()
    assert len(page.select(".content-toc")) == 0
    assert page.select_one("#過去のアップデート要約")
    return {"hero_adjacent": True, "home_headlines": 3, "news_items": 5, "blog_removed": True, "date_removed": True, "shared_h2_style": True, "description_removed": True, "date_in_heading": True}


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
