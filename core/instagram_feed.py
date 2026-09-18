"""A small, public Instagram carousel shared by normal and snapshot builds."""
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/instagram.json"
START = "<!-- BEGIN:INSTAGRAM_FEED -->"
END = "<!-- END:INSTAGRAM_FEED -->"
HEAD = ('<link id="instagram-feed-css" rel="stylesheet" href="/instagram-feed.css?v=20260919">'
        '<script id="instagram-feed-js" defer src="/instagram-feed.js?v=20260919"></script>')


def render_instagram_feed() -> str:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    username = config["username"]
    assert re.fullmatch(r"[a-zA-Z0-9._]+", username)
    profile = f"https://www.instagram.com/{username}/"
    assert config["profile_url"] == profile
    cards = []
    for index, post in enumerate(config["posts"], 1):
        code, title = post["shortcode"], escape(post["title"])
        assert re.fullmatch(r"[a-zA-Z0-9_-]+", code)
        url = f"https://www.instagram.com/p/{code}/"
        cards.append(
            f'<article class="instagram-card" aria-label="投稿 {index} / {len(config["posts"])}">'
            f'<div class="instagram-card-heading"><span>{index:02d}</span><h3>{title}</h3></div>'
            f'<iframe class="instagram-frame" src="{url}embed/" '
            f'title="@{escape(username)}のInstagram投稿：{title}" width="360" height="540" '
            'loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
            'allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>'
            f'<a class="instagram-post-link" href="{url}" target="_blank" rel="noopener noreferrer">'
            'Instagramで投稿を見る <span aria-hidden="true">↗</span></a></article>'
        )
    return (
        START + '<section class="instagram-feed" id="instagram" aria-labelledby="instagram-title">'
        '<div class="instagram-feed-heading"><div><p class="instagram-eyebrow">INSTAGRAM</p>'
        '<h2 id="instagram-title">日々の実践を、Instagramで。</h2>'
        '<p class="instagram-description">AIの工夫、地域のこと、日々の気づき。</p></div>'
        f'<a class="instagram-profile-link" href="{profile}" target="_blank" rel="noopener noreferrer">'
        f'@{escape(username)} <span aria-hidden="true">↗</span></a></div>'
        '<div class="instagram-toolbar"><p id="instagram-swipe-hint">左右にスワイプして投稿を見る</p>'
        '<div class="instagram-controls" hidden><button type="button" data-instagram-prev '
        'aria-label="前のInstagram投稿" aria-controls="instagram-track">←</button>'
        f'<span data-instagram-position aria-live="polite" aria-atomic="true">1 / {len(cards)}</span>'
        '<button type="button" data-instagram-next aria-label="次のInstagram投稿" '
        'aria-controls="instagram-track">→</button></div></div>'
        '<div class="instagram-track" id="instagram-track" tabindex="0" role="region" '
        'aria-label="Instagramの投稿一覧" aria-describedby="instagram-swipe-hint">'
        + ''.join(cards) + '</div></section>' + END
    )


def apply_instagram_feed(text: str) -> str:
    """Insert before news/diagnosis, preserving every byte outside our own markup."""
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), "", text, flags=re.S)
    text = text.replace(HEAD, "")
    anchors = [match.start() for match in re.finditer(
        r'<section\b[^>]*\bid=[\"\']ai-news[\"\']|<div\b[^>]*\bclass=[\"\']diagnosis-guide-row[\"\']', text)]
    if not anchors:
        raise ValueError("Expected the homepage news or diagnosis section after the hero")
    position = min(anchors)
    text = text[:position] + render_instagram_feed() + text[position:]
    assert text.count("</head>") == 1
    return text.replace("</head>", HEAD + "</head>", 1)
