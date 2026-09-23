"""Remove only homepage teaser descriptions; keep destinations and prices."""
import re

def compact_home(text):
    classes = r'(?:readiness-guide__summary|focus-section-lead|pf-desc|pf-description)'
    text = re.sub(r'<p\b[^>]*class=([\"\x27])'+classes+r'\1[^>]*>.*?</p>', '', text, flags=re.S)
    text = re.sub(r'<div class=([\"\x27])pf-sum\1>.*?</div>', '', text, flags=re.S)
    return text
