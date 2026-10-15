// One registry for the dashboard, canonical URLs, legacy redirects, and view selection.
export const ROUTES = Object.freeze([
  ['blog-create','ブログ制作','create','studio','/admin/apps/blog.html'],
  ['reel','リール制作','create','studio','/admin/apps/reel.html'],
  ...[['articles','記事一覧'],['editor','記事編集'],['publish','公開確認'],['status','接続状態'],['settings','ブログ設定']].map(([view,title])=>['blog-'+view,title,'create','blog','/admin/blog/'+view,view]),
  ['sns-post','SNS投稿','create','static','/admin/sns-post'],
  ['command-center','予定・指示の概要','operations','command','/admin/command-center','dashboard'],
  ...[['calendar','カレンダー'],['tasks','タスク'],['businesses','事業一覧'],['directives','指示'],['studio','Codex連携'],['tools','検証・移行'],['trade','相場羅針盤'],['market','市場候補'],['screener','財務スクリーナー'],['security','銘柄詳細'],['trade-plan','取引プラン作成'],['trade-plans','登録プラン'],['trades','取引記録'],['market-sources','データ収集状況']].map(([view,title])=>[view,title,'operations','command','/admin/command-center/'+view,view]),
  ['gubble-sns','SNS分析','operations','static','/admin/gubble-sns'],
  ['sns-cross-media-dashboard','旧媒体ボード（設定・履歴）','operations','static','/admin/sns-cross-media-dashboard'],
  ['chat','AIに相談','operations','static','/admin/chat'],
  ['ops','運用記録・原文','materials','ops','/ops'],
    ['daily-operation','毎日の運営チェック','materials','document','/admin/materials/daily-operation'],
  ['publishing','ブログ・リール制作の進め方','materials','document','/admin/materials/publishing'],
  ['artwork','画像・資料の使い分け','materials','document','/admin/materials/artwork'],
  ['watch','収集記事','materials','watch','/watch'],
  ['migration','移行・接続状況','operations','migration','/admin/migration'],
].map(([slug,title,group,kind,legacy,view])=>Object.freeze({path:'/admin/'+slug,title,group,kind,legacy,view,archive:slug==='sns-cross-media-dashboard'})));

export const routeAt = path => ROUTES.find(route=>route.path===path);
export const OPERATION_SECTIONS = Object.freeze([
  {path:'/admin/operations/schedule',title:'予定・指示',slugs:['command-center','calendar','tasks','directives']},
  {path:'/admin/operations/business',title:'事業・分析',slugs:['businesses','gubble-sns','chat']},
  {path:'/admin/operations/trading',title:'相場・取引',slugs:['trade','market','screener','security','trade-plan','trade-plans','trades','market-sources']},
  {path:'/admin/operations/connections',title:'連携・接続',slugs:['studio','tools','migration']},
].map(section=>Object.freeze({...section,routes:Object.freeze(section.slugs.map(slug=>routeAt('/admin/'+slug)))})));
export const operationSectionAt = path => OPERATION_SECTIONS.find(section=>section.path===path||section.routes.some(route=>route.path===path)||(path==='/admin/sns-cross-media-dashboard'&&section.path==='/admin/operations/business'));
const aliases = new Map(ROUTES.filter(r=>r.path!==r.legacy).map(r=>[r.legacy,r.path]));
for(const path of ['/admin/create','/admin/blog','/admin/blog/generate','/admin/apps/blog']) aliases.set(path,'/admin/blog-create');
aliases.set('/admin/apps/reel','/admin/reel');
aliases.set('/admin/docs','/admin/ops');
for(const path of ['/admin/prompts','/ops/prompts']) aliases.set(path,'/admin/ops#sec-prompts');
aliases.set('/admin','/admin/blog-create');
for(const path of ['/admin/index.html','/admin/hub.html','/admin/index','/admin/hub']) aliases.set(path,'/admin/blog-create');
for(const route of ROUTES.filter(r=>r.kind==='document')) aliases.set(route.legacy+'.md',route.path+'.md');

export function canonicalUrl(value, base='https://admin.invalid') {
  let url; try { url=new URL(value,base); } catch { return value; }
  if(url.origin!==new URL(base).origin) return value;
  const path=url.pathname.replace(/\/+$/,'')||'/';
  let target=aliases.get(path);
  if(path==='/watch'||path.startsWith('/watch/')) {
    // HTML views use one direct child; assets retain their authenticated URL.
    const item=path.slice(7)||'index.html';
    if(!/\.[a-z0-9]+$/i.test(item)||item.endsWith('.html')) {
      target='/admin/watch';
      url.searchParams.set('path',item);
    }
  }
  if(!target) return value;
  const destination=new URL(target,url.origin);
  return destination.pathname+url.search+(url.hash||destination.hash);
}

export function rewriteNavigation(text, {studio=false}={}) {
  // Studio uses relative links both in its initial HTML and its client-side menu.
  // Keep CSS/module URLs relative to the original app directory; only views move.
  if(studio) for(const [file,target] of [['blog','/admin/blog-create'],['reel','/admin/reel']]) {
    text=text.replace(new RegExp('(["\'])\\./'+file+'\\.html\\1','g'),(_,quote)=>quote+target+quote);
    text=text.replace(new RegExp('(href=["\'])'+file+'\\.html(["\'])','g'),'$1'+target+'$2');
  }
  // Match URL literals, never /api/admin URLs or arbitrary text within an API path.
  return text.replace(/(["'`])((?:\/admin\/|\/ops(?:[/?#]|(?=["'`]))|\/watch(?:[/?#]|(?=["'`])))[^"'`\s<>]*)/g,
    (match,quote,url)=>quote+canonicalUrl(url));
}
