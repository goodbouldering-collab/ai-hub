"""Keep the three compact homepage actions together across daily builds."""
import re
from bs4 import BeautifulSoup
from core.editorial_feed import _ElementSpans
from core.glass_hero import apply_glass_hero

PROMPTS = {'readiness-guide-title': 'ほんとにAI使えてる？', 'seo-llmo-guide-title': 'AIに表示されてる？'}
STYLE = '''<style id="diagnosis-copy-style">
body.studio-theme.studio-editorial.studio-home #top .focus-actions{gap:0!important;margin-top:0!important}
body.studio-editorial.studio-home .diagnosis-guide-row{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr))!important;gap:6px!important;box-sizing:border-box;max-width:1160px;margin:12px auto!important;padding:0 24px!important;background:none!important;border:0!important}
body.studio-editorial.studio-home #top .diagnosis-guide-row{flex-basis:100%;width:100%;max-width:none;margin:0!important;padding:0!important}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action{display:flex!important;align-items:center;justify-content:flex-start!important;gap:10px!important;box-sizing:border-box;width:100%;min-width:0;min-height:48px!important;margin:0!important;padding:7px 12px!important;border:1px solid #bfd3cc!important;border-radius:10px!important;background:#fffefa!important;color:#244b46!important;font:inherit;line-height:1.3!important;text-align:left;text-decoration:none!important;box-shadow:none!important;cursor:pointer;transition:background .15s,border-color .15s}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action--flow{background:#244b46!important;border-color:#244b46!important;color:#fff!important}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action svg{display:block;flex:0 0 20px;width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action .diagnosis-label{display:flex;flex-direction:column;gap:1px;min-width:0}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action small{display:block;margin:0;font-size:11px!important;line-height:1.35!important;letter-spacing:0;opacity:1}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action strong{display:block;font-size:13px!important;font-weight:700;line-height:1.4!important;letter-spacing:0}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action:hover{background:#eaf3ed!important;border-color:#6c9b8b!important;transform:none!important}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action--flow:hover{background:#315f57!important;color:#fff!important}
body.studio-editorial.studio-home .diagnosis-guide-row .diagnosis-action:focus-visible{outline:3px solid #528679;outline-offset:3px}
body.studio-editorial.studio-home #top .focus-trust{margin:10px 0 12px!important;gap:6px 14px}
@media(prefers-reduced-motion:reduce){.diagnosis-guide-row .diagnosis-action{transition:none!important}}
/* Keep these action tokens stronger than the existing pastel theme layer. */
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row{gap:10px!important;border-top:0!important;margin-top:8px!important}
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-action{min-height:76px!important;padding:13px 14px!important;border:2px solid #087e79!important;border-radius:14px!important;background:#087e79!important;color:#fff!important;box-shadow:0 5px 12px #075b5526!important}
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-action strong{font-size:16px!important;font-weight:800;line-height:1.45!important;color:inherit!important}
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-action small{font-size:12px!important;color:inherit!important;line-height:1.45!important}
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-arrow{margin-left:auto;flex:none;font-size:22px;font-weight:700;line-height:1}
@media(max-width:1000px){body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-arrow{display:none}}
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-action:hover{background:#065f5b!important;border-color:#065f5b!important;color:#fff!important}
body.studio-theme.studio-editorial.studio-home #top #diagnosis-start.diagnosis-guide-row .diagnosis-action:focus-visible{outline:3px solid #b65c23;outline-offset:4px}
</style>'''


def _icon(paths):
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + paths + '</svg>'


def _buttons():
    items = [
        ('button', 'type="button" aria-controls="diagnoseModal" aria-haspopup="dialog"',
         ' diagnosis-action--flow diagnose-open', '何からはじめれば？', 'どの講習を選べば？',
         '<path d="M4 5h6v5H4zM14 14h6v5h-6zM7 10v6h7M10 7h7v7"/>'),
        ('a', 'href="/seo-llmo-diagnosis/"', ' diagnosis-action--site',
         PROMPTS['seo-llmo-guide-title'], 'サイト診断',
         '<rect x="3" y="3" width="18" height="13" rx="2"/><path d="M8 21h8M12 16v5"/><circle cx="11" cy="9" r="3"/><path d="m13 11 3 3"/>'),
        ('a', 'href="/ai-agent-readiness/"', '',
         PROMPTS['readiness-guide-title'], 'AI実力診断',
         '<path d="M4 20h16M6 16v-4M12 16V8M18 16V4M4 7l5-3 4 1 5-3"/>'),
    ]
    result = '<div id="diagnosis-start" class="diagnosis-guide-row" role="group" aria-label="自分に合う入口を選ぶ">'
    for tag, attrs, modifier, question, title, icon in items:
        result += (f'<{tag} class="diagnosis-action{modifier}" {attrs}>' + _icon(icon)
                   + f'<span class="diagnosis-label"><small>{question}</small><strong>{title}</strong></span><span class="diagnosis-arrow" aria-hidden="true">→</span></{tag}>')
    return result + '</div>'


def apply_diagnosis_copy(document):
    spans = _ElementSpans(document, 'diagnosis-guide-row').spans
    if len(spans) != 1:
        raise ValueError('Expected one diagnosis button group')
    start, end = spans[0]
    source = BeautifulSoup(document[start:end], 'html.parser')
    if not any(a['href'].rstrip('/') == '/ai-agent-readiness' for a in source.select('a[href]')):
        raise ValueError('Expected the existing AI readiness destination')
    replacement = _buttons()
    document = document[:start] + document[end:]
    if _ElementSpans(document, 'focus-hero-copy').spans:
        document = _place_in_hero(document, replacement)
    else:
        document = document[:start] + replacement + document[start:]
    pattern = r'<style id="diagnosis-copy-style">.*?</style>'
    if re.search(pattern, document, flags=re.S):
        document = re.sub(pattern, lambda _: STYLE, document, flags=re.S)
    else:
        document = document.replace('</head>', STYLE + '\n</head>', 1)
    return apply_glass_hero(document)


def _one(document, class_name):
    spans = _ElementSpans(document, class_name).spans
    if len(spans) != 1:
        raise ValueError(f'Expected one {class_name}')
    return spans[0]


def _place_in_hero(document, diagnosis):
    start, end = _one(document, 'focus-trust')
    trust = document[start:end]
    document = document[:start] + document[end:]
    _, lead_end = _one(document, 'focus-lead')
    document = document[:lead_end] + trust + document[lead_end:]
    start, end = _one(document, 'focus-actions')
    actions = document[start:end]
    for name in ('secondary', 'hero-text-link', 'hero-diagnose-cta'):
        for a, b in reversed(_ElementSpans(actions, name).spans):
            actions = actions[:a] + actions[b:]
    assert actions.endswith('</div>')
    actions = actions[:-6] + diagnosis + '</div>'
    document = document[:start] + actions + document[end:]
    for class_name, element_id in [('home-learning-links', ''), ('', 'restored-hero-image')]:
        for a, b in reversed(_ElementSpans(document, class_name, element_id=element_id).spans):
            document = document[:a] + document[b:]
    return document
