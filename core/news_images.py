"""Attach source-matched thumbnails without changing the news or its links."""
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from core.editorial_feed import _ElementSpans

ROOT = Path(__file__).resolve().parents[1]
STYLE_ID = 'news-images-style'


def _catalog():
    return json.loads((ROOT / 'config/news-images.json').read_text(encoding='utf-8'))


def image_for(url, *, codex=False):
    catalog = _catalog()
    entry = catalog['codex'] if codex else catalog['articles'].get(url, catalog['fallback'])
    parsed = urlsplit(entry['image'])
    if not ((parsed.scheme == 'https' and parsed.netloc) or
            (entry['image'].startswith('/') and not entry['image'].startswith('//') and not parsed.netloc)):
        raise ValueError('News thumbnails must use HTTPS or a local asset')
    if '..' in parsed.path.split('/'):
        raise ValueError('Invalid news thumbnail path')
    return entry


def thumbnail(url, *, codex=False):
    entry = image_for(url, codex=codex)
    credit = entry['credit']
    return ('<span class="news-thumbnail">'
            f'<img src="{escape(entry["image"], quote=True)}" alt="{escape(entry["alt"], quote=True)}" '
            f'title="{escape(credit, quote=True)}" width="240" height="160" '
            'loading="lazy" decoding="async" referrerpolicy="no-referrer">'
            '</span>')


def strip_news_images(document):
    document = re.sub(r'<span class="news-thumbnail">.*?</span>', '', document, flags=re.S)
    return re.sub(r'<style id="news-images-style">.*?</style>', '', document, flags=re.S)


def apply_news_images(document, news=None):
    """Use exact article URLs, never rank alone, to choose a publisher image."""
    document = strip_news_images(document)
    changed = False
    if 'id="ai-news"' in document or "id='ai-news'" in document:
        if news is None:
            news = json.loads((ROOT / 'content/daily-ai-news.json').read_text(encoding='utf-8'))
        def add_home(match):
            nonlocal changed
            rank = int(match[2])
            item = news['items'][rank-1]
            text = BeautifulSoup(match[3], 'html.parser').get_text(' ', strip=True)
            if item['title'] not in text:
                raise ValueError('News title and thumbnail source do not match')
            changed = True
            return match[1] + thumbnail(item['url']) + match[3] + match[4]
        document = re.sub(r'(<a\b[^>]*href=[\'"]/ai-news/#news-(\d+)[\'"][^>]*>)(.*?)(</a>)',
                          add_home, document, flags=re.S)
    for class_name in ('daily-ai-news__item', 'codex-feature-card'):
        for start, end in reversed(_ElementSpans(document, class_name).spans):
            fragment = document[start:end]
            soup = BeautifulSoup(fragment, 'html.parser')
            link = soup.select_one('.update-card__source a[href]') if class_name == 'codex-feature-card' else soup.select_one('h3 a[href]')
            if not link:
                continue
            insertion = fragment.index('>') + 1
            fragment = fragment[:insertion] + thumbnail(link['href'], codex=class_name == 'codex-feature-card') + fragment[insertion:]
            document = document[:start] + fragment + document[end:]
            changed = True
    if changed:
        css = (ROOT / 'site/templates/ai-news/news-images.css').read_text(encoding='utf-8')
        if document.count('</head>') != 1:
            raise ValueError('Expected one news document head')
        document = document.replace('</head>', f'<style id="{STYLE_ID}">{css}</style></head>')
    return document
