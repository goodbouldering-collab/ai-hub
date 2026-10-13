"""Original paper illustrations; preserve hero and documentary image contents."""
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = '/design-system/studio/images/paper-20261014/'
ALIASES = {'site': 'code', 'article-workflow': 'rag', 'article-cloud': 'code',
           'article-remote': 'salon', 'article-decision': 'support', 'article-orca': 'agent',
           'article-web-assistant': 'code', 'article-mindclip': 'rag',
           'article-optimizer': 'personal', 'article-infrastructure': 'support',
           'article-ai-world': 'salon', 'article-news': 'practice'}
ALT = {
 'agent': '紙の種から店舗・カレンダー・資料が育つ、AI活用のペーパーアート',
 'personal': '二人で絡まった紙の道を一本につなぐ、個別相談のペーパーアート',
 'code': 'ブラウザの窓から小さな店舗が生まれる、Web制作のペーパーアート',
 'support': '資料・予定・仕事の島を一本の道でつなぐ、伴走支援のペーパーアート',
 'salon': '離れた場所の作り手が一つの星につながる、交流のペーパーアート',
 'practice': '本から小さな階段を進み星へ届く、実践学習のペーパーアート',
 'rag': '紙の図書館で金色の資料を探す、根拠を確かめるペーパーアート',
 'climbing': '本から立ち上がった紙の山を登る、クライミングのペーパーアート',
}

def apply_paper_art(document):
    def replace(match):
        tag = BeautifulSoup(match[0], 'html.parser').img
        src = tag.get('src', '')
        if '/photo-20261011/' not in src:
            return match[0]
        key = Path(src.split('?', 1)[0]).stem
        key = ALIASES.get(key, key)
        if key not in ALT:
            return match[0]
        tag['src'] = IMAGE_ROOT + key + '.webp'
        tag['alt'] = ALT[key]
        tag['width'], tag['height'] = '960', '640'
        tag['loading'], tag['decoding'] = 'lazy', 'async'
        tag.attrs.pop('srcset', None)
        return str(tag)
    document = re.sub(r'<img\b[^>]*>', replace, document, flags=re.S | re.I)
    css = (ROOT/'site/templates/ai-news/paper-art.css').read_text(encoding='utf-8')
    style = '<style id="paper-art-style">'+css+'</style>'
    pattern = r'<style id="paper-art-style">.*?</style>'
    if re.search(pattern, document, flags=re.S):
        return re.sub(pattern, lambda _: style, document, flags=re.S)
    return document.replace('</head>', style+'</head>')
