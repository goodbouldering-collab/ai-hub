"""Current art direction: contextual photographic work stories and the selected portrait."""
import re
PREFIX='/design-system/studio/images/'
EDITORIAL_VERSION='20260926-contextual'
PORTRAIT='/img/speaker-portrait-painting.webp'
ART_ALTS={'soft-hero': '商品のアイデアを、AIとともに販売ページと実物へつなげる制作風景のイメージ', 'soft-agent': '商品の下書きから告知物を作り、仕上がりを確認するAIエージェント活用のイメージ', 'soft-personal': '相談者の仕事を整理し、AIで取り組む最初の一歩を選ぶ個別相談のイメージ', 'soft-code': 'コードの変更と予約ページを比較し、スマートフォンでも動作を確かめるイメージ', 'soft-support': '業務を段階的に改善し、組織で使える手順書を残す伴走支援のイメージ', 'soft-salon': '音声で実践を共有し、次に取り組むことを決めるオンラインサロンのイメージ', 'soft-site': '店舗の予約ページから実際の制作依頼につながるAIアプリサイトのイメージ', 'soft-prepare': '告知物や仕事の数字を持ち寄り、相談する課題を選ぶ準備のイメージ', 'soft-try': '試作した予約画面を操作し、受付結果を確かめるイメージ', 'soft-keep': '完成した告知物とうまくいった手順を、次回使える形で保存するイメージ', 'soft-login': '記事や動画、予定を一つの作業画面に整理した管理スペースのイメージ', 'lesson-agent': 'AIが修正した商品説明の変更箇所を確認し、安全に進める練習のイメージ', 'lesson-practice': '散らばった仕事メモを、短時間で使える一日の予定に整理する実践のイメージ', 'lesson-rag': '許可された資料の該当箇所とAIの回答を照合するRAG活用のイメージ', 'lesson-site': '必要な予約機能を選び、店舗サイトの画面へ具体化するイメージ', 'lesson-salon': '今週の成果と疑問を振り返り、音声交流から次の行動を決めるイメージ', 'lesson-climbing': 'クライミングの知識をAIでスライドと配布資料へ展開し、内容を確認するイメージ', 'lesson-coding': '見積もり計算ツールの設計案、コード、動作結果を比べるコーディング実践のイメージ'}
LESSONS={
 '/lectures/assets/covers/2026-04-ai-kihon.png':('lesson-agent', ART_ALTS['lesson-agent']),
 '/lectures/assets/covers/2026-04-ai-kangaekata.png':('lesson-practice', ART_ALTS['lesson-practice']),
 '/lectures/assets/covers/2026-06-ai-agent-rag-design.png':('lesson-rag', ART_ALTS['lesson-rag']),
 '/lectures/assets/covers/2026-08-ai-app-site-consult-sheet.png':('lesson-site', ART_ALTS['lesson-site']),
 '/lectures/assets/covers/2026-07-ai-online-salon-practice.png':('lesson-salon', ART_ALTS['lesson-salon']),
 '/lectures/assets/covers/2026-05-climbing-history.png':('lesson-climbing', ART_ALTS['lesson-climbing']),
 '/img/course-path-coding.webp':('lesson-coding', ART_ALTS['lesson-coding']),
}
def attr(tag,name,value):
    pattern=rf'\b{re.escape(name)}\s*=\s*([\"\']).*?\1'
    replacement=f'{name}="{value}"'
    return re.sub(pattern,lambda _:replacement,tag,count=1,flags=re.S) if re.search(pattern,tag,re.S) else tag[:-1]+' '+replacement+'>'
def decorate_art_direction(text):
    text=re.sub(r'(editorial\.css\?v=)[a-zA-Z0-9-]+',lambda m:m[1]+EDITORIAL_VERSION,text)
    def image(match):
        tag=match[0]
        src=re.search(r'\bsrc=[\"\']([^\"\']+)',tag)
        if not src:return tag
        path=src[1].split('?')[0]
        if path in {PREFIX+'soft-mentor.webp',PREFIX+'soft-profile.webp','/img/speaker-anime.png','/img/speaker-portrait-v2.webp'}:
            for k,v in {'src':PORTRAIT,'alt':'AI相談講師 由井辰美の水彩風ポートレート','width':'1254','height':'1254'}.items():tag=attr(tag,k,v)
            style=re.search(r'\bstyle=([\"\'])(.*?)\1',tag,re.S)
            tag=attr(tag,'style',(style[2].rstrip(';')+';' if style else '')+'object-fit:cover!important')
        elif path in LESSONS:
            name,alt=LESSONS[path]
            for k,v in {'src':PREFIX+name+'.webp','alt':alt,'width':'1536','height':'1024'}.items():tag=attr(tag,k,v)
        current=re.search(r'\bsrc=[\"\x27]([^\"\x27]+)',tag)[1].split('?')[0]
        if re.fullmatch(re.escape(PREFIX)+r'(?:soft-(?:hero|agent|personal|code|support|salon|site|prepare|try|keep|login)|lesson-[a-z]+)\.webp',current):
            tag=attr(tag,'src',current+'?v='+EDITORIAL_VERSION)
            name=current.rsplit('/',1)[1].removesuffix('.webp')
            if name in ART_ALTS:tag=attr(tag,'alt',ART_ALTS[name])
        return tag
    return re.sub(r'<img\b[^>]*>',image,text)
