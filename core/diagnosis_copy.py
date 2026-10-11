"""Invite visitors to the two existing diagnoses before the blog."""
import re
from bs4 import BeautifulSoup
from core.editorial_feed import _ElementSpans

PROMPTS = {'readiness-guide-title': 'あなたのAI実力を試す', 'seo-llmo-guide-title': 'サイトのAI対応を調べる'}
STYLE = '''<style id="diagnosis-copy-style">
body.studio-editorial.studio-home .diagnosis-guide-row{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:14px!important;max-width:1160px;margin:28px auto!important;padding:0 24px!important;background:none!important;border:0!important}
.diagnosis-guide-row .diagnosis-intro{grid-column:1/-1;margin:0 0 4px}.diagnosis-guide-row .diagnosis-intro h2{margin:0 0 7px;font-size:24px;line-height:1.5;color:#243747;letter-spacing:.01em}.diagnosis-guide-row .diagnosis-intro p{margin:0;font-size:14px;line-height:1.8;color:#566775}
.diagnosis-guide-row .diagnosis-action{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:72px;padding:18px 22px;border:1px solid #345567;border-radius:12px;background:#193c49;color:#fff!important;text-decoration:none!important;box-shadow:0 5px 16px #102f4210;transition:background .15s,transform .15s}
.diagnosis-guide-row .diagnosis-action--site{background:#fff;color:#193c49!important;border-color:#c7d3d9}
.diagnosis-action strong{font-size:17px;line-height:1.5;font-weight:750}.diagnosis-action small{display:block;font-size:11px;letter-spacing:.04em;line-height:1.5;opacity:.8;margin-bottom:3px}.diagnosis-action>span:last-child{font-size:22px}
.diagnosis-guide-row .diagnosis-action:hover{transform:translateY(-2px);background:#285569}.diagnosis-guide-row .diagnosis-action--site:hover{background:#edf3f5}.diagnosis-action:focus-visible{outline:3px solid #56879a;outline-offset:4px}
@media(max-width:600px){body.studio-editorial.studio-home .diagnosis-guide-row{grid-template-columns:1fr!important;padding:0 18px!important;gap:10px!important}.diagnosis-guide-row .diagnosis-intro h2{font-size:20px}.diagnosis-guide-row .diagnosis-intro p{font-size:13px}.diagnosis-guide-row .diagnosis-action{min-height:68px;padding:14px 18px}.diagnosis-action strong{font-size:16px}}
@media(prefers-reduced-motion:reduce){.diagnosis-guide-row .diagnosis-action{transition:none;transform:none}}
</style>'''

def apply_diagnosis_copy(document):
    spans = _ElementSpans(document, 'diagnosis-guide-row').spans
    if len(spans) != 1:
        raise ValueError('Expected one diagnosis button group')
    start,end=spans[0]
    source=BeautifulSoup(document[start:end], 'html.parser')
    destinations=[a['href'] for a in source.select('a[href]')]
    paths=['/ai-agent-readiness/','/seo-llmo-diagnosis/']
    if not all(any(href.rstrip('/')==path.rstrip('/') for href in destinations) for path in paths):
        raise ValueError('Expected both existing diagnosis destinations')
    replacement=('<div id="diagnosis-start" class="diagnosis-guide-row" role="region" aria-labelledby="diagnosis-guide-title">'
                 '<div class="diagnosis-intro"><h2 id="diagnosis-guide-title">まずは診断で、次の一歩を。</h2>'
                 '<p>自分のAI活用力やサイトの課題を、ここからチェック。</p></div>')
    for path,label,caption,modifier in [(paths[0],PROMPTS['readiness-guide-title'],'あなたのAI実力診断',''),(paths[1],PROMPTS['seo-llmo-guide-title'],'AI対応サイト診断',' diagnosis-action--site')]:
        replacement+=f'<a class="diagnosis-action{modifier}" href="{path}"><span><small>{caption}</small><strong>{label}</strong></span><span aria-hidden="true">→</span></a>'
    replacement+='</div>'
    # A first migration pass can precede blog generation. Once the blog exists,
    # move the whole group without reserializing other sections or duplicating it.
    without_group=document[:start]+document[end:]
    blogs=list(re.finditer(r'<section\b[^>]*\bid=[\x27"]blog[\x27"][^>]*>',without_group))
    if len(blogs)>1:
        raise ValueError('Expected at most one blog section')
    insertion=blogs[0].start() if blogs else start
    document=without_group[:insertion]+replacement+without_group[insertion:]
    pattern=r'<style id="diagnosis-copy-style">.*?</style>'
    if re.search(pattern,document,flags=re.S):
        return re.sub(pattern,lambda _:STYLE,document,flags=re.S)
    return document.replace('</head>',STYLE+'\n</head>',1)
