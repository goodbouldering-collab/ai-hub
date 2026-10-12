"""Add one panoramic AI-agent workshop illustration to the homepage only."""
from pathlib import Path
import re

from core.editorial_feed import _ElementSpans

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ('hero-workshop-800.webp', 'hero-workshop-1672.webp')
START = '<!-- glass-hero:20261012 -->'
END = '<!-- /glass-hero:20261012 -->'
FIGURE = (START + '<figure id="hero-glass-art" class="hero-glass-art" data-workshop-hero="20261012">'
          '<div class="hero-glass-surface"><img '
          'src="/design-system/studio/images/hero-workshop-1672.webp" '
          'srcset="/design-system/studio/images/hero-workshop-800.webp 800w, '
          '/design-system/studio/images/hero-workshop-1672.webp 1672w" '
          'sizes="(max-width: 600px) 133vw, 100vw" '
          'width="1672" height="941" fetchpriority="high" decoding="async" '
          'alt="AIエージェント講習のイメージ。講師と受講者がPCを囲み、依頼・実行・確認の流れを学びながら、完成した告知を見て使い方に気づく場面">'
          '</div><figcaption>AIエージェント講習のイメージ</figcaption></figure>' + END)


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
