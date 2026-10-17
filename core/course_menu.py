"""Keep the public course menu, pricing and extension guidance together."""
import re

from core.editorial_feed import _ElementSpans
from core.reel_course import apply_reel_course
from core.square_menu import apply_square_menu

NOTICE = "内容により2〜3時間が目安。延長は当日の空き状況に応じて相談可。表示料金は基本時間分です。"

def compact_time_note(document: str) -> str:
    spans = _ElementSpans(document, element_id='course-time-note').spans
    if len(spans) != 1:
        raise ValueError('Expected one course time note')
    start, end = spans[0]
    note = f'<aside class="course-time-note" id="course-time-note" aria-label="受講時間の目安"><p>{NOTICE}</p></aside>'
    document = document[:start] + note + document[end:]
    style = '<style id="compact-course-time-note-style">#packages #course-time-note{margin:12px 0 28px;padding:0 4px;border:0;border-radius:0;background:none;line-height:1.7}#packages #course-time-note p{font-size:13px;color:#52686b}</style>'
    import re
    document = re.sub(r'<style id="compact-course-time-note-style">.*?</style>', '', document, flags=re.S)
    return document.replace('</head>', style + '</head>', 1)

CSS = """
#packages .course-menu-group-title{margin:28px 0 16px;font-size:clamp(20px,2.5vw,27px);line-height:1.5;color:#263d4a}
body #packages .compact-course-grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:24px!important;align-items:stretch!important;max-width:none!important}
body #packages .compact-course-grid>.compact-course-card{grid-column:auto!important;grid-row:auto!important;margin:0!important;transform:none!important;min-width:0}
#packages .course-time-note{margin:22px 0 36px;padding:20px 24px;border:1px solid #d9dfd7;border-radius:18px;background:#f7f8f2;color:#263d4a;line-height:1.9}
#packages .course-time-note h3{margin:0 0 8px;font-size:18px}
#packages .course-time-note p{margin:0;font-size:15px;color:inherit}
#packages .course-booking-format{font-weight:600;color:#334e5b;line-height:1.7}
@media(max-width:680px){body #packages .compact-course-grid{grid-template-columns:minmax(0,1fr)!important;gap:18px!important}#packages .course-time-note{padding:18px}}
"""


def _salon_last(document: str) -> str:
    """Move the complete salon card last without changing any card contents."""
    for start, end in reversed(_ElementSpans(document, 'compact-course-grid').spans):
        grid = document[start:end]
        spans = _ElementSpans(grid, 'compact-course-card').spans
        for index, (card_start, card_end) in enumerate(spans):
            card = grid[card_start:card_end]
            if re.search(r"\bid=['\"]seven-day-courses['\"]", card.split('>', 1)[0]):
                if index != len(spans) - 1:
                    last_end = spans[-1][1]
                    grid = (grid[:card_start] + grid[card_end:last_end]
                            + card + grid[last_end:])
                    document = document[:start] + grid + document[end:]
                break
    return document


def apply_course_menu(document: str) -> str:
    document = document.replace("AI個別講習", "AI個別相談")
    document = document.replace("個別講習を予約", "個別相談を予約")
    document = document.replace(">個別講習<", ">個別相談<")
    if 'id="course-time-note"' in document:
        return compact_time_note(apply_square_menu(apply_reel_course(_salon_last(document))))
    pattern = r"<div class=['\"]compact-course-grid['\"]>(.*?)</article></div>"
    match = re.search(pattern, document, re.S)
    if not match:
        raise ValueError("Course menu grid missing")
    cards = re.findall(r"<article\b.*?</article>", match.group(0), re.S)
    if len(cards) != 6:
        raise ValueError(f"Expected six course cards, got {len(cards)}")
    assert "AIエージェント講習" in cards[0] and "AI個別相談" in cards[1]
    formats = ["毎週水曜・複数人で受講（料金はお一人分）", "ご希望の時間を指定・マンツーマン"]
    for i, label in enumerate(formats):
        cards[i], count = re.subn(
            r"(<div class=['\"]compact-course-meta['\"]>.*?</div>)",
            lambda m: m[0] + f'<p class="course-booking-format">{label}</p>', cards[i], count=1, flags=re.S)
        assert count == 1
    cards[0] = cards[0].replace("<strong>少数</strong>", "<strong>複数人</strong>")
    cards[1] = cards[1].replace("<strong>個別</strong>", "<strong>お一人</strong>")
    cards[0] = cards[0].replace("受講人数：少数", "受講人数：複数人")
    cards[1] = cards[1].replace("受講人数：個別", "受講人数：お一人")
    replacement = (
        '<h3 class="course-menu-group-title">講習・個別相談を選ぶ</h3>'
        '<div class="compact-course-grid">' + ''.join(cards[:2]) + '</div>'
        '<aside class="course-time-note" id="course-time-note" aria-labelledby="course-time-title">'
        '<h3 id="course-time-title">所要時間と当日の延長について</h3>'
        f'<p>{NOTICE}</p></aside>'
        '<h3 class="course-menu-group-title">さらに学ぶ・継続する・制作を任せる</h3>'
        '<div class="compact-course-grid">' + ''.join(cards[2:]) + '</div>'
    )
    document = document[:match.start()] + replacement + document[match.end():]
    if '</head>' in document:
        document = document.replace('</head>', f'<style id="course-menu-style">{CSS}</style></head>', 1)
    return compact_time_note(apply_square_menu(apply_reel_course(_salon_last(document))))
