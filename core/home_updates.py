"""Combine the home news entry and the two latest publicly listed blog posts."""
from datetime import date
from html import escape
from html.parser import HTMLParser
import re


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
            self.card = {'href': attrs.get('href', ''), 'title': '', 'date': ''}
        if self.card is not None:
            if 'tr-title' in classes:
                self.field = 'title'
            elif 'tr-date' in classes:
                self.field = 'date'

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


def latest_published_posts(blog_index):
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
        posts[href] = {'href': href, 'title': title, 'date': published}
    latest = sorted(posts.values(), key=lambda post: (post['date'], post['href']), reverse=True)[:2]
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
    combined = (
        feature[1] + '<div class="home-updates__news">' + inner + '</div><!-- /home-updates-news -->'
        '<div id="blog" class="home-updates__blog" role="region" aria-labelledby="home-blog-title">'
        '<h2 id="home-blog-title">最新ブログ</h2>'
        '<a class="home-updates__more" href="/blog/">一覧を見る<b aria-hidden="true">→</b></a>'
        f'<ol>{rows}</ol></div>' + feature[3]
    )
    document = document[:feature.start()] + combined + document[feature.end():]
    # The existing #blog navigation now targets the compact group above.
    document = re.sub(r'<section\b[^>]*id=[\'"]blog[\'"][^>]*>.*?</section>', '', document, flags=re.S)
    style = f'<style id="home-updates-style">{css}</style>'
    pattern = r'<style\b[^>]*id=[\'"]home-updates-style[\'"][^>]*>.*?</style>'
    if re.search(pattern, document, re.S):
        document = re.sub(pattern, lambda _: style, document, flags=re.S)
    else:
        if document.count('</head>') != 1:
            raise ValueError('Expected one document head')
        document = document.replace('</head>', style + '</head>')
    return document
