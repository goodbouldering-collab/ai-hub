"""Reproducible editorial charts; values live in the cited evidence JSON."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/blog/2026-09-28-orca-evidence/data.json'
D = json.loads(DATA.read_text(encoding='utf-8'))
font = Path('C:/Windows/Fonts/meiryo.ttc')
fontManager.addfont(str(font))
plt.rcParams.update({'font.family': FontProperties(fname=str(font)).get_name(),
                     'svg.fonttype': 'path', 'axes.unicode_minus': False})
BG, INK, AQUA, GOLD, PURPLE = '#F4F0E7', '#142939', '#087F83', '#C17A21', '#7767AD'

def text(ax,x,y,s,size=22,color=INK,ha='left',weight='normal',**kw):
    return ax.text(x,y,s,fontsize=size,color=color,ha=ha,va='center',weight=weight,**kw)

def box(ax,x,y,w,h,fill,edge=None):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.015,rounding_size=0.018',
                              facecolor=fill,edgecolor=edge or fill,linewidth=1.5))

def arrow(ax,a,b,color=AQUA):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=24,
                               linewidth=2.5,color=color,connectionstyle='arc3'))

def base(n,title,sub,dark=False):
    bg=INK if dark else BG
    fig=plt.figure(figsize=(14,9),facecolor=bg)
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    fg='#F4F0E7' if dark else INK
    text(ax,.065,.94,f'ORCA / FIELD NOTES 0{n}',13,'#63D5C7' if dark else AQUA,weight='bold')
    text(ax,.065,.855,title,31,fg,weight='bold')
    text(ax,.065,.785,sub,17,'#B5C6CE' if dark else '#536571')
    return fig,ax

def save(fig,n):
    stem=f'blog-orca-ade-section-0{n}-evidence-20260928'
    out=ROOT/'site/static/img';out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/(stem+'.png'),dpi=120,facecolor=fig.get_facecolor())
    vectors=ROOT/'docs/blog/2026-09-28-orca-evidence/charts'
    vectors.mkdir(parents=True,exist_ok=True)
    svg=vectors/(stem+'.svg')
    fig.savefig(svg,facecolor=fig.get_facecolor())
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)

def main():
    op=D['operator']; community=D['community']; recipe=D['parallel_recipe']
    assert op['registered_repositories']==33 and op['recloned_repositories']==0 and op['new_worktrees']==0
    assert community['sessions_approx']==15 and recipe['agent_count']==len(recipe['agents'])==3
    fig,ax=base(1,'33件の入口を、ひとつに。','運営者の導入記録  |  2026.09.27 / Orca 1.4.212')
    plot=fig.add_axes([.31,.255,.57,.43],facecolor=BG)
    vals=[op['registered_repositories'],op['recloned_repositories'],op['new_worktrees']]
    labels=['既存プロジェクト登録','再ダウンロード','新規 worktree 作成']
    plot.barh([2,1,0],vals,color=[AQUA,GOLD,PURPLE],height=.47,zorder=3)
    plot.set(xlim=(0,40),ylim=(-.65,2.65),yticks=[],xticks=[0,10,20,30,40])
    plot.tick_params(axis='x',labelsize=15,colors='#536571',length=0,pad=10)
    plot.xaxis.grid(True,color='#D6DCD8',linewidth=1);plot.set_axisbelow(True)
    for spine in plot.spines.values():spine.set_visible(False)
    for y,v,label in zip([2,1,0],vals,labels):
        plot.text(-2,y,label,ha='right',va='center',fontsize=19,color=INK)
        plot.text(v+1,y,str(v),ha='left',va='center',fontsize=32,weight='bold',color=INK)
        if v==0:plot.plot(0,y,'o',ms=8,color=INK,zorder=4)
    text(ax,.89,.208,'件',16)
    box(ax,.065,.092,.87,.08,'#E1E8DD')
    text(ax,.09,.132,'元のフォルダを参照。引っ越し作業は増やさなかった。',20,weight='bold')
    text(ax,.065,.044,'記録：運営者の導入結果・登録一覧を照合 / 同時実行数・速度の比較ではありません。',12,'#536571')
    save(fig,1)

    fig,ax=base(2,'約15の仕事を、見失わない。','海外利用者1人の報告  |  trader_tick / Reddit',True)
    text(ax,.075,.60,'約',28,'#F4F0E7')
    text(ax,.15,.60,str(community['sessions_approx']),86,'#69DED0',weight='bold')
    text(ax,.077,.46,'同時に進めるセッション',20,'#F4F0E7')
    for i in range(community['sessions_approx']):
        ax.scatter(.095+(i%5)*.06,.34-(i//5)*.075,s=350,c='#69DED0',marker='o')
    text(ax,.077,.11,'● 1点＝1セッション（概数）',13,'#B5C6CE')
    for x,num,label in [(.52,community['computers'],'台のPC'),(.755,community['repositories'],'リポジトリ')]:
        box(ax,x,.465,.18,.22,'#203D4C')
        text(ax,x+.09,.60,str(num),48,'#F4F0E7',ha='center',weight='bold')
        text(ax,x+.09,.505,label,17,'#B5C6CE',ha='center')
    text(ax,.52,.355,'1リポジトリあたり',18,'#F4F0E7')
    x0,x1=.54,.90
    ax.plot([x0,x1],[.245,.245],color='#4C6571',lw=3)
    for i in range(7):
        x=x0+(x1-x0)*i/6
        ax.plot([x,x],[.233,.257],color='#718995',lw=1)
        text(ax,x,.20,str(i),12,'#B5C6CE',ha='center')
    lo,hi=community['sessions_per_repository_range']
    ax.plot([x0+(x1-x0)*lo/6,x0+(x1-x0)*hi/6],[.245,.245],lw=10,c='#F3B760',solid_capstyle='round')
    text(ax,.72,.295,f'{lo}〜{hi} セッション',24,'#F3B760',ha='center',weight='bold')
    text(ax,.065,.044,'出典：Reddit「Orca ADE is incredible」/ 自己申告。平均・上限・速度を示す図ではありません。',12,'#B5C6CE')
    save(fig,2)

    fig,ax=base(3,'3つの案を、並べて選ぶ。','公式レシピの流れ  |  速度を表すグラフではありません')
    box(ax,.34,.645,.32,.076,INK)
    text(ax,.50,.684,'同じ依頼・同じ出発点',22,BG,ha='center',weight='bold')
    positions=[.08,.37,.66]
    colors=[AQUA,GOLD,PURPLE]
    for x,name,c in zip(positions,recipe['agents'],colors):
        arrow(ax,(.5,.625),(x+.13,.555),c)
        box(ax,x,.345,.26,.19,'#FFFFFF',c)
        text(ax,x+.13,.475,name,21,c,ha='center',weight='bold')
        text(ax,x+.13,.413,'別々の作業フォルダ',16,ha='center')
        text(ax,x+.13,.368,'worktree',13,'#536571',ha='center')
        arrow(ax,(x+.13,.325),(.5,.245),c)
    box(ax,.19,.105,.62,.12,INK)
    text(ax,.50,.18,'人が比較・テスト → 1案を採用',26,BG,ha='center',weight='bold')
    text(ax,.50,.129,'見やすさ / 変更内容 / 動作',15,'#B5C6CE',ha='center')
    text(ax,.065,.044,'出典：Orca Docs「Race three agents on the same task」/ 3は使用例の数。製品上限ではありません。',12,'#536571')
    save(fig,3)

    fig,ax=base(4,'「ここ」を指すと、情報が渡る。','Design Mode  |  公式仕様にもとづく概念図・実画面ではありません',True)
    box(ax,.075,.25,.38,.435,'#F4F0E7')
    ax.add_patch(Rectangle((.075,.62),.38,.05,facecolor='#DCE3DF',edgecolor='none'))
    for x in [.101,.119,.137]:ax.scatter(x,.645,s=20,c='#96A4A7')
    text(ax,.108,.552,'申し込みページ',20,INK,weight='bold')
    ax.plot([.11,.38],[.482,.482],color='#CAD5D5',lw=8,solid_capstyle='round')
    ax.plot([.11,.315],[.442,.442],color='#CAD5D5',lw=8,solid_capstyle='round')
    box(ax,.108,.295,.23,.072,AQUA)
    text(ax,.223,.331,'申し込む',21,'white',ha='center',weight='bold')
    ax.add_patch(Rectangle((.093,.28),.26,.102,fill=False,edgecolor='#E0A146',linewidth=2,linestyle='--'))
    arrow(ax,(.395,.242),(.318,.302),'#F3B760')
    text(ax,.10,.177,'直したい部品をクリック',19,'#F4F0E7')
    for y,name,desc,c in [(.565,'HTML','構造','#69DED0'),(.395,'CSS','色・余白・文字','#F3B760'),(.225,'IMAGE','切り抜き画像','#B9ADF0')]:
        arrow(ax,(.48,.40),(.585,y+.045),c)
        box(ax,.61,y,.30,.10,'#203D4C')
        text(ax,.635,y+.051,name,22,c,weight='bold')
        text(ax,.89,y+.051,desc,16,'#F4F0E7',ha='right')
    text(ax,.61,.145,'＋ 変更の希望をAIへ',20,'#F4F0E7',weight='bold')
    text(ax,.065,.063,'出典：Orca Docs「Design Mode」/ 基本の3種を図示。',12,'#B5C6CE')
    text(ax,.065,.03,'開発環境によっては、元ファイル・行番号も付加されます。',12,'#B5C6CE')
    save(fig,4)
    print(json.dumps({'charts':4,'registered':op['registered_repositories'],'sessions_approx':community['sessions_approx'],'agents':recipe['agent_count']}))

if __name__=='__main__':main()
