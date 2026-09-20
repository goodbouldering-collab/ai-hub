"""Compact public Instagram thumbnails shared by normal and snapshot builds."""
from html import escape
import json
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/instagram.json'
START = '<!-- BEGIN:INSTAGRAM_FEED -->'
END = '<!-- END:INSTAGRAM_FEED -->'
HEAD = ('<link id="instagram-feed-css" rel="stylesheet" href="/instagram-feed.css?v=20260920">'
        '<script id="instagram-feed-js" defer src="/instagram-feed.js?v=20260920"></script>')
def strip_instagram_feed(text):
    text = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', text, flags=re.S)
    return re.sub(r'<link\b[^>]*\bid="instagram-feed-css"[^>]*>|<script\b[^>]*\bid="instagram-feed-js"[^>]*>\s*</script>', '', text)
def render_instagram_feed():
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    username = config['username']
    assert re.fullmatch(r'[a-zA-Z0-9._]+', username)
    assert config['profile_url'] == f'https://www.instagram.com/{username}/'
    cards = []
    for post in config['posts']:
        code, title = post['shortcode'], escape(post['title'])
        assert re.fullmatch(r'[a-zA-Z0-9_-]+', code)
        cards.append(f'<a class="instagram-card" href="https://www.instagram.com/p/{code}/" '
            f'target="_blank" rel="noopener noreferrer" aria-label="Instagram：{title}（新しいタブで開く）">'
            f'<img src="/instagram/{code}.webp" alt="{title}" width="320" height="320" '
            'loading="lazy" decoding="async"></a>')
    return (START + '<section class="instagram-feed" id="instagram" aria-label="Instagramの投稿">'
        '<div class="instagram-track" id="instagram-track" tabindex="0" role="region" '
        'aria-label="Instagramの投稿画像。左右キーでスクロール">' + ''.join(cards) + '</div></section>' + END)
def apply_instagram_feed(text):
    text = strip_instagram_feed(text)
    anchors = [m.start() for m in re.finditer(r'<section\b[^>]*\bid=[\"\']ai-news[\"\']|<div\b[^>]*\bclass=[\"\']diagnosis-guide-row[\"\']', text)]
    if not anchors:
        raise ValueError('Expected homepage news or diagnosis section')
    position = min(anchors)
    text = text[:position] + render_instagram_feed() + text[position:]
    assert text.count('</head>') == 1
    return text.replace('</head>', HEAD + '</head>', 1)
