"""Keep works and learning resources together without rewriting their contents."""
from pathlib import Path
import re
from core.editorial_feed import _ElementSpans

ROOT = Path(__file__).resolve().parents[1]


def apply_compact_cards(document):
    # Frozen homepage shells also feed daily releases. Remove the retired work
    # here so rebuilding from an older shell cannot put its card back.
    for start, end in reversed(_ElementSpans(document, 'pf-card').spans):
        if '/img/portfolio/rieru-seikotsu.jpg' in document[start:end]:
            document = document[:start] + document[end:]
    spans = _ElementSpans(document, element_id='lectures').spans
    if len(spans) != 1:
        raise ValueError('Expected one learning materials section')
    start, end = spans[0]
    lectures = document[start:end]
    document = document[:start] + document[end:]
    works = _ElementSpans(document, element_id='all-works').spans
    if len(works) != 1:
        raise ValueError('Expected one works section')
    end = works[0][1]
    document = document[:end] + lectures + document[end:]
    document = re.sub(r'<style id="compact-cards-style">.*?</style>', '', document, flags=re.S)
    css = (ROOT / 'site/templates/ai-news/compact-cards.css').read_text(encoding='utf-8')
    if document.count('</head>') != 1:
        raise ValueError('Expected one document head')
    document = document.replace('</head>', '<style id="compact-cards-style">' + css + '</style></head>')
    popups = (ROOT / 'site/templates/ai-news/diagnosis-popups.html').read_text(encoding='utf-8')
    document = re.sub(r'<!-- diagnosis-popups:start -->.*?<!-- diagnosis-popups:end -->\n?', '', document, flags=re.S)
    _, end = _ElementSpans(document, element_id='diagnosis-start').spans[0]
    return document[:end] + popups + document[end:]
