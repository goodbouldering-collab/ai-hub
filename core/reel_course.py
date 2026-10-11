"""Add the reel workshop without rewriting the other course cards."""
from html import escape
from pathlib import Path
import json
import re

from core.editorial_feed import _ElementSpans

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- BEGIN:REEL_COURSE -->'
END = '<!-- END:REEL_COURSE -->'


def course_data():
    data = json.loads((ROOT / 'config/reel-course.json').read_text(encoding='utf-8'))
    assert sum(row['minutes'] for row in data['curriculum']) == data['duration_minutes'] == 120
    assert data['price_yen'] == 8800
    assert data['square']['item_id'] and data['square']['booking_url'].endswith('/' + data['square']['item_id'])
    return data


def render_course():
    c = course_data()
    curriculum = ''.join(
        f'<li><strong>{escape(row["title"])}（{row["minutes"]}分）</strong><span>{escape(row["detail"])}</span></li>'
        for row in c['curriculum']
    )
    return (
        START + '<article class="compact-course-card offer-card" id="reel-course" '
        'data-editorial-course="20261011" aria-labelledby="reel-course-title">'
        f'<img class="compact-course-visual" data-reel-course-visual="true" src="{escape(c["image"])}" alt="{escape(c["image_alt"])}" '
        'width="1536" height="1024" loading="lazy" decoding="async">'
        '<div class="editorial-course-lead"><div class="offer-role-row offer-role-row--course">'
        '<div class="offer-role-copy"><span class="offer-role-badge">学ぶ</span><span class="offer-role-note">リール実践</span></div></div>'
        f'<div class="compact-course-heading"><h3 id="reel-course-title">{escape(c["name"])}</h3>'
        '<span class="offer-audience" aria-label="対象：Codex経験者"><span class="offer-audience-label">対象</span>'
        '<strong>Codex経験者</strong></span></div>'
        f'<div class="compact-course-meta"><strong>{escape(c["price_label"])}</strong><span>2時間（120分）</span></div></div>'
        f'<div class="studio-course-body"><p><strong>{escape(c["tagline"])}</strong></p><p>{escape(c["description"])}</p>'
        f'<p class="course-booking-format">{escape(c["audience"])}</p><div class="compact-course-tail">'
        '<details class="compact-course-details"><summary>2時間の内容・持ち物を見る</summary>'
        f'<p class="compact-course-details-lead">{escape(c["outcome"])}</p><ul>{curriculum}'
        f'<li><strong>持ち物・事前準備</strong><span>{escape(c["preparation"])}</span></li>'
        f'<li><strong>投稿の確認</strong><span>{escape(c["posting_note"])}</span></li>'
        '<li><strong>参加方法</strong><span>Squareでご希望の日時と、来店（グッぼる）またはオンライン（LINE通話）を選んでください。</span></li></ul></details>'
        f'<a class="offer-action compact-course-action" href="{escape(c["square"]["booking_url"])}" target="_blank" rel="noopener">reel自動投稿講座を予約 →</a>'
        f'<p class="compact-course-material-row"><a class="compact-course-material" href="{escape(c["reference_url"])}" target="_blank" rel="noopener">参考動画でイメージを見る →</a></p>'
        '</div></div></article>' + END
    )


def apply_reel_course(document):
    c = course_data()
    card = render_course()
    if START in document:
        assert document.count(START) == document.count(END) == 1
        document = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: card, document, flags=re.S)
    else:
        grids = _ElementSpans(document, 'compact-course-grid').spans
        if not grids:
            raise ValueError('Course grid missing')
        # The menu groups basic courses first and advanced courses second.
        start = grids[-1][0]
        insert_at = document.index('>', start) + 1
        document = document[:insert_at] + card + document[insert_at:]
    document = document.replace('講習・相談・制作の全6メニュー', '講習・相談・制作の全7メニュー')
    schema = {
        '@context': 'https://schema.org', '@type': 'Course',
        '@id': 'https://aiclimb.aiclimb.workers.dev/#course-reel',
        'name': c['name'], 'description': c['description'], 'inLanguage': 'ja',
        'url': 'https://aiclimb.aiclimb.workers.dev/#reel-course',
        'provider': {'@id': 'https://aiclimb.aiclimb.workers.dev/#business'},
        'timeRequired': 'PT2H', 'coursePrerequisites': c['audience'],
        'teaches': [row['title'] for row in c['curriculum']],
        'offers': {'@type': 'Offer', 'price': '8800', 'priceCurrency': 'JPY', 'url': c['square']['booking_url']},
    }
    tag = '<script id="reel-course-schema" type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
    pattern = r'<script\b[^>]*id=["\x27]reel-course-schema["\x27][^>]*>.*?</script>'
    if re.search(pattern, document, re.S):
        document = re.sub(pattern, lambda _: tag, document, flags=re.S)
    else:
        assert document.count('</head>') == 1
        document = document.replace('</head>', tag + '</head>')
    return document
