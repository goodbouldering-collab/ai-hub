"""Current art direction: minimal photographic workspaces and the selected portrait."""
import re
PREFIX='/design-system/studio/images/'
EDITORIAL_VERSION='20260926-minimal'
PORTRAIT='/img/speaker-portrait-painting.webp'
ART_ALTS={'soft-hero': '自然光が差す机にノートPCと白い紙の立体を置いた制作スペース', 'soft-agent': '作業の進み具合を整理するノートPCと小さな箱', 'soft-personal': 'アイデアを描くタブレットとペン', 'soft-code': 'シンプルなWebページを映すモニター', 'soft-support': 'ノートPCと小さな建築模型を置いた制作机', 'soft-salon': '制作案を並べたタブレットと丸いテーブル', 'soft-site': '店舗ページを映すタブレットと商品パッケージ', 'soft-prepare': '相談内容を整理するノートとペン', 'soft-try': '制作物を確かめるカメラと白い試作品', 'soft-keep': '仕事の方法を残すノートPCとファイル', 'soft-login': '静かな作業スペースに置いたノートPC', 'lesson-agent': 'AIへの依頼と成果物を比較するノートPC', 'lesson-practice': '一週間の仕事を整理するタブレット', 'lesson-rag': '参照資料を確かめるバインダーとタブレット', 'lesson-site': '予約を整理するタブレットとカード', 'lesson-salon': '制作の進み具合を共有するノートPC', 'lesson-climbing': '岩を思わせるクライミングホールドとカラビナ', 'lesson-coding': 'コードとページの仕上がりを確認するノートPC'}
LESSONS={
 '/lectures/assets/covers/2026-04-ai-kihon.png':('lesson-agent', 'AIへの依頼と成果物を比較するノートPC'),
 '/lectures/assets/covers/2026-04-ai-kangaekata.png':('lesson-practice', '一週間の仕事を整理するタブレット'),
 '/lectures/assets/covers/2026-06-ai-agent-rag-design.png':('lesson-rag', '参照資料を確かめるバインダーとタブレット'),
 '/lectures/assets/covers/2026-08-ai-app-site-consult-sheet.png':('lesson-site', '予約を整理するタブレットとカード'),
 '/lectures/assets/covers/2026-07-ai-online-salon-practice.png':('lesson-salon', '制作の進み具合を共有するノートPC'),
 '/lectures/assets/covers/2026-05-climbing-history.png':('lesson-climbing', '岩を思わせるクライミングホールドとカラビナ'),
 '/img/course-path-coding.webp':('lesson-coding', 'コードとページの仕上がりを確認するノートPC'),
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
        if path==PREFIX+'soft-hero.webp':
            tag=attr(tag,'alt','自然光が差す机にノートPCと白い紙の立体を置いた制作スペース')
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
