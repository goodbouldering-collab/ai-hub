import { ROUTES, routeAt, rewriteNavigation } from './routes.mjs';
import { THEME } from './theme.mjs';
export const MENU = Object.freeze([
  { href: '/admin', label: 'ホーム', key: 'home' },
  { href: '/admin/blog-create', label: '制作・発信', key: 'create' },
  { href: '/admin/materials', label: '内部資料', key: 'materials' },
  { href: '/admin/operations', label: '運営・分析', key: 'operations' },
]);

function activeKey(path) {
  const route=routeAt(path); if(route) return route.group;
  if(path==='/admin/document') return 'materials';
  if (path.startsWith('/admin/materials') || path.startsWith('/ops')) return 'materials';
  if (/^\/admin\/(create|blog|apps|sns-post)/.test(path)) return 'create';
  if (/^\/admin\/(operations|command-center|gubble-sns|chat)/.test(path)) return 'operations';
  return 'home';
}

export function header(path) {
  const active = activeKey(path);
  return `<header id="workspace-header"><div class="workspace-bar"><a class="workspace-brand" href="/admin">AI相談<small>管理</small></a><nav aria-label="管理メニュー">${MENU.map(item => `<a href="${item.href}"${active === item.key ? ' aria-current="page"' : ''}>${item.label}</a>`).join('')}</nav><div class="workspace-tools"><a href="/" target="_blank" rel="noopener">公開サイト ↗</a><a href="/admin/logout">ログアウト</a></div></div></header>`;
}

// Generated from the same registry as the home catalogue; no parallel menu definitions.
export function creationNavigation(path) {
  return `<nav class="workspace-actions" aria-label="制作・発信メニュー">${ROUTES.filter(r=>r.group==='create').map(r=>`<a class="workspace-action${r.path===path?' workspace-action--primary':''}" href="${r.path}"${r.path===path?' aria-current="page"':''}>${r.title}</a>`).join('')}</nav>`;
}

export const SHELL_STYLE = `<style data-workspace-shell-style>
html{scroll-padding-top:130px}body[data-workspace-shell]{padding-top:0!important}body[data-workspace-shell]>main,body[data-workspace-shell]>.container{padding-top:24px!important}body[data-workspace-shell]>.admin-page-context{display:none!important}
#workspace-header{position:sticky!important;top:0!important;z-index:1000;display:block;width:100%;max-width:none;margin:0!important;padding:0!important;border:0;border-bottom:1px solid #dce3e8;background:#fff;color:#193542;box-shadow:0 3px 15px #122b3708;font:14px/1.5 system-ui,"Yu Gothic",sans-serif;transform:none;backdrop-filter:none;height:auto!important}
#workspace-header *{box-sizing:border-box}#workspace-header .workspace-bar{display:flex;align-items:center;gap:30px;max-width:1280px;margin:auto;padding:12px 28px}#workspace-header a{color:#304d5d;text-decoration:none;box-shadow:none}#workspace-header .workspace-brand{display:flex;align-items:baseline;gap:12px;font-size:23px;font-weight:800;white-space:nowrap}#workspace-header .workspace-brand small{font-size:11px;color:#71808c;font-weight:500}
#workspace-header nav{position:static;display:flex;align-items:center;justify-content:center;gap:6px;flex:1;width:auto;height:auto;max-width:none;margin:0;padding:0;overflow:visible;border:0;background:none;box-shadow:none;transform:none;visibility:visible;opacity:1}#workspace-header nav a{display:block;min-height:44px;margin:0;padding:11px 16px;border-radius:8px;border:0;background:none;font-size:14px;font-weight:650;white-space:nowrap}#workspace-header nav a:hover{background:#f0f4f6}#workspace-header nav a[aria-current]{background:#eaf1f4;color:#123e50;box-shadow:inset 0 -2px #2e657c}
#workspace-header .workspace-tools{display:flex;gap:15px;align-items:center;font-size:12px;white-space:nowrap}#workspace-header a:focus-visible{outline:3px solid #387d99;outline-offset:3px}
body[data-workspace-shell] .topbar{position:static!important;top:auto!important}body[data-workspace-shell] .studio-tabs{position:static}body[data-workspace-shell] .steps{top:115px}
@media(max-width:900px){#workspace-header .workspace-bar{display:grid;grid-template-columns:1fr auto;gap:8px 12px;padding:10px 16px}#workspace-header nav{grid-column:1/-1;grid-row:2;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px;width:100%}#workspace-header nav a{text-align:center;padding:10px 3px;font-size:13px;white-space:normal}#workspace-header .workspace-brand{font-size:20px}#workspace-header .workspace-tools{gap:12px;font-size:11px}}
#workspace-header nav a{border:1px solid #b6cbd7;background:#fff}#workspace-header .workspace-tools a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:8px 12px;border:1px solid #b6cbd7;border-radius:8px;background:#fff}#workspace-header .workspace-tools{gap:8px}
</style>`;

