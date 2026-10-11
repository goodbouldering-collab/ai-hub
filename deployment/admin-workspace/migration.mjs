import { documents, statusSnapshot } from './assets.generated.mjs';
export const PRIVATE_HEADERS={'cache-control':'private, no-store','x-content-type-options':'nosniff','x-robots-tag':'noindex, nofollow'};
export const json=(body,status=200)=>Response.json(body,{status,headers:PRIVATE_HEADERS});
export const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function documentHtml(body){
  return body.split(/\n\n+/).map(block=>/^#{1,4} /.test(block)?block.split('\n').map(line=>{const m=line.match(/^(#{1,4}) (.*)$/);return m?`<h${m[1].length+1}>${escapeHtml(m[2])}</h${m[1].length+1}>`:`<p>${escapeHtml(line)}</p>`;}).join(''):`<p style="white-space:pre-wrap">${escapeHtml(block)}</p>`).join('');
}
export function connectionState(env){
  return [
    {name:'管理画面・資料閲覧',state:'Cloudflareで稼働',detail:'画面、メニュー、運用原文の閲覧を移行。'},
    {name:'ブログ・リール生成',state:env.OPENAI_API_KEY?'サーバーキー設定あり・生成未検証':'利用者の保存キー確認が必要',detail:'同じ管理画面の接続設定から確認できます。実生成の成功は別途確認します。'},
    {name:'画像の永続保存',state:env.ARTICLE_IMAGES&&env.ARTICLE_IMAGES_PUBLIC_URL?'ストレージ設定あり・保存未検証':'ストレージ接続待ち',detail:'既存R2 bindingと生成キーの確認が必要です。'},
    {name:'記事の外部公開',state:env.COLORME_ACCESS_TOKEN?'接続設定あり・公開未検証':'外部サービスの接続待ち',detail:'公開先の確認と接続情報の設定が必要です。'},
    {name:'予定・タスク・プロンプトの保存',state:'保存APIの移行・接続待ち',detail:'画面と資料閲覧は移行済み。共有データの保存・同期は未完了です。'},
    {name:'SNS投稿・AIチャット',state:'API接続待ち',detail:'画面を移行済み。実投稿、チャット生成、分析データの更新は未検証です。'},
  ];
}
export function migratedApi(request,env){
  const url=new URL(request.url),path=url.pathname;
  if(!['/api/ops/doc','/api/admin/status','/api/admin/migration'].includes(path)) return null;
  if(!['GET','HEAD'].includes(request.method)) return new Response(null,{status:405,headers:{...PRIVATE_HEADERS,allow:'GET, HEAD'}});
  let response;
  if(path==='/api/admin/migration') response=json({items:connectionState(env)});
  else if(path==='/api/admin/status') response=statusSnapshot?json({...statusSnapshot,snapshot:true}):json({error:'保存済みの運用記録がありません。'},503);
  else {
    const slug=url.searchParams.get('file');
    if(!slug) response=json({docs:documents.map(({body,...meta})=>meta)});
    else {
      const doc=documents.find(d=>d.slug===slug.replace(/\.md$/,''));
      response=doc?json({...doc,html:'<p><a href="/admin/document?file='+encodeURIComponent(doc.slug)+'">この資料を開く →</a></p>'+documentHtml(doc.body)}):json({error:'資料が見つかりません。'},404);
    }
  }
  return request.method==='HEAD'?new Response(null,response):response;
}
export function pendingApi(path){
  if(path==='/api/ops/prompts') return 'プロンプトの共有保存は接続待ちです。既存データは変更されていません。';
  if(/^\/api\/admin\/command-center\/(data|calendar|brief|relay|migrate)$/.test(path)) return '予定・タスクの保存先は移行・接続待ちです。「移行・接続状況」で残件を確認できます。';
  if(['/api/admin/chat','/api/admin/sns-draft','/api/admin/sns-post','/api/admin/sns-history','/api/admin/gubble-sns-metrics'].includes(path)) return 'この機能のAPI接続は未完了です。「移行・接続状況」で確認してください。';
  return null;
}
