"""Short prompts within the existing compact diagnosis card footprint."""
import re

PROMPTS = {'readiness-guide-title': 'AI使えてますか？', 'seo-llmo-guide-title': 'AIに選ばれるサイトって？'}
STYLE = '''<style id="diagnosis-copy-style">
body.studio-editorial.studio-home .diagnosis-guide-row .readiness-guide__inner { padding-block:18px!important; }
.diagnosis-guide-row .offer-role-row { margin-bottom:0!important; }
body.studio-editorial.studio-home .diagnosis-guide-row .readiness-guide__title { margin-top:0!important; }
.diagnosis-guide-row .diagnosis-guide-prompt { margin:0!important; font-size:13px; line-height:19px; font-weight:700; color:var(--focus-blue); }
@media(max-width:520px) { body.studio-editorial.studio-home .diagnosis-guide-row .readiness-guide__inner { padding-block:14px!important; } }
</style>'''


def apply_diagnosis_copy(document):
    document = re.sub(r'<p class="diagnosis-guide-prompt">.*?</p>', '', document)
    for node_id, prompt in PROMPTS.items():
        pattern = r'(<h2\b[^>]*\bid=["\x27]'+node_id+r'["\x27][^>]*>)'
        document, count = re.subn(pattern, lambda m: '<p class="diagnosis-guide-prompt">'+prompt+'</p>'+m[1], document)
        assert count == 1, node_id
    document = re.sub(r'<style id="diagnosis-copy-style">.*?</style>\s*', '', document, flags=re.S)
    return document.replace('</head>', STYLE+'\n</head>', 1)
