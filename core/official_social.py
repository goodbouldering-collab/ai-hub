"""Render only owner-approved, profile-verified social destinations."""
import html
import json
from pathlib import Path

def render_official_social():
    entries = json.loads((Path(__file__).resolve().parents[1] / 'config/official-social.json').read_text(encoding='utf-8'))
    links = []
    for entry in entries:
        if not entry.get('verified') or not entry['url'].startswith('https://'):
            raise ValueError('Only verified HTTPS profiles may be published')
        links.append(f"<a href='{html.escape(entry['url'], quote=True)}' target='_blank' rel='noopener noreferrer'>{html.escape(entry['name'])}</a>")
    return "<nav class='footer-nav' aria-label='AI相談の公式SNS' id='official-social'><span class='footer-nav-head'>AI相談の発信</span>" + ''.join(links) + '</nav>'
