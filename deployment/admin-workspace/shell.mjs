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

export function allButtons(path) {
 return '<nav class="workspace-button-grid" aria-label="管理機能">'+ROUTES.map(r=>'<a href="'+r.path+'"'+(r.path===path?' aria-current="page"':'')+'>'+r.title+'</a>').join('')+'</nav>';
}
export function header(path) {
 return '<header id="workspace-header"><div class="workspace-button-tools">'+(path==='/admin'?'':'<a href="/admin">全管理機能</a>')+'<a href="/" target="_blank" rel="noopener">公開サイト</a><a href="/admin/logout">ログアウト</a></div>'+(path==='/admin'?'':allButtons(path))+'</header>';
}

export const SHELL_STYLE = `<style data-workspace-shell-style>
html{scroll-padding-top:130px}body[data-workspace-shell]{padding-top:0!important}body[data-workspace-shell]>main,body[data-workspace-shell]>.container{padding-top:24px!important}body[data-workspace-shell]>.admin-page-context{display:none!important}
#workspace-header{position:sticky!important;top:0!important;z-index:1000;display:block;width:100%;max-width:none;margin:0!important;padding:0!important;border:0;border-bottom:1px solid #dce3e8;background:#fff;color:#193542;box-shadow:0 3px 15px #122b3708;font:14px/1.5 system-ui,"Yu Gothic",sans-serif;transform:none;backdrop-filter:none;height:auto!important}
#workspace-header *{box-sizing:border-box}#workspace-header .workspace-bar{display:flex;align-items:center;gap:30px;max-width:1280px;margin:auto;padding:12px 28px}#workspace-header a{color:#304d5d;text-decoration:none;box-shadow:none}#workspace-header .workspace-brand{display:flex;align-items:baseline;gap:12px;font-size:23px;font-weight:800;white-space:nowrap}#workspace-header .workspace-brand small{font-size:11px;color:#71808c;font-weight:500}
#workspace-header nav{position:static;display:flex;align-items:center;justify-content:center;gap:6px;flex:1;width:auto;height:auto;max-width:none;margin:0;padding:0;overflow:visible;border:0;background:none;box-shadow:none;transform:none;visibility:visible;opacity:1}#workspace-header nav a{display:block;min-height:44px;margin:0;padding:11px 16px;border-radius:8px;border:0;background:none;font-size:14px;font-weight:650;white-space:nowrap}#workspace-header nav a:hover{background:#f0f4f6}#workspace-header nav a[aria-current]{background:#eaf1f4;color:#123e50;box-shadow:inset 0 -2px #2e657c}
#workspace-header .workspace-tools{display:flex;gap:15px;align-items:center;font-size:12px;white-space:nowrap}#workspace-header a:focus-visible{outline:3px solid #387d99;outline-offset:3px}
body[data-workspace-shell] .topbar{position:static!important;top:auto!important}body[data-workspace-shell] .studio-tabs{position:static}body[data-workspace-shell] .steps{top:115px}
@media(max-width:900px){#workspace-header .workspace-bar{display:grid;grid-template-columns:1fr auto;gap:8px 12px;padding:10px 16px}#workspace-header nav{grid-column:1/-1;grid-row:2;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px;width:100%}#workspace-header nav a{text-align:center;padding:10px 3px;font-size:13px;white-space:normal}#workspace-header .workspace-brand{font-size:20px}#workspace-header .workspace-tools{gap:12px;font-size:11px}}
#workspace-header{position:static!important;padding:16px!important}
#workspace-header .workspace-button-tools{display:flex;flex-wrap:wrap;gap:8px;max-width:1120px;margin:0 auto 12px}
.workspace-button-grid,#workspace-header nav.workspace-button-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;max-width:1120px;margin:0 auto;width:100%;padding:0}
.workspace-button-grid a,#workspace-header nav.workspace-button-grid a,#workspace-header .workspace-button-tools a{display:flex;align-items:center;justify-content:center;min-height:48px;padding:12px 14px;border:1px solid #b8cad0;border-radius:9px;background:#fff;color:#193e4e;text-align:center;text-decoration:none;font:600 14px/1.5 system-ui,"Yu Gothic",sans-serif;white-space:normal}
.workspace-button-grid a:hover,#workspace-header nav.workspace-button-grid a:hover{background:#eaf3f4;border-color:#326b78}
.workspace-button-grid a[aria-current],#workspace-header nav.workspace-button-grid a[aria-current]{background:#193e4e;color:#fff}
.workspace-button-grid a:focus-visible{outline:3px solid #387d99;outline-offset:3px}
@media(max-width:600px){.workspace-button-grid,#workspace-header nav.workspace-button-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}#workspace-header{padding:12px!important}.workspace-button-grid a,#workspace-header nav.workspace-button-grid a{font-size:13px;padding:10px 8px}}
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
  return html.replace('</head>', SHELL_STYLE + THEME + '</head>').replace(/\uE000WORKSPACE(\d+)\uE001/g,(_,index)=>raw[Number(index)]);
}
