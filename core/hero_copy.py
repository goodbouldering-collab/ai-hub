"""Apply the homepage copy approved in the September 26 browser annotations."""
import re

TITLE = '彦根発！ちゃんと使えるAI'
SUBTITLE = '個人事業から業務管理までこなせる'
BENEFIT = 'あなたの経験がAIで拡張できる'
CONCERN = 'でも、なんかうまく使えてないかも・・・'
STYLE = '''<style id="hero-copy-style">
#top .focus-title .focus-title-first,
#top .focus-title .focus-title-line,
#top .focus-title .focus-title-line strong { white-space:normal; word-break:keep-all; overflow-wrap:anywhere; }
#top #hero-advantage-title { margin:0 0 22px; line-height:1.7; }
#top #hero-advantage-title .hero-advantage-equation,
#top #hero-advantage-title .hero-advantage-outcome { display:block; white-space:normal; }
</style>'''


def apply_hero_copy(document):
    if not re.search(r'class=["\x27]focus-title["\x27]', document):
        return document
    for class_name, content in [('focus-title-first', TITLE.replace('！', '！<wbr>')), ('focus-title-line', '<strong>'+SUBTITLE.replace('から', 'から<wbr>')+'</strong>')]:
        document, count = re.subn(r'(<span class=["\x27]'+class_name+r'["\x27]>).*?</span>', lambda m: m[1]+content+'</span>', document, count=1, flags=re.S)
        assert count == 1, class_name
    paragraph = f'<p id="hero-advantage-title"><span class="hero-advantage-equation"><strong>{BENEFIT}</strong></span><span class="hero-advantage-outcome">{CONCERN}</span></p>'
    document, count = re.subn(r'<p id=["\x27]hero-advantage-title["\x27]>.*?</p>', lambda _: paragraph, document, flags=re.S)
    if not count:
        document = re.sub(r'(<h1 class=["\x27]focus-title["\x27]>.*?</h1>)', lambda m: m[1]+paragraph, document, count=1, flags=re.S)
    document = re.sub(r'<style id="hero-copy-style">.*?</style>\s*', '', document, flags=re.S)
    return document.replace('</head>', STYLE+'\n</head>', 1)
