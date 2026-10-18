"""Apply the user-approved homepage copy, including the October 12 heading."""
import re

TITLE = '彦根で使えるAIを学ぶ'
SUBTITLE = 'AIエージェント動いてますか？'
TAGLINE = '普及率6%｜今が好機'
BENEFIT = 'あなたの経験がAIで拡張できる'
CONCERN = 'でも、なんかうまく使えてないかも・・・'
STYLE = '''<style id="hero-copy-style">
#top .focus-title .focus-title-first,
#top .focus-title .focus-title-line,
#top .focus-title .focus-title-line strong { white-space:normal; word-break:keep-all; overflow-wrap:anywhere; }
#top #hero-advantage-title { margin:0 0 22px; line-height:1.7; }
#top #hero-advantage-title .hero-advantage-equation,
#top #hero-advantage-title .hero-advantage-outcome { display:block; white-space:normal; }
#top #hero-glass-art { position:relative; }
#top .hero-opportunity-badge { position:absolute; top:16px; right:16px; z-index:3; margin:0; padding:8px 12px; border:1px solid rgba(255,255,255,.7); border-radius:999px; background:rgba(255,255,255,.92); color:#253d3a; font:700 12px/1.2 sans-serif; letter-spacing:.04em; white-space:nowrap; box-shadow:0 2px 12px rgba(20,40,35,.08); pointer-events:none; }
@media(max-width:600px) { #top .hero-opportunity-badge { top:10px; right:10px; padding:7px 10px; font-size:11px; } }
</style>'''


def apply_hero_copy(document):
    if not re.search(r'class=["\x27]focus-title["\x27]', document):
        return document
    document = re.sub(r'(<p\b[^>]*class=["\x27]focus-lead["\x27][^>]*>)(.*?)(</p>)',
                      lambda m: m[1] + m[2].replace('AI対応サイトの代行制作も可能。', 'AI対応サイトの作成も可能。').replace('AI対応サイトの代行も可能。', 'AI対応サイトの作成も可能。') + m[3],
                      document, flags=re.S)
    for class_name, content in [('focus-title-first', TITLE), ('focus-title-line', f'<strong>{SUBTITLE}</strong>')]:
        document, count = re.subn(r'(<span class=["\x27]'+class_name+r'["\x27]>).*?</span>', lambda m: m[1]+content+'</span>', document, count=1, flags=re.S)
        assert count == 1, class_name
    document = re.sub(r'<span class="hero-opportunity-badge">.*?</span>', '', document, flags=re.S)
    document = re.sub(r'(<figure\b[^>]*id="hero-glass-art"[^>]*>)', lambda m: m[1]+f'<span class="hero-opportunity-badge">{TAGLINE}</span>', document, count=1)
    paragraph = f'<p id="hero-advantage-title"><span class="hero-advantage-equation"><strong>{BENEFIT}</strong></span><span class="hero-advantage-outcome">{CONCERN}</span></p>'
    document, count = re.subn(r'<p id=["\x27]hero-advantage-title["\x27]>.*?</p>', lambda _: paragraph, document, flags=re.S)
    if not count:
        document = re.sub(r'(<h1 class=["\x27]focus-title["\x27]>.*?</h1>)', lambda m: m[1]+paragraph, document, count=1, flags=re.S)
    document = re.sub(r'<style id="hero-copy-style">.*?</style>\s*', '', document, flags=re.S)
    return document.replace('</head>', STYLE+'\n</head>', 1)
