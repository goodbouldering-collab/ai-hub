"""Keep works and learning resources together without rewriting their contents."""
from pathlib import Path
import re
from core.editorial_feed import _ElementSpans

ROOT = Path(__file__).resolve().parents[1]


def apply_compact_cards(document):
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
    return document.replace('</head>', '<style id="compact-cards-style">' + css + '</style></head>')
