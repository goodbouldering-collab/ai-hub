import { OPERATION_SECTIONS, operationSectionAt } from './routes.mjs';
import { header, SHELL_STYLE, operationsNavigation } from './shell.mjs';

export const DOCUMENTS = Object.freeze([
  {slug:'daily-operation',category:'運営',title:'毎日の運営チェック',description:'予定の確認から公開後の確認まで。',sections:[
    ['最初に見る','実行指令室で予定と指示を確認し、今日進める仕事を一つ決めます。公開サイトの講習案内・ブログ・申込リンクに更新が必要か確認します。'],
    ['制作する','「制作・発信」からブログまたはリールを開きます。元資料、写真、伝えたい事実をそろえ、対象者と次の行動を決めてから作ります。'],
    ['公開を確認する','下書きの完成と公開完了は別です。公開先・最終内容を確認してから反映し、実際のURL、画像、リンクをPCとスマートフォンで確かめます。'],
    ['次に残す','使った素材、完成原稿、公開URL、残っている作業を記録します。問い合わせや予約の個人情報は発信用の原稿や画像に混ぜません。'],
  ]},
  {slug:'publishing',category:'制作',title:'ブログ・リール制作の進め方',description:'素材をそろえ、下書き・確認・公開へ。',sections:[
    ['伝えることを一つにする','誰の、どんな困りごとを解決するかを決めます。タイトル、見出し、画像は同じ主題にそろえます。読み終えた人にしてほしい行動を一つ選びます。'],
    ['ブログを作る','ブログ制作で元資料とテーマを入力し、提案から記事を整えます。固有名詞、日付、数字、出典、申込先を原本と照合します。既存記事の編集・公開確認はブログ管理から行います。'],
    ['リールを作る','縦動画の各場面にメッセージを一つ置きます。小さな画面で文字を読めるか、音声と表示時間が合うか、カバーと投稿文が一致するかを確認します。'],
    ['公開前の確認','最終原稿と投稿先の事業・アカウントを確認します。SNSへの投稿は、下書きを作っただけで実施済みとしません。送信結果が不明なときは履歴を確認し、重複投稿を防ぎます。'],
  ]},
  {slug:'artwork',category:'素材',title:'画像・資料の使い分け',description:'生成画像、実績画面、講師写真を使い分ける。',sections:[
    ['サイトの案内画像','2026年10月11日の案内画像は、落ち着いた写実表現の生成画像です。人物や場面は架空のイメージです。実際の講師・顧客・支援実績の写真として扱いません。'],
    ['事実を伝える画像','講師紹介には本人写真、制作実績には実際のサイト画面、記事の根拠には確認できる資料を使います。雰囲気をそろえるために証拠画像を生成画像へ置き換えません。'],
    ['資料を渡す','受講者向けには公開の受講資料を案内し、運営用の手順・メモは内部資料で扱います。配布前に公開範囲と個人情報の有無を確認します。'],
    ['素材を残す','元素材と配信用画像を分け、採用した画像と生成プロンプト、利用場所が分かるよう記録します。画像だけを見て、何の話か一言で説明できるものを選びます。'],
  ]},
]);

