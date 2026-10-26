"""One course specification shared by the website and the existing Square service."""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def course_data():
    c = json.loads((ROOT / 'config/voice-memo-course.json').read_text(encoding='utf-8'))
    assert sum(x['minutes'] for x in c['curriculum']) == c['duration_minutes'] == 120
    assert c['price_yen'] == 8800
    assert c['square']['booking_url'].endswith('/' + c['square']['item_id'])
    return c


def square_description(c):
    parts = [c['tagline'], c['description'], '【対象】\n' + c['audience'],
             '【メリット】\n' + '\n'.join(x['title'] + '：' + x['detail'] for x in c['benefits']),
             '【120分の内容】\n' + '\n'.join(f"{x['minutes']}分｜{x['title']}：{x['detail']}" for x in c['curriculum']),
             '【受講後にできること・目標】\n' + '\n'.join(c['outcomes']),
             '【持ち物】\n' + c['preparation'], c['scope_note'], '受講料：8,800円／個別・120分']
    return '\n\n'.join(parts)


def render_course(c):
    def rows(items):
        return ''.join('<li><strong>' + escape(x['title']) + '</strong><span>' + escape(x['detail']) + '</span></li>' for x in items)
    curriculum = [dict(title=f"{x['title']}（{x['minutes']}分）", detail=x['detail']) for x in c['curriculum']]
    outcomes = ''.join('<li>' + escape(x) + '</li>' for x in c['outcomes'])
    return (
        '<article class="compact-course-card offer-card" id="voice-memo-course" data-editorial-course="20261011" aria-labelledby="voice-memo-course-title">'
        f'<img class="compact-course-visual" src="{escape(c["image"])}" alt="{escape(c["image_alt"])}" width="1536" height="1024" loading="lazy" decoding="async">'
        '<div class="editorial-course-lead"><div class="offer-role-row offer-role-row--course"><div class="offer-role-copy"><span class="offer-role-badge">学ぶ</span><span class="offer-role-note">音声活用・アプリ制作</span></div></div>'
        f'<div class="compact-course-heading"><h3 id="voice-memo-course-title">{escape(c["name"])}</h3><span class="offer-audience" aria-label="受講人数：個別"><span class="offer-audience-label">受講人数</span><strong>個別</strong></span></div>'
        '<div class="compact-course-meta"><strong>8,800円</strong><span>120分</span></div></div>'
        f'<div class="studio-course-body"><p><strong>{escape(c["tagline"])}</strong></p><p>{escape(c["description"])}</p>'
        f'<p class="course-booking-format">{escape(c["audience"])}</p><div class="compact-course-tail">'
        f'<details class="compact-course-details"><summary>メリット・120分の内容を見る</summary><ul>{rows(c["benefits"])}</ul><p class="compact-course-details-lead">当日の流れ</p><ul>{rows(curriculum)}</ul>'
        f'<p><strong>持ち物</strong>：{escape(c["preparation"])}</p><p>{escape(c["scope_note"])}</p></details>'
        f'<details class="compact-course-details"><summary>受講後にできることを見る</summary><p>以下は講座で目指す到達点です。</p><ul>{outcomes}</ul></details>'
        f'<a class="offer-action compact-course-action" href="{escape(c["square"]["booking_url"])}" target="_blank" rel="noopener">AI音声メモ講座を予約 →</a>'
        f'<p class="compact-course-material-row"><a class="compact-course-material" href="{escape(c["reference_url"])}">ブログで制作例を見る →</a></p></div></div></article>'
    )


def apply_voice_memo_course(document):
    c = course_data()
    pattern = r'<article\b[^>]*class=[\x27"][^\x27"]*compact-course-card[^\x27"]*[\x27"][^>]*>.*?</article>'
    found = [m for m in re.finditer(pattern, document, re.S) if c['square']['item_id'] in m[0]]
    if not found:
        return document
    assert len(found) == 1, 'Expected exactly one existing Square course'
    m = found[0]
    document = document[:m.start()] + render_course(c) + document[m.end():]
    def schema(match):
        tag = match[0]; start = tag.index('>') + 1; end = tag.rindex('</script>')
        data = json.loads(tag[start:end])
        def visit(value, course=False):
            if isinstance(value, dict):
                course = course or any(s in str(value.get('name', '')) for s in ('AIコーディング', 'AI音声メモ'))
                if course and 'name' in value and value.get('@type') in ('Course', 'Service', 'Product', 'Offer'):
                    value['name'] = c['name']
                    if 'description' in value: value['description'] = c['description']
                    value.pop('review', None); value.pop('aggregateRating', None)
                    if value.get('@type') == 'Course':
                        value['teaches'] = [x['title'] for x in c['curriculum']]
                        value['coursePrerequisites'] = c['audience']
                        value['timeRequired'] = 'PT2H'
                if value.get('@type') == 'WebPage' and isinstance(value.get('description'), str):
                    value['description'] = value['description'].replace('AIコーディング講習', 'AI音声メモ講座')
                for key, item in list(value.items()):
                    if course and key in ('price', 'lowPrice', 'highPrice'):
                        value[key] = '8800' if isinstance(item, str) else 8800
                    else: visit(item, course)
            elif isinstance(value, list):
                for item in value: visit(item, course)
        visit(data)
        return tag[:start] + json.dumps(data, ensure_ascii=False) + tag[end:]
    return re.sub(r'<script[^>]*type=[\x27"]application/ld\+json[\x27"][^>]*>.*?</script>', schema, document, flags=re.S)
