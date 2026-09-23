"""Progressive, presentation-only task navigation for public and admin pages."""
import re
VERSION='20260923-focused'
ASSETS='/design-system/studio/'

def decorate_focused_ux(text, *, home=False):
    if '</head>' not in text:return text
    text=re.sub(r'<link\b[^>]*id=[\"\x27]focused-ux-style[\"\x27][^>]*>','',text)
    text=re.sub(r'<script\b[^>]*id=[\"\x27]focused-ux-script[\"\x27][^>]*>\s*</script>','',text)
    tags=f'<link id="focused-ux-style" rel="stylesheet" href="{ASSETS}focused-ux.css?v={VERSION}"><script id="focused-ux-script" defer src="{ASSETS}focused-ux.js?v={VERSION}"></script>'
    text=re.sub(r'\s*</head>',lambda _:tags+'\n</head>',text,count=1)
    if home:
        # The main headline and existing consultation/menu actions remain.
        text=re.sub(r'<aside\b[^>]*class=[\"\x27][^\"\x27]*\bhero-advantage\b[^\"\x27]*[\"\x27][^>]*>.*?</aside>','',text,flags=re.S)
    return text

def admin_hub():
    groups=[
      ('create','ブログ制作','/admin/apps/blog','記事の下書きをつくる','記事 文章 画像'),
      ('create','ブログ管理','/admin/blog','記事を編集・公開する','記事 一覧 編集 公開'),
      ('create','リール制作','/admin/apps/reel/','動画と投稿文をつくる','動画 Instagram'),
      ('create','SNS投稿','/admin/sns-post','下書きと投稿を確認する','Threads X 発信'),
      ('check','SNS分析','/admin/gubble-sns','反応から次の一手へ','数値 分析 Instagram'),
      ('check','公開ページ','/','公開中の表示を見る','サイト トップ'),
      ('organize','実行指令室','/admin/command-center','予定と指示をまとめる','予定 タスク カレンダー'),
      ('organize','AI相談','/admin/chat','考えと次の行動を整理する','チャット メモ'),
      ('organize','OPS','/ops','資料とプロンプトを探す','資料 手順 プロンプト'),
      ('check','相場羅針盤','/admin/command-center/trade','調査・計画・記録を見る','相場 市場 株 取引'),
    ]
    from html import escape
    cards=''.join(f'<a class="ux-task-card" href="{url}" data-ux-category="{group}" data-ux-keywords="{escape(keywords)}"><span><strong>{title}</strong><small>{desc}</small></span><span aria-hidden="true">↗</span></a>' for group,title,url,desc,keywords in groups)
    return f'''<main class="ux-admin-home" id="main-content"><header class="ux-admin-intro"><p>AI相談 / WORKSPACE</p><h1>今日は、何を進めますか。</h1></header>
<section class="ux-task-browser" aria-label="管理作業を選ぶ"><div class="ux-task-controls" hidden><label class="ux-search-label" for="ux-task-search">作業を探す<input id="ux-task-search" type="search" placeholder="記事、動画、予定…" autocomplete="off"></label><div class="ux-filters" role="group" aria-label="管理作業の目的"><button type="button" data-ux-filter="all" aria-pressed="true">すべて</button><button type="button" data-ux-filter="create" aria-pressed="false">つくる</button><button type="button" data-ux-filter="check" aria-pressed="false">確かめる</button><button type="button" data-ux-filter="organize" aria-pressed="false">整える</button></div></div><div class="ux-task-grid">{cards}</div><p class="ux-empty" hidden>見つかりませんでした。別の言葉で探すか、「すべて」に戻してください。</p><p class="ux-result-status" role="status" aria-live="polite"></p></section>
<footer class="ux-admin-footer"><a href="/">公開ページを見る ↗</a><a href="/admin/logout">ログアウト</a></footer></main>'''

def replace_admin_hub(text):
    if 'ux-admin-home' in text:return decorate_focused_ux(text)
    text,count=re.subn(r'<main\b[^>]*>.*?</main>',lambda _:admin_hub(),text,count=1,flags=re.S)
    assert count==1,'Expected admin main'
    return decorate_focused_ux(text)


def decorate_admin_entry(text):
    # One protected asset also serves blog subroutes: retain all existing forms.
    if 'data-ux-admin-hub' not in text:
        hub=admin_hub().replace('<main ', '<main hidden data-ux-admin-hub ', 1)
        text,count=re.subn(r'(<div class="container">)',lambda m:hub+m[0],text,count=1)
        assert count==1,'Expected protected admin container'
    return decorate_focused_ux(text)
