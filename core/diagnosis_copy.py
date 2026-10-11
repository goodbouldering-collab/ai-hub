"""Keep the AI readiness action in a compact hero without the removed extras."""
import re
from bs4 import BeautifulSoup
from core.editorial_feed import _ElementSpans
from core.glass_hero import apply_glass_hero

PROMPTS = {'readiness-guide-title': 'あなたのAI実力を試す', 'seo-llmo-guide-title': 'サイトのAI対応を調べる'}
STYLE = '''<style id="diagnosis-copy-style">
body.studio-editorial.studio-home .diagnosis-guide-row{display:grid!important;grid-template-columns:minmax(0,1fr)!important;gap:14px!important;max-width:1160px;margin:28px auto!important;padding:0 24px!important;background:none!important;border:0!important}
.diagnosis-guide-row .diagnosis-intro{grid-column:1/-1;margin:0 0 4px}.diagnosis-guide-row .diagnosis-intro h2{margin:0 0 7px;font-size:24px;line-height:1.5;color:#243747;letter-spacing:.01em}.diagnosis-guide-row .diagnosis-intro p{margin:0;font-size:14px;line-height:1.8;color:#566775}
.diagnosis-guide-row .diagnosis-action{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:72px;padding:18px 22px;border:1px solid #345567;border-radius:12px;background:#193c49;color:#fff!important;text-decoration:none!important;box-shadow:0 5px 16px #102f4210;transition:background .15s,transform .15s}
.diagnosis-guide-row .diagnosis-action--site{background:#fff;color:#193c49!important;border-color:#c7d3d9}
.diagnosis-action strong{font-size:17px;line-height:1.5;font-weight:750}.diagnosis-action small{display:block;font-size:11px;letter-spacing:.04em;line-height:1.5;opacity:.8;margin-bottom:3px}.diagnosis-action>span:last-child{font-size:22px}
.diagnosis-guide-row .diagnosis-action:hover{transform:translateY(-2px);background:#285569}.diagnosis-guide-row .diagnosis-action--site:hover{background:#edf3f5}.diagnosis-action:focus-visible{outline:3px solid #56879a;outline-offset:4px}
@media(max-width:600px){body.studio-editorial.studio-home .diagnosis-guide-row{grid-template-columns:1fr!important;padding:0 18px!important;gap:10px!important}.diagnosis-guide-row .diagnosis-intro h2{font-size:20px}.diagnosis-guide-row .diagnosis-intro p{font-size:13px}.diagnosis-guide-row .diagnosis-action{min-height:68px;padding:14px 18px}.diagnosis-action strong{font-size:16px}}
@media(prefers-reduced-motion:reduce){.diagnosis-guide-row .diagnosis-action{transition:none;transform:none}}
body.studio-editorial.studio-home #top .diagnosis-guide-row{flex-basis:100%;width:100%;max-width:none;margin:6px 0 0!important;padding:0!important;gap:10px!important}
body.studio-editorial.studio-home #top .diagnosis-intro h2{font-size:20px;margin:0 0 4px}
body.studio-editorial.studio-home #top .diagnosis-intro p{font-size:13px}
body.studio-editorial.studio-home #top .diagnosis-action{box-sizing:border-box;min-height:78px;padding:13px 16px;gap:10px}
body.studio-editorial.studio-home #top .diagnosis-action strong{font-size:15px}
body.studio-editorial.studio-home #top .focus-trust{margin:12px 0 22px!important;gap:6px 14px}
body.studio-theme.studio-editorial.studio-home #top .focus-hero-shell{display:block!important}
body.studio-theme.studio-editorial.studio-home #top .focus-hero-copy{width:100%!important;max-width:900px!important;box-sizing:border-box;margin:0 auto!important}
@media(max-width:600px){body.studio-editorial.studio-home #top .diagnosis-guide-row{grid-template-columns:1fr!important}body.studio-editorial.studio-home #top .diagnosis-intro h2{font-size:18px}body.studio-editorial.studio-home #top .diagnosis-action{min-height:64px;padding:10px 14px}}
</style>'''

def apply_diagnosis_copy(document):
    spans = _ElementSpans(document, 'diagnosis-guide-row').spans
    if len(spans) != 1:
        raise ValueError('Expected one diagnosis button group')
    start,end=spans[0]
    source=BeautifulSoup(document[start:end], 'html.parser')
    destinations=[a['href'] for a in source.select('a[href]')]
    paths=['/ai-agent-readiness/']
    if not all(any(href.rstrip('/')==path.rstrip('/') for href in destinations) for path in paths):
        raise ValueError('Expected the existing AI readiness destination')
    replacement=('<div id="diagnosis-start" class="diagnosis-guide-row" role="region" aria-labelledby="diagnosis-guide-title">'
                 '<div class="diagnosis-intro"><h2 id="diagnosis-guide-title">まずは診断で、次の一歩を。</h2>'
                 '<p>自分のAI活用力を、ここからチェック。</p></div>')
    for path,label,caption,modifier in [(paths[0],PROMPTS['readiness-guide-title'],'あなたのAI実力診断','')]:
        replacement+=f'<a class="diagnosis-action{modifier}" href="{path}"><span><small>{caption}</small><strong>{label}</strong></span><span aria-hidden="true">→</span></a>'
    replacement+='</div>'
    document = document[:start] + document[end:]
    if _ElementSpans(document, 'focus-hero-copy').spans:
        document = _place_in_hero(document, replacement)
    else:
        document = document[:start] + replacement + document[start:]
    pattern=r'<style id="diagnosis-copy-style">.*?</style>'
    if re.search(pattern,document,flags=re.S):
        return apply_glass_hero(re.sub(pattern,lambda _:STYLE,document,flags=re.S))
    return apply_glass_hero(document.replace('</head>',STYLE+'\n</head>',1))


def _one(document, class_name):
    spans = _ElementSpans(document, class_name).spans
    if len(spans) != 1:
        raise ValueError(f'Expected one {class_name}')
    return spans[0]


def _place_in_hero(document, diagnosis):
    # Move whole elements, retaining destinations and link attributes.
    start, end = _one(document, 'focus-trust')
    trust = document[start:end]
    document = document[:start] + document[end:]
    _, lead_end = _one(document, 'focus-lead')
    document = document[:lead_end] + trust + document[lead_end:]
    start, end = _one(document, 'focus-actions')
    actions = document[start:end]
    for name in ('secondary', 'hero-text-link'):
        for a, b in reversed(_ElementSpans(actions, name).spans):
            actions = actions[:a] + actions[b:]
    document = document[:start] + actions + document[end:]
    for class_name, element_id in [('home-learning-links', ''), ('', 'restored-hero-image')]:
        for a, b in reversed(_ElementSpans(document, class_name, element_id=element_id).spans):
            document = document[:a] + document[b:]
    _, cta_end = _one(document, 'hero-diagnose-cta')
    return document[:cta_end] + diagnosis + document[cta_end:]
