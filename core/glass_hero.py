"""Add the original glass conversation-loop artwork to the homepage only."""
from pathlib import Path
import re

from core.editorial_feed import _ElementSpans

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ('hero-glass-640.webp', 'hero-glass-1200.webp')
START = '<!-- glass-hero:20261012 -->'
END = '<!-- /glass-hero:20261012 -->'
FIGURE = (START + '<figure id="hero-glass-art" class="hero-glass-art">'
          '<div class="hero-glass-surface"><img '
          'src="/design-system/studio/images/hero-glass-1200.webp" '
          'srcset="/design-system/studio/images/hero-glass-640.webp 640w, '
          '/design-system/studio/images/hero-glass-1200.webp 1200w" '
          'sizes="(max-width: 760px) 360px, 50vw" '
          'width="1200" height="1200" fetchpriority="high" decoding="async" '
          'alt="透明な青緑のガラスの輪から光がひらく、対話とAIの可能性を表したアート">'
          '</div></figure>' + END)


def apply_glass_hero(document: str) -> str:
    if not _ElementSpans(document, 'focus-hero-shell').spans:
        return document
    # Replace only this layer. Keep surrounding HTML and its whitespace intact.
    document = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', document, flags=re.S)
    spans = _ElementSpans(document, 'focus-hero-shell').spans
    if len(spans) != 1:
        raise ValueError('Expected one homepage hero shell')
    _, end = spans[0]
    assert document[end - 6:end] == '</div>'
    document = document[:end - 6] + FIGURE + document[end - 6:]
    css = (ROOT / 'site/templates/ai-news/glass-hero.css').read_text(encoding='utf-8')
    style = '<style id="glass-hero-style">' + css + '</style>'
    pattern = r'<style id="glass-hero-style">.*?</style>'
    if re.search(pattern, document, flags=re.S):
        return re.sub(pattern, lambda _: style, document, flags=re.S)
    if document.count('</head>') != 1:
        raise ValueError('Expected one document head')
    return document.replace('</head>', style + '</head>', 1)
