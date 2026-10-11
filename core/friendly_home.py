"""Apply the homepage's brighter glass palette without changing its content."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def apply_friendly_home(document):
    document = document.replace("/design-system/studio/images/photo-20261011/hero.webp", "/design-system/studio/images/photo-20261011/hero-friendly-20261011.webp")
    css = (ROOT / 'site/templates/ai-news/friendly-glass.css').read_text(encoding='utf-8')
    css += '\n' + (ROOT / 'site/static/brand/brand.css').read_text(encoding='utf-8')
    style = '<style id="friendly-glass-style">' + css + '</style>'
    pattern = r'<style\b[^>]*id=[\x27"]friendly-glass-style[\x27"][^>]*>.*?</style>'
    document = re.sub(pattern, '', document, flags=re.S)
    if document.count('</head>') != 1:
        raise ValueError('Expected one homepage head')
    return document.replace('</head>', style + '</head>')