const CSS=`<style>
:root{font-family:system-ui,"Yu Gothic",sans-serif;color:#193342;background:#f5f7f9;font-synthesis:none}*{box-sizing:border-box}body{margin:0}a{color:inherit}a:focus-visible,summary:focus-visible,input:focus-visible{outline:3px solid #3b819b;outline-offset:4px}.admin-workspace{max-width:1120px;margin:auto;padding:38px 28px 72px!important}.workspace-intro{display:flex;justify-content:space-between;align-items:end;gap:24px;margin:12px 0 30px}.workspace-intro p{margin:9px 0 0;color:#667a87;font-size:14px;line-height:1.7}.workspace-intro h1{margin:0;font-size:clamp(25px,3vw,34px);font-weight:750;letter-spacing:-.04em;line-height:1.45}.workspace-eyebrow{font-size:10px;font-weight:700;letter-spacing:.12em;color:#6e8794;display:block;margin-bottom:10px}.workspace-section{margin-top:32px}.workspace-section h2{font-size:16px;margin:0 0 14px}.workspace-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.workspace-card{display:flex;flex-direction:column;position:relative;min-height:175px;padding:24px;border:1px solid #dae2e8;border-radius:14px;background:#fff;text-decoration:none;transition:border-color .15s,box-shadow .15s}.workspace-card:hover{border-color:#698c9d;box-shadow:0 7px 22px #1a3a4c09}.workspace-card--primary{background:#193e4e;border-color:#193e4e;color:#fff}.workspace-card .card-icon{font-size:21px;line-height:1;margin-bottom:20px}.workspace-card h2,.workspace-card h3{font-size:19px;line-height:1.5;margin:0 0 8px;letter-spacing:-.025em}.workspace-card p{font-size:13px;line-height:1.7;color:#6b7f8b;margin:0 0 18px}.workspace-card--primary p{color:#cedee6}.workspace-card .card-arrow{margin-top:auto;font-size:13px;font-weight:650}.workspace-list{margin:0;padding:0;list-style:none;display:grid;gap:0;border:1px solid #dce4e9;border-radius:12px;background:#fff;overflow:hidden}.workspace-list li+li{border-top:1px solid #e7edf0}.workspace-list a{display:flex;gap:18px;align-items:center;justify-content:space-between;padding:18px 21px;text-decoration:none}.workspace-list a:hover{background:#f5f9fb}.workspace-list strong{font-size:14px}.workspace-list small{display:block;color:#728592;font-size:12px;margin-top:5px}.workspace-details{margin-top:24px;border:1px solid #dce4e9;border-radius:12px;background:#fff}.workspace-details summary{cursor:pointer;padding:18px 21px;font-size:14px;font-weight:650}.workspace-details .workspace-list{border:0;border-radius:0 0 12px 12px}.workspace-details p{padding:0 21px;color:#728592;font-size:12px;line-height:1.7}.workspace-note{font-size:12px;color:#728592;margin:20px 0;line-height:1.7}.workspace-subnav{display:flex;gap:18px;flex-wrap:wrap;margin:26px 0;color:#647d8d;font-size:13px}.workspace-search{display:block;width:100%;max-width:470px;padding:13px 16px;border:1px solid #cbd8e0;border-radius:10px;font:inherit;font-size:14px;background:#fff;margin-bottom:22px}.workspace-tag{font-size:10px;letter-spacing:.07em;color:#6f8794;margin-bottom:14px}.workspace-document{max-width:800px;background:#fff;border:1px solid #dce4e9;border-radius:16px;padding:30px}.workspace-document h2{font-size:18px;margin:28px 0 10px}.workspace-document h2:first-child{margin-top:0}.workspace-document p{font-size:14px;line-height:1.95;color:#455e6e}.workspace-empty{padding:20px;background:#fff;border:1px dashed #bcced8;border-radius:10px;color:#627c8c}a.workspace-download{display:inline-block;padding:12px 16px;border:1px solid #c7d5de;border-radius:8px;text-decoration:none;font-size:13px;background:#fff} [hidden]{display:none!important}
@media(max-width:700px){.admin-workspace{padding:20px 18px 50px!important}.workspace-intro{display:block;margin:4px 0 24px}.workspace-grid{grid-template-columns:1fr;gap:12px}.workspace-card{min-height:0;padding:20px}.workspace-card .card-icon{margin-bottom:14px}.workspace-card p{margin-bottom:15px}.workspace-document{padding:22px}.workspace-subnav{gap:12px}.workspace-intro h1{font-size:26px}}
.admin-workspace .workspace-intro{margin:4px 0 20px}.admin-workspace .workspace-intro p,.admin-workspace .workspace-eyebrow{display:none}.admin-workspace .workspace-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;border:0;background:transparent;overflow:visible}.admin-workspace .workspace-list li+li{border:0}.admin-workspace .workspace-list a{height:100%;min-height:48px;justify-content:center;padding:12px 16px;border:1px solid #b6cbd7;border-radius:8px;background:#fff;text-align:center}.admin-workspace .workspace-list small,.admin-workspace .workspace-list a>span:last-child:not(:first-child){display:none}.admin-workspace .workspace-card{min-height:48px;padding:16px;justify-content:center;text-align:center;border-radius:8px}.admin-workspace .workspace-card h2{font-size:15px;margin:0}.admin-workspace .workspace-card :is(p,.workspace-tag,.card-arrow){display:none}.admin-workspace .workspace-grid{grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}.admin-workspace .workspace-details{padding:0 12px 12px}.admin-workspace .workspace-details summary{min-height:44px}.admin-workspace .workspace-search{min-height:44px}@media(max-width:600px){.admin-workspace .workspace-list,.admin-workspace .workspace-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.admin-workspace .workspace-list a{padding:10px 8px}.admin-workspace .workspace-list strong{font-size:13px}}
@media(prefers-reduced-motion:reduce){.workspace-card{transition:none}}
</style>`;
const e=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const list=items=>`<ul class="workspace-list">${items.map(([href,title,description])=>`<li><a href="${href}"><span><strong>${title}</strong><small>${description}</small></span><span aria-hidden="true">→</span></a></li>`).join('')}</ul>`;
const section=(title,body)=>`<section class="workspace-section"><h2>${title}</h2>${body}</section>`;
export const workspacePage=(path,title,lead,body)=>{
  // Move only the landing-page launchers above the introduction. Document cards
  // and their search metadata stay in the content area.
  const launcher=body.match(/^<div class="workspace-grid">([\s\S]*?)<\/div>/);
  const actions=launcher&&launcher[1].includes('class="workspace-action');
  const navigation=operationSectionAt(path)?operationsNavigation(path):actions?`<nav class="workspace-actions" aria-label="作業メニュー">${launcher[1]}</nav>`:'';
  const content=actions?body.slice(launcher[0].length):body;
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>AI相談</title>${CSS}${SHELL_STYLE}</head><body data-workspace-shell>${header(path)}${navigation}<main class="admin-workspace"><div class="workspace-intro"><div><span class="workspace-eyebrow">AI相談 / 管理</span><h1>${title}</h1><p>${lead}</p></div></div>${content}</main></body></html>`;
};

export function renderPage(path) {
  if(path==='/admin/operations') return workspacePage(path,'運営・分析','',list(OPERATION_SECTIONS.map(item=>[item.path,item.title,''])));
  const operationSection=OPERATION_SECTIONS.find(item=>item.path===path);
  if(operationSection) return workspacePage(path,operationSection.title,'',list(operationSection.routes.map(route=>[route.path,route.title,''])));
  if(path==='/admin/materials') return workspacePage(path,'内部資料','運営と制作に必要な手順を、一か所に。',`<label for="material-search" class="workspace-search-label">資料を探す</label><input class="workspace-search" id="material-search" type="search" placeholder="例：公開、画像、リール" autocomplete="off"><div class="workspace-grid" id="material-list">${DOCUMENTS.map(doc=>`<a class="workspace-card" data-material-search="${e([doc.title,doc.category,doc.description,...doc.sections.flat()].join(' '))}" href="/admin/materials/${doc.slug}"><span class="workspace-tag">${doc.category} / 手順書</span><h2>${doc.title}</h2><p>${doc.description}</p><span class="card-arrow">読む →</span></a>`).join('')}</div><p class="workspace-empty" id="material-empty" role="status" hidden>一致する資料がありません。別の言葉で検索してください。</p>`+section('関連する資料',list([['/admin/watch','収集記事','収集済みの記事を確認'],['/ops','運用記録・プロンプト','保存済みの資料、プロンプト、活動記録'],['/lectures/index.html','受講者向け資料','公開中の講習資料を確認'],['/design-system/','デザインの見本','色・部品・表示ルール']]))+`<script>document.getElementById('material-search').addEventListener('input',event=>{const query=event.target.value.trim().normalize('NFKC').toLocaleLowerCase('ja');let found=0;document.querySelectorAll('[data-material-search]').forEach(card=>{const match=card.dataset.materialSearch.normalize('NFKC').toLocaleLowerCase('ja').includes(query);card.hidden=!match;if(match)found++});document.getElementById('material-empty').hidden=found>0});</script>`);
  const doc=DOCUMENTS.find(doc=>path==='/admin/'+doc.slug);
  if(doc) return workspacePage(path,doc.title,doc.description,`<nav class="workspace-subnav" aria-label="資料内ナビ"><a href="/admin/materials">← 内部資料一覧</a><span>更新 2026-10-11</span></nav><article class="workspace-document">${doc.sections.map(([heading,body])=>`<h2>${e(heading)}</h2><p>${e(body)}</p>`).join('')}</article><p><a class="workspace-download" href="/admin/materials/${doc.slug}.md" download>この資料を保存 ↓</a></p>`);
  return null;
}

export function renderMarkdown(path) {
  const doc=DOCUMENTS.find(doc=>path==='/admin/'+doc.slug+'.md');
  return doc ? `# ${doc.title}\n\n更新: 2026-10-11\n\n${doc.description}\n\n${doc.sections.map(([h,b])=>`## ${h}\n\n${b}`).join('\n\n')}\n` : null;
}
