"""Render only owner-approved, profile-verified social destinations."""
import html
import json
import re
from pathlib import Path

SOCIAL_CSS = """<style id='official-social-style'>
#official-social{display:flex;align-items:center;justify-content:flex-end;gap:16px;max-width:1200px;margin:0 auto;padding:10px 24px;box-sizing:border-box;scroll-margin-top:90px;color:#315f5a;font-family:inherit}
#official-social .social-caption{font-size:12px;font-weight:600;letter-spacing:.04em;white-space:nowrap}
#official-social .social-links{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
#official-social a{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-height:44px;padding:0 13px;box-sizing:border-box;border:1px solid #d5e4df;border-radius:24px;background:#fff;color:#244f49;font-size:12px;font-weight:600;text-decoration:none;line-height:1;white-space:nowrap;transition:background .15s,border-color .15s}
#official-social a:hover{background:#e9f3ee;border-color:#609a89}
#official-social a:focus-visible{outline:3px solid #267566;outline-offset:3px}
#official-social svg{width:17px;height:17px;fill:currentColor;flex:none}
@media(max-width:600px){#official-social{padding:8px 12px;gap:6px;align-items:flex-start;flex-direction:column}#official-social .social-caption{font-size:11px}#official-social .social-links{gap:4px;flex-wrap:nowrap;max-width:100%;overflow-x:auto}#official-social a{padding:6px 3px;font-size:9px;gap:4px;flex-direction:column;min-width:44px;min-height:52px;flex-shrink:0}}
@media(prefers-reduced-motion:reduce){#official-social a{transition:none}}
</style>"""

def render_official_social():
    entries = json.loads((Path(__file__).resolve().parents[1] / 'config/official-social.json').read_text(encoding='utf-8'))
    links = []
    for entry in entries:
        if not entry.get('verified') or not entry['url'].startswith('https://'):
            raise ValueError('Only verified HTTPS profiles may be published')
        icon_name = {'X':'x', 'note':'note', 'Instagram':'instagram', 'Threads':'threads', 'Facebook':'facebook', 'YouTube':'youtube', 'TikTok':'tiktok'}[entry['name']]
        icon = (Path(__file__).resolve().parents[1] / f'site/static/icons/social/{icon_name}.svg').read_text(encoding='utf-8')
        icon = re.sub(r'<title>.*?</title>', '', icon).replace('role="img"', 'aria-hidden="true" focusable="false"')
        name = html.escape(entry['name'])
        links.append(f"<a href='{html.escape(entry['url'], quote=True)}' target='_blank' rel='noopener noreferrer' aria-label='{name}のAI相談（新しいタブで開く）'>{icon}<span>{name}</span></a>")
    return SOCIAL_CSS + "<nav aria-label='AI相談の公式SNS' id='official-social'><span class='social-caption'>AI相談の発信</span><div class='social-links'>" + ''.join(links) + '</div></nav>'
