"""Maintain the approved home feed with current published articles."""
from datetime import date
from html import escape
from html.parser import HTMLParser
import re
import json
from pathlib import Path
import yaml

BLOG_DIR = Path(__file__).resolve().parents[1] / "content/blog"


class _BlogCards(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.posts = []
        self.card = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'a' and 'tr-card' in classes:
            self.card = {'href': attrs.get('href', ''), 'title': '', 'date': '', 'summary': ''}
        if self.card is not None:
            if 'tr-title' in classes:
                self.field = 'title'
            elif 'tr-date' in classes:
                self.field = 'date'
            elif 'tr-sum' in classes:
                self.field = 'summary'

    def handle_data(self, data):
        if self.card is not None and self.field:
            self.card[self.field] += data

    def handle_endtag(self, tag):
        if tag == 'div':
            self.field = None
        if tag == 'a' and self.card is not None:
            self.posts.append(self.card)
            self.card = None
            self.field = None


def published_posts(blog_index):
    """Use the public index, so an unpublished Markdown draft cannot appear."""
    parser = _BlogCards()
    parser.feed(blog_index)
    posts = {}
    for card in parser.posts:
        match = re.fullmatch(r'(?:\./|/blog/)([a-z0-9-]+)\.html', card['href'])
        if not match or match[1] == 'codex-update-log':
            continue
        title, published = card['title'].strip(), card['date'].strip()
        if not title:
            raise ValueError('Published blog card has no title')
        date.fromisoformat(published)
        href = f'/blog/{match[1]}.html'
        posts[href] = {'href': href, 'title': title, 'date': published, 'summary': card['summary'].strip()}
    return sorted(posts.values(), key=lambda post: (post['date'], post['href']), reverse=True)


def latest_published_posts(blog_index):
    latest = [{k: p[k] for k in ('href', 'title', 'date')} for p in published_posts(blog_index)[:2]]
    if len(latest) != 2:
        raise ValueError('Expected at least two publicly listed blog posts')
    return latest


def apply_home_updates(document, blog_index, css):
    """Keep the approved image feed and compact menu on daily regeneration."""
    from core.editorial_feed import apply_home_feed, public_posts
    from core.editorial_home import apply_editorial_home
    templates = Path(__file__).resolve().parents[1] / 'site/templates/ai-news'
    style = f'<style id="home-updates-style">{css}</style>'
    pattern = r'<style\b[^>]*id=[\x27"]home-updates-style[\x27"][^>]*>.*?</style>'
    if re.search(pattern, document, re.S):
        document = re.sub(pattern, lambda _: style, document, flags=re.S)
    else:
        document = document.replace('</head>', style + '</head>')
    document = apply_home_feed(document, public_posts(blog_index), (templates / 'editorial-feed.css').read_text(encoding='utf-8'))
    return apply_editorial_home(document)


def render_home_blog_list(blog_index):
    """Render the original seven-card layout, excluding unpublished local drafts."""
    cards = []
    catalog_path = BLOG_DIR.parents[1] / 'config/home-blog-images.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8')) if catalog_path.is_file() else {}
    for post in published_posts(blog_index)[:7]:
        source = BLOG_DIR / (Path(post['href']).stem + '.md')
        image = catalog.get(source.stem, '')
        if source.is_file():
            raw = source.read_text(encoding='utf-8')
            parts = raw.split('---', 2)
            if raw.startswith('---') and len(parts) == 3:
                image = str((yaml.safe_load(parts[1]) or {}).get('image') or image)
        media = ''
        if image.startswith('/img/') and '..' not in image:
            media = f"<div class='blog-card-media'><img src='{escape(image, quote=True)}' alt='' loading='lazy' decoding='async'></div>"
        cards.append(
            f"<a class='blog-card' href='{escape(post['href'], quote=True)}'>{media}"
            f"<div class='blog-card-body'><div class='blog-card-meta'><span>{post['date']}</span></div>"
            f"<div class='blog-card-title-row'><h3>{escape(post['title'])}</h3></div>"
            f"<p>{escape(post['summary'])}</p><span class='blog-card-more'>読む</span></div></a>"
        )
    return (
        "<section class='focus-block' id='blog'><div class='focus-section-head'><small>PRACTICAL BLOG</small><h2>ブログ</h2></div>"
        "<div class='pf-carousel-wrap blog-carousel-wrap focus-blog-carousel'>"
        "<button type='button' class='pf-arrow pf-prev' aria-label='前へ' data-dir='-1'>‹</button>"
        "<div class='pf-carousel blog-carousel' id='blog-carousel'>" + ''.join(cards) + "</div>"
        "<button type='button' class='pf-arrow pf-next' aria-label='次へ' data-dir='1'>›</button></div>"
        "<div class='focus-content-actions'><a class='focus-btn secondary' href='/blog/'>ブログを一覧で読む</a></div></section>"
    )
