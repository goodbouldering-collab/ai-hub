"""Current art direction: tactile line art and the selected watercolor portrait."""
import re
PREFIX='/design-system/studio/images/'
EDITORIAL_VERSION='20260923-cyber'
PORTRAIT='/img/speaker-portrait-painting.webp'
LESSONS={
 '/lectures/assets/covers/2026-04-ai-kihon.png':('lesson-agent','AIへの依頼と成果物の確認を表す講習資料のイラスト'),
 '/lectures/assets/covers/2026-04-ai-kangaekata.png':('lesson-practice','毎週の仕事をAIで整える実践資料のイラスト'),
 '/lectures/assets/covers/2026-06-ai-agent-rag-design.png':('lesson-rag','資料を探し根拠を確かめるRAGのイラスト'),
 '/lectures/assets/covers/2026-08-ai-app-site-consult-sheet.png':('lesson-site','店舗の予約と問い合わせを支えるAIサイトのイラスト'),
 '/lectures/assets/covers/2026-07-ai-online-salon-practice.png':('lesson-salon','成果を持ち寄り学び合うオンラインサロンのイラスト'),
 '/lectures/assets/covers/2026-05-climbing-history.png':('lesson-climbing','登山から現代のジムへ続くクライミング史のイラスト'),
 '/img/course-path-coding.webp':('lesson-coding','コードの変更と成果を確かめる実践資料のイラスト'),
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
            tag=attr(tag,'alt','PCで仕事を整える人物と、透明なAI操作パネルを描いたアニメ映画風のイラスト')
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
        return tag
    return re.sub(r'<img\b[^>]*>',image,text)
