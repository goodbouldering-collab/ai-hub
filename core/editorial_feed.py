"""Compose public blog and daily Codex links without changing article content."""
from __future__ import annotations

from datetime import date
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Iterable, Mapping
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / 'config/editorial-feed.json'
STYLE_ID = 'editorial-feed-style'


class _PublicCards(HTMLParser):
    """Read only cards explicitly included in the public blog index."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.posts = []
        self.card = None
        self.field = None
        self.field_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'a' and 'tr-card' in classes:
            self.card = {'href': attrs.get('href', ''), 'title': '', 'date': '', 'summary': ''}
        if self.card is None:
            return
        for attribute in ('data-date', 'data-published', 'datetime'):
            if attrs.get(attribute):
                self.card['date_iso'] = attrs[attribute]
                break
        if tag == 'img' and not self.card.get('image'):
            self.card['image'] = attrs.get('src', '')
            self.card['image_alt'] = attrs.get('alt', '')
        if tag == 'div':
            if self.field:
                self.field_depth += 1
            for class_name, field in (('tr-title', 'title'), ('tr-date', 'date'), ('tr-sum', 'summary')):
                if class_name in classes:
                    self.field = field
                    self.field_depth = 1
                    break

    def handle_data(self, data):
        if self.card is not None and self.field:
            self.card[self.field] += data

    def handle_endtag(self, tag):
        if tag == 'div' and self.field:
            self.field_depth -= 1
            if not self.field_depth:
                self.field = None
        if tag == 'a' and self.card is not None:
            self.posts.append(self.card)
            self.card = None
            self.field = None
            self.field_depth = 0


def _parse_public_date(value: str) -> str:
    match = re.search(r'(\d{4})[-./年](\d{1,2})[-./月](\d{1,2})(?:日)?', value)
    if not match:
        raise ValueError('Published blog card has no recognizable date')
    return date(*(int(part) for part in match.groups())).isoformat()


def _normalise_posts(posts: Iterable[Mapping[str, str]]) -> list[dict[str, str]]:
    unique = {}
    for source in posts:
        href = str(source.get('href', ''))
        match = re.fullmatch(r'(?:\./|/blog/)([a-z0-9-]+)\.html', href)
        if not match or match[1] == 'codex-update-log':
            continue
        title = str(source.get('title', '')).strip()
        date_label = str(source.get('date_label') or source.get('date', '')).strip()
        published = _parse_public_date(str(source.get('date_iso') or source.get('date', '')))
        if not title:
            raise ValueError('Published blog card has no title')
        date.fromisoformat(published)
        canonical = f'/blog/{match[1]}.html'
        post = {key: str(value) for key, value in source.items()}
        post.update(href=canonical, title=title, date=published, date_label=date_label or published, date_iso=published,
                    summary=str(source.get('summary', '')).strip(),
                    source_href=str(source.get('source_href') or href))
        unique[canonical] = post
    return sorted(unique.values(), key=lambda post: (post['date'], post['href']), reverse=True)


def public_posts(blog_document: str) -> list[dict[str, str]]:
    """Keep public .tr-card articles; exclude the legacy Codex news duplicate."""
    parser = _PublicCards()
    parser.feed(blog_document)
    return _normalise_posts(parser.posts)


def _config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def _safe_image(value: str) -> str:
    """Accept an existing local asset or HTTPS image, never an active URL."""
    value = str(value).strip()
    parsed = urlsplit(value)
    if '..' in parsed.path.split('/') or not value:
        return ''
    if value.startswith('/') and not value.startswith('//') and not parsed.netloc:
        return value
    if parsed.scheme == 'https' and parsed.netloc:
        return value
    return ''


def _post_image(post: Mapping[str, str], config: dict) -> tuple[str, str]:
    slug = Path(post['href']).stem
    entry = config['articles'].get(slug)
    if entry:
        return entry['image'], entry['alt']
    # A new, publicly listed post may supply its own image. Reading its
    # frontmatter never adds unpublished Markdown files to the feed.
    image, alt = '', ''
    source = ROOT / 'content/blog' / (slug + '.md')
    if source.is_file():
        raw = source.read_text(encoding='utf-8')
        parts = raw.split('---', 2)
        if raw.startswith('---') and len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            if isinstance(meta, dict):
                image = _safe_image(meta.get('image') or '')
                alt = str(meta.get('image_alt') or '')
    if not image:
        image = _safe_image(post.get('image', ''))
        alt = str(post.get('image_alt') or '')
    if not image:
        catalog_path = ROOT / 'config/home-blog-images.json'
        if catalog_path.is_file():
            catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
            image = _safe_image(catalog.get(slug, ''))
    if not image:
        return config['fallback']['image'], config['fallback']['alt']
    return image, alt or f'{post["title"]}のイメージ'


def _news_date(feature: str) -> str:
    # data-news-date survives a second pass; daily regeneration supplies a new
    # original feature with its own <time datetime> before this transform runs.
    for pattern in (r'\bdata-news-date=[\x27"](\d{4}-\d{2}-\d{2})[\x27"]',
                    r'<time\b[^>]*\bdatetime=[\x27"](\d{4}-\d{2}-\d{2})(?:T[^\x27"]*)?[\x27"]'):
        match = re.search(pattern, feature)
        if match:
            date.fromisoformat(match[1])
            return match[1]
    raise ValueError('The home AI news feature must include its published date')


def _row(post: Mapping[str, str], config: dict, *, news: bool = False,
         preserve_href: bool = False, heading_level: int = 3) -> str:
    image, alt = ((config['news']['image'], config['news']['alt']) if news else _post_image(post, config))
    href = post['href']
    if preserve_href and not news:
        candidate = post.get('source_href', href)
        if re.fullmatch(r'(?:\./|/blog/)[a-z0-9-]+\.html', candidate):
            href = candidate
    classes = 'editorial-feed__row editorial-feed__news' if news else 'editorial-feed__row tr-card'
    title = escape(post['title'])
    category = config['news']['label'] if news else config['article_label']
    date_label = escape(str(post.get('date_label') or post['date']))
    return (
        '<li class="editorial-feed__item">'
        f'<a class="{classes}" href="{escape(href, quote=True)}">'
        '<span class="editorial-feed__media">'
        f'<img src="{escape(image, quote=True)}" alt="{escape(alt, quote=True)}" '
        'width="480" height="320" loading="lazy" decoding="async"></span>'
        '<div class="editorial-feed__body">'
        '<div class="editorial-feed__meta">'
        f'<span class="editorial-feed__category">{escape(category)}</span>'
        f'<div class="tr-date editorial-feed__date"><time datetime="{post["date"]}">{date_label}</time></div></div>'
        f'<div class="tr-title editorial-feed__title" role="heading" aria-level="{heading_level}">{title}</div>'
        f'<div class="tr-sum editorial-feed__summary">{escape(post["summary"])}</div>'
        '</div></a></li>'
    )


def _news_post(news_date: str, config: dict) -> dict[str, str]:
    date.fromisoformat(news_date)
    return {'href': config['news']['href'], 'title': config['news']['title'],
            'summary': config['news']['summary'], 'date': news_date}


def _style(document: str, css: str) -> str:
    style = f'<style id="{STYLE_ID}">{css}</style>'
    pattern = rf'<style\b[^>]*id=[\x27"]{STYLE_ID}[\x27"][^>]*>.*?</style>'
    if re.search(pattern, document, re.S):
        return re.sub(pattern, lambda _: style, document, flags=re.S)
    if document.count('</head>') != 1:
        raise ValueError('Expected one document head')
    return document.replace('</head>', style + '</head>')


def apply_home_feed(document: str, posts: Iterable[Mapping[str, str]], css: str) -> str:
    """Show daily AI/Codex news plus the latest two publicly listed articles."""
    posts = _normalise_posts(posts)
    if len(posts) < 2:
        raise ValueError('Expected at least two publicly listed blog posts')
    config = _config()
    pattern = r'<section\b[^>]*id=[\x27"]ai-news[\x27"][^>]*>.*?</section>'
    matches = list(re.finditer(pattern, document, re.S))
    if len(matches) != 1:
        raise ValueError('Expected one home AI news feature')
    feature = matches[0]
    published = _news_date(feature[0])
    rows = _row(_news_post(published, config), config, news=True)
    rows += ''.join(_row(post, config) for post in posts[:2])
    combined = (
        '<section id="ai-news" class="ai-news-feature editorial-feed-host" aria-labelledby="editorial-feed-title">'
        f'<div id="blog" class="editorial-feed editorial-feed--home" data-news-date="{published}">'
        '<div class="editorial-feed__heading">'
        f'<h2 id="editorial-feed-title">{escape(config["heading"])}</h2>'
        '</div><ol class="editorial-feed__list">' + rows + '</ol>'
        '<div class="editorial-feed__actions">'
        f'<a class="editorial-feed__more" href="{escape(config["more_href"], quote=True)}">'
        f'{escape(config["more_label"])}<span aria-hidden="true">→</span></a></div></div></section>'
    )
    document = document[:feature.start()] + combined + document[feature.end():]
    document = re.sub(r'<section\b[^>]*id=[\x27"](?:blog|latest-blog)[\x27"][^>]*>.*?</section>',
                      '', document, flags=re.S)
    return _style(document, css)


class _ElementSpans(HTMLParser):
    """Find complete classed elements without reserializing the page shell."""
    def __init__(self, document: str, class_name: str):
        super().__init__(convert_charrefs=True)
        self.class_name = class_name
        self.lines = [0]
        self.lines.extend(match.end() for match in re.finditer('\n', document))
        self.active_tag = None
        self.depth = 0
        self.start = 0
        self.spans = []
        self.feed(document)

    def _offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if self.active_tag:
            if tag == self.active_tag:
                self.depth += 1
        elif self.class_name in dict(attrs).get('class', '').split():
            self.active_tag = tag
            self.depth = 1
            self.start = self._offset()

    def handle_endtag(self, tag):
        if tag == self.active_tag:
            self.depth -= 1
            if not self.depth:
                self.spans.append((self.start, self._offset() + len(tag) + 3))
                self.active_tag = None


def apply_blog_feed(blog_document: str, news_date: str, css: str) -> str:
    """Restyle the public index and add one daily-news row, retaining its shell."""
    posts = public_posts(blog_document)
    if not posts:
        raise ValueError('Expected publicly listed blog posts')
    config = _config()
    spans = _ElementSpans(blog_document, 'tr-grid').spans
    if len(spans) != 1:
        raise ValueError('Expected one public blog grid')
    rows = _row(_news_post(news_date, config), config, news=True, heading_level=2)
    rows += ''.join(_row(post, config, preserve_href=True, heading_level=2) for post in posts)
    replacement = '<ol class="tr-grid editorial-feed editorial-feed--archive editorial-feed__list">' + rows + '</ol>'
    start, end = spans[0]
    result = blog_document[:start] + replacement + blog_document[end:]
    result = re.sub(r'<title>.*?</title>', '<title>AI相談</title>', result, count=1, flags=re.S)
    result = re.sub(r'<h1>ブログ(?:・Codex情報)?</h1>',
                    lambda _: f'<h1>{escape(config["heading"])}</h1>', result, count=1)
    return _style(result, css)