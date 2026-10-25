"""Apply public Square service facts verified on 2026-10-14."""
import re
from core.voice_memo_course import apply_voice_memo_course

def apply_square_menu(document: str) -> str:
    document = document.replace('AI個別講習', 'AI個別相談')
    document = document.replace('個別講習を予約', '個別相談を予約')
    document = document.replace('60分・5,500円', '120分・8,800円')
    document = document.replace('60分5,500円', '120分8,800円')
    document = document.replace('AI個別相談 60分', 'AI個別相談 120分')
    document = document.replace('手順を60分で整理', '手順を120分で整理')
    document = document.replace('予約ページから60分の日時', '予約ページから120分の日時')
    def card(match):
        text = match[0]
        if 'TO3XHZT6XP3OM4QBDYMW7TZP' in text:
            text = text.replace('5,500円', '8,800円').replace('60分', '120分')
            text = re.sub(r'(<h3[^>]*>).*?(</h3>)', r'\g<1>AI個別相談120分｜AI時代のなんでも相談\2', text, count=1)
        elif 'S7GERYVDIPRV76DKXCC3WJWH' in text:
            text = re.sub(r'(<h3[^>]*>).*?(</h3>)', r'\g<1>AIコーディング講習120分｜AI時代の専門技術を伝授\2', text, count=1)
        elif 'V57YTNICA2KV2TN7ENARAVQE' in text:
            text = re.sub(r'(<h3[^>]*>).*?(</h3>)', r'\g<1>AI事業導入相談30分｜伴走できる実務導入を検討\2', text, count=1)
            text = text.replace('伴走支援を申し込む', '初回無料・30分の相談を予約')
            if '初回相談30分・無料。その後の伴走支援' not in text:
                text = re.sub(r"(<div class=['\"]compact-course-meta['\"]>)", r"<p class='course-booking-format'>初回相談30分・無料。その後の伴走支援は以下の料金・期間です。</p>\1", text, count=1)
        return text
    document = re.sub(r'<article\b[^>]*class=[\'"][^\'"]*compact-course-card[^\'"]*[\'"][^>]*>.*?</article>', card, document, flags=re.S)
    document = document.replace("bookingMeta: '診断後の入口整理'", "bookingMeta: '20分・無料'")
    document = document.replace("title: 'まずは、無料相談で入口を整理する'", "title: 'AI無料準備相談20分｜講習準備と業務導入相談'")
    document = document.replace("bookingLabel: '無料相談の日程を選ぶ'", "bookingLabel: 'AI無料準備相談を予約する'")
    document = document.replace('まずは困っている仕事を相談する</a>', 'AI無料準備相談20分を予約する</a>')
    def schema(match):
        import json
        tag = match[0]
        start, end = tag.index('>') + 1, tag.rindex('</script>')
        data = json.loads(tag[start:end])
        changed = False
        def visit(value, individual=False):
            nonlocal changed
            if isinstance(value, dict):
                individual = individual or 'AI個別相談' in str(value.get('name', ''))
                for key, item in value.items():
                    if individual and key in ('price', 'lowPrice', 'highPrice') and str(item) == '5500':
                        value[key] = '8800' if isinstance(item, str) else 8800
                        changed = True
                    else:
                        visit(item, individual)
            elif isinstance(value, list):
                for item in value:
                    visit(item, individual)
        visit(data)
        return tag[:start] + json.dumps(data, ensure_ascii=False) + tag[end:] if changed else tag
    document = re.sub(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>.*?</script>', schema, document, flags=re.S)
    return apply_voice_memo_course(document)