export function applyShell(html, url) {
  html=rewriteNavigation(html);
  html=html.replace('REEL APP SERVER','AI相談').replace('事業別リール制作','AI相談 リール制作').replace('⚙️ OPS — AIスペシャリスト管理本部','運用記録・プロンプト');
  if (html.includes('id="workspace-header"')) return html.includes('data-admin-theme')?html:html.replace('</head>',THEME+'</head>');
  // Keep production editor headings/status IDs. Only replace the shared navigation.
  html = html.replace(/<script\b[^>]*src=["'][^"']*admin-menu\.js[^"']*["'][^>]*>[\s\S]*?<\/script>/gi, '');
  html = html.replace(/<title>[\s\S]*?<\/title>/i,'<title>AI相談</title>').replace(/document\.title\s*=\s*["'][^"']*["']/g,'document.title="AI相談"');
  // Legacy CSS comments contain literal <header> examples. Keep raw-text blocks
  // opaque so replacing a real header cannot consume the head or editor body.
  const raw=[];
  html=html.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>|<style\b[^>]*>[\s\S]*?<\/style\s*>|<!--[\s\S]*?-->/gi,block=>{raw.push(block);return '\uE000WORKSPACE'+(raw.length-1)+'\uE001';});
  const route=routeAt(url.pathname);
  if(route?.group==='create') {
    html=html.replace(/<nav\b[^>]*class=["'][^"']*\b(?:studio-tabs|blog-page-nav)\b[^"']*["'][^>]*>[\s\S]*?<\/nav>/gi,'');
  }
  const oldHeader = /<header\b(?=[^>]*(?:class=["'][^"']*\bsite-header\b|id=["']site-header["']))[^>]*>[\s\S]*?<\/header>/i;
  if (oldHeader.test(html)) html = html.replace(oldHeader, header(url.pathname));
  else html = html.replace(/(<body\b[^>]*>)/i, `$1${header(url.pathname)}`);
  html = html.replace(/<body\b/i, '<body data-workspace-shell');
  html = html.replace('id="studio-nav-back" href="/studio"', 'id="studio-nav-back" href="/admin/create"');
  if(route?.group==='create') html=html.replace('</header>','</header>'+creationNavigation(url.pathname));
  if(route) html=html.replace('</header>', '</header><div class="workspace-return"><a href="/admin">← 管理ホーム</a><span>'+route.title+'</span></div>');
  if(url.pathname==='/admin/gubble-sns') html=html.replace('</header>','</header><details class="workspace-details" style="max-width:1120px;margin:16px auto;padding:0 16px"><summary>以前の媒体ボードに保存した設定・履歴</summary><p>旧ボードの保存内容を確認できます。通常の分析はこの画面を使います。</p><p><a href="/admin/sns-cross-media-dashboard">旧媒体ボードを開く</a></p></details>');
  if(url.pathname==='/admin/sns-cross-media-dashboard') html=html.replace('</header>','</header><p class="workspace-return">旧媒体ボード：保存済み設定・履歴の参照用。<a href="/admin/gubble-sns">SNS分析へ</a></p>');
  return html.replace('</head>', SHELL_STYLE + THEME + '</head>').replace(/\uE000WORKSPACE(\d+)\uE001/g,(_,index)=>raw[Number(index)]);
}
