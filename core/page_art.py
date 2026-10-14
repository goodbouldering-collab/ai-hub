"""Apply the approved paper artwork without ever changing the homepage."""
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import html
import json
import re
import shutil
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/page-art.json'
VERSION = '20261015'

def normalize(value, page):
    return urlsplit(urljoin('/' + page, html.unescape(value))).path

def apply_page_art(document, page):
    if page == 'index.html' or page.startswith(('admin/', 'watch/')):
        return document
    config = json.loads(CONFIG.read_text(encoding='utf8'))
    mapping = {item['source']: item for item in config['images']}
    active = {key: item for key, item in mapping.items() if page in item['pages']}
    if not active:
        return document
    def attribute(match):
        prefix, quote, value = match.groups()
        if urlsplit(html.unescape(value)).netloc and 'aiclimb.aiclimb.workers.dev' not in value:
            return match[0]
        item = active.get(normalize(value, page))
        if not item:
            return match[0]
        # Image links, social metadata and video posters follow the same mapping.
        target = item['target']
        if value.startswith('https://'):
            target = 'https://aiclimb.aiclimb.workers.dev' + target
        return prefix + quote + target + quote
    document = re.sub(r'((?:src|poster|content|href)\s*=\s*)([\"\'])(.*?)(?:\2)', attribute, document, flags=re.I)
    # JSON-LD image URLs are kept consistent with the visible cover.
    for source, item in active.items():
        document = document.replace('https://aiclimb.aiclimb.workers.dev' + source,
                                    'https://aiclimb.aiclimb.workers.dev' + item['target'])
    targets = {item['target']: item for item in active.values()}
    def image_tag(match):
        tag = BeautifulSoup(match[0], 'html.parser').img
        item = targets.get(normalize(tag.get('src',''), page))
        if not item:
            return match[0]
        classes = list(tag.get('class', []))
        if 'page-paper-art' not in classes:
            classes.append('page-paper-art')
        tag['class'] = classes
        tag['decoding'] = 'async'
        tag['width'],tag['height'] = ('1440','960') if item['mode']=='generate' else ('960','640')
        if item['key']=='speaker-portrait-painting':
            tag['width'],tag['height']='1000','1000'
            tag['alt']='店内のテーブルとAI講習の風景を背景にした講師 由井辰美'
            tag['style']='object-fit:contain!important;height:auto!important;min-height:0!important;aspect-ratio:auto 1/1!important;transform:none!important;margin:0!important'
        return str(tag)
    document = re.sub(r'<img\b[^>]*>',image_tag,document,flags=re.S|re.I)
    style = '<style id="page-paper-art-style">img.page-paper-art{height:auto!important;aspect-ratio:auto 3/2!important;object-fit:contain!important;max-width:100%;background:#f4efe6}html body .speaker-content .speaker-page-visual .speaker-art:has(>img.page-paper-art){height:auto!important;min-height:0!important;aspect-ratio:1/1!important}img.page-paper-art[src*="speaker-portrait"]{aspect-ratio:auto 1/1!important}video[poster*="paper-20261015"]{object-fit:contain;background:#f4efe6}</style>'
    if 'page-paper-art-style' not in document:
        document=document.replace('</head>',style+'</head>')
    return document

def apply_page_art_tree(output):
    changed = []
    for path in output.rglob('*.html'):
        page = path.relative_to(output).as_posix()
        before = path.read_bytes()
        after = apply_page_art(before.decode('utf8'), page).encode('utf8')
        if after != before:
            path.write_bytes(after)
            changed.append(page)
    for version in ('paper-20261014', 'paper-20261015'):
        relative = Path('design-system/studio/images') / version
        shutil.copytree(ROOT / 'site/static' / relative, output / relative, dirs_exist_ok=True)
    return sorted(changed)
