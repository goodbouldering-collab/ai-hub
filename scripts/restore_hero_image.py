"""Restore the existing hero photograph without rebuilding other sections."""
from pathlib import Path
import re


def restore(text: str) -> str:
    if 'id="restored-hero-image"' in text:
        return text
    start = text.index("<section class='focus-hero'")
    end = text.index('</section>', start)
    hero = text[start:end]
    closing = '</div></div>'
    if not hero.endswith(closing):
        raise ValueError('Unexpected hero layout; review before modifying')
    figure = (
        '<figure class="restored-hero-image" id="restored-hero-image">'
        '<img src="/img/hero-ai-consult-hikone.png" '
        'alt="彦根城を背景に、パソコンを囲んでAIを学ぶ講習のイメージ" '
        'width="1672" height="941" fetchpriority="high" decoding="async">'
        '</figure>'
    )
    hero = hero[:-len(closing)] + '</div>' + figure + '</div>'
    text = text[:start] + hero + text[end:]
    css = '''<style id="restored-hero-image-style">
.focus-hero-shell{grid-template-columns:minmax(0,760px) minmax(0,1fr);gap:32px}
.restored-hero-image{margin:0;min-width:0;align-self:center}
.restored-hero-image img{display:block;width:100%;height:auto;border-radius:20px}
@media(max-width:1200px){.focus-hero-shell{grid-template-columns:1fr}.restored-hero-image{width:100%;max-width:760px}}
</style>'''
    return text.replace('</head>', css + '</head>', 1)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    path = root / 'cloudflare-runtime/public/index.html'
    path.write_text(restore(path.read_text(encoding='utf-8')), encoding='utf-8', newline='\n')
