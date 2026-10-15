import published from '../my-workflows/published-worker.mjs';
import { applyShell } from './shell.mjs';
import { renderPage, renderMarkdown, workspacePage } from './pages.mjs';
import { routeAt, canonicalUrl, rewriteNavigation } from './routes.mjs';
import { assets, documents } from './assets.generated.mjs';
import { PRIVATE_HEADERS, json, migratedApi, pendingApi, connectionState, escapeHtml, documentHtml } from './migration.mjs';
import { THEME } from './theme.mjs';

async function authorized(request,env,ctx) {
  const response=await published.fetch(new Request(new URL('/api/admin/ping',request.url),{headers:request.headers}),env,ctx);
  const body=await response.json().catch(()=>null);
  return response.status===200 && body?.ok===true ? 200 : response.status===401 ? 401 : 503;
}
function pageResponse(html,request,status=200) {
  return new Response(request.method==='HEAD'?null:applyShell(html,new URL(request.url)),{status,headers:{...PRIVATE_HEADERS,'content-type':'text/html; charset=utf-8'}});
}
const PROFILE={id:'ai-hub',name:'AI相談',area:'彦根・滋賀',audience:'AIを仕事に活用したい地域の事業者・個人',defaultCta:'AI相談の講習・個別相談を見る',sourceUrls:['https://aiclimb.aiclimb.workers.dev/']};

export default {
  async fetch(request,env,ctx) {
    const url=new URL(request.url);
    const path=url.pathname.replace(/\/+$/,'')||'/';
    const login=['/admin/login','/admin/logout'].includes(path);
    const protectedApi=['/api/ops/doc','/api/admin/status','/api/admin/migration','/api/content-studio/api/profiles'].includes(path)||pendingApi(path);
    const privatePage=path==='/admin'||path.startsWith('/admin/')||path==='/ops'||path.startsWith('/ops/')||path==='/watch'||path.startsWith('/watch/');
    if((privatePage&&!login)||protectedApi){
      const auth=await authorized(request,env,ctx);
      if(auth===503) return json({error:'管理画面の認証設定を確認できません。時間をおいて開き直してください。'},503);
      if(auth!==200) return protectedApi?json({error:'管理画面へログインしてください。'},401):new Response(null,{status:303,headers:{...PRIVATE_HEADERS,location:'/admin/login?next='+encodeURIComponent(canonicalUrl(path+url.search,url.origin))}});
      if(protectedApi){
        if(path==='/api/content-studio/api/profiles') return request.method==='GET'?json({ok:true,profiles:[PROFILE]}):new Response(null,{status:405,headers:{...PRIVATE_HEADERS,allow:'GET'}});
        const migrated=migratedApi(request,env);if(migrated)return migrated;
        return json({error:pendingApi(path),migration:'connection-required'},503);
      }
      if(!['GET','HEAD'].includes(request.method)) return new Response(null,{status:405,headers:{...PRIVATE_HEADERS,allow:'GET, HEAD'}});
      const canonical=canonicalUrl(path+url.search,url.origin);
      if(canonical!==path+url.search) return new Response(null,{status:302,headers:{...PRIVATE_HEADERS,location:canonical}});
      const route=routeAt(path);
      const markdown=renderMarkdown(path);
      if(markdown!==null) return new Response(request.method==='HEAD'?null:markdown,{headers:{...PRIVATE_HEADERS,'content-type':'text/markdown; charset=utf-8','content-disposition':'attachment; filename="'+path.split('/').at(-1)+'"'}});
      if(path==='/admin/document') {
        const doc=documents.find(d=>d.slug===url.searchParams.get('file'));
        if(doc) return pageResponse(workspacePage(path,escapeHtml(doc.title),'運用記録 / '+doc.date,'<article class="workspace-document">'+documentHtml(doc.body)+'</article>'),request);
      }
      if(route?.kind==='migration') return pageResponse(workspacePage(path,route.title,'稼働中の機能と、接続が必要な機能を確認できます。','<ul class="workspace-list">'+connectionState(env).map(item=>'<li style="padding:20px"><strong>'+escapeHtml(item.name)+'</strong><p>'+escapeHtml(item.state)+'</p><small>'+escapeHtml(item.detail)+'</small></li>').join('')+'</ul>'),request);
      const own=renderPage(path);
      if(own!==null) return pageResponse(own,request);
      const asset=assets[path];
      if(asset) return asset.type.startsWith('text/html')?pageResponse(asset.body,request):new Response(request.method==='HEAD'?null:asset.body,{headers:{...PRIVATE_HEADERS,'content-type':asset.type}});
      if(route?.kind==='watch') {
        const item=url.searchParams.get('path')||'index.html';
        if(!/^[a-zA-Z0-9_/-]+(?:\.html)?$/.test(item)||item.includes('..')) return json({error:'記事が見つかりません。'},404);
        const upstream=new URL('/watch/'+item.replace(/index\.html$/,'').replace(/\.html$/,''),url);
        const result=await published.fetch(new Request(upstream,{headers:request.headers}),env,ctx);
        if(result.status===200&&result.headers.get('content-type')?.includes('text/html')) {
          const base=new URL('.',new URL('/watch/'+item,url)).pathname;
          const html=(await result.text()).replace(/<head\b[^>]*>/i,match=>match+'<base href="'+base+'">');
          return pageResponse(html,request);
        }
        if(result.status>=300&&result.status<400){
          const location=canonicalUrl(result.headers.get('location')||'',url.origin);
          if(location!==url.pathname+url.search) return new Response(null,{status:302,headers:{...PRIVATE_HEADERS,location}});
        }
        return pageResponse(workspacePage(path,'記事が見つかりません','収集記事の一覧から選び直してください。','<a href="/admin/watch">収集記事の一覧</a>'),request,404);
      }
      if(route?.kind==='studio') {
        const upstream=new URL(route.legacy+url.search,url);
        const response=await published.fetch(new Request(upstream,{headers:request.headers}),env,ctx);
        if(response.status===200) return pageResponse(rewriteNavigation((await response.text()).replace(/<head\b[^>]*>/i,match=>match+'<base href="/admin/apps/">'),{studio:true}),request);
        return response;
      }
    }
    const response=await published.fetch(request,env,ctx);
    if(login&&request.method==='GET'&&response.headers.get('content-type')?.includes('text/html')) {
      const html=(await response.text()).replace(/<body\b/,'<body data-workspace-shell').replace('</head>',THEME+'</head>');
      return new Response(html,{status:response.status,headers:response.headers});
    }
    if(privatePage&&!login) {
      if(response.status===200&&response.headers.get('content-type')?.includes('text/html')) return pageResponse(await response.text(),request);
      if(response.status===503||response.status===404) return pageResponse(workspacePage(path,'ページが見つかりません','上部のボタンから目的の機能を選んでください。','<a href="/admin/blog-create">制作・発信へ</a>'),request,404);
      if(response.status===200&&path.endsWith('content-studio.config.json')) {
        if(request.method==='HEAD') return response;
        const config=await response.json();config.adminUrl='/admin/blog-editor';return json(config);
      }
      if(response.status===200&&/javascript/.test(response.headers.get('content-type')||'')) return new Response(request.method==='HEAD'?null:rewriteNavigation(await response.text(),{studio:path.startsWith('/admin/apps/')}),{headers:{...PRIVATE_HEADERS,'content-type':'text/javascript; charset=utf-8'}});
    }
    return response;
  }
};
