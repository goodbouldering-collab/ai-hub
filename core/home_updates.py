"""Keep compact updates and the original home blog carousel together."""
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
    posts = latest_published_posts(blog_index)
    rows = ''.join(
        f'<li><a href="{post["href"]}" title="{escape(post["title"], quote=True)}">'
        f'<time datetime="{post["date"]}">{post["date"].replace("-", ".")}</time>'
        f'<span>{escape(post["title"])}</span><b aria-hidden="true">↗</b></a></li>'
        for post in posts
    )
    feature_pattern = r'(<section\b[^>]*id=[\'"]ai-news[\'"][^>]*>)(.*?)(</section>)'
    matches = list(re.finditer(feature_pattern, document, re.S))
    if len(matches) != 1:
        raise ValueError('Expected one home news entry')
    feature = matches[0]
    inner = feature[2]
    previous = re.fullmatch(r'<div class="home-updates__news">(.*?)</div><!-- /home-updates-news -->.*', inner, re.S)
    if previous:
        inner = previous[1]
    carousel = render_home_blog_list(blog_index)
    # A div keeps the news section flat for the daily shell replacement.
    carousel = carousel.replace("<section class='focus-block' id='blog'>", "<div class='home-updates__carousel' id='blog' role='region' aria-label='ブログ'>", 1)
    carousel = carousel.removesuffix('</section>') + '</div>'
    combined = (
        feature[1] + '<div class="home-updates__news">' + inner + '</div><!-- /home-updates-news -->'
        + carousel + feature[3]
    )
    document = document[:feature.start()] + combined + document[feature.end():]
    latest = (
        '<section id="latest-blog" class="focus-block home-updates__blog" aria-labelledby="home-blog-title">'
        '<h2 id="home-blog-title">最新ブログ</h2>'
        '<a class="home-updates__more" href="/blog/">一覧を見る<b aria-hidden="true">→</b></a>'
        f'<ol>{rows}</ol></section>'
    )
    # Replace either the original carousel section or the already-moved list.
    pattern = r"<section\b[^>]*id=['\"](?:blog|latest-blog)['\"][^>]*>.*?</section>"
    if re.search(pattern, document, re.S):
        document = re.sub(pattern, lambda _: latest, document, flags=re.S)
    else:
        speaker = re.search(r"<section\b[^>]*id=['\"]speaker['\"][^>]*>", document)
        if not speaker:
            raise ValueError('Expected speaker section as home blog insertion point')
        document = document[:speaker.start()] + latest + document[speaker.start():]
    style = f'<style id="home-updates-style">{css}</style>'
    pattern = r'<style\b[^>]*id=[\'"]home-updates-style[\'"][^>]*>.*?</style>'
    if re.search(pattern, document, re.S):
        document = re.sub(pattern, lambda _: style, document, flags=re.S)
    else:
        if document.count('</head>') != 1:
            raise ValueError('Expected one document head')
        document = document.replace('</head>', style + '</head>')
    return document


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
