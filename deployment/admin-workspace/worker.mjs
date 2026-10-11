import published from '../my-workflows/published-worker.mjs';
import { applyShell } from './shell.mjs';
import { renderPage, renderMarkdown } from './pages.mjs';

async function authorized(request,env,ctx) {
  const response=await published.fetch(new Request(new URL('/api/admin/ping',request.url),{headers:request.headers}),env,ctx);
  const body=await response.json().catch(()=>null);
  return response.status===200 && body?.ok===true ? 200 : response.status===401 ? 401 : 503;
}
const PRIVATE_HEADERS={'cache-control':'private, no-store','x-content-type-options':'nosniff','x-robots-tag':'noindex, nofollow'};

export default {
  async fetch(request,env,ctx) {
    const url=new URL(request.url);
    let path=url.pathname.replace(/\/+$/,'') || '/';
    if(['/admin/index.html','/admin/hub.html'].includes(path)) path='/admin';
    const ownPath=['/admin','/admin/create','/admin/operations','/admin/materials'].includes(path) || path.startsWith('/admin/materials/');
    if(ownPath) {
      const authStatus=await authorized(request,env,ctx);
      if(authStatus===503) return new Response(request.method==='HEAD'?null:'管理画面を一時的に利用できません。時間をおいて再度開いてください。',{status:503,headers:{...PRIVATE_HEADERS,'content-type':'text/plain; charset=utf-8','retry-after':'60'}});
      if(authStatus!==200) return new Response(null,{status:303,headers:{...PRIVATE_HEADERS,location:'/admin/login?next='+encodeURIComponent(url.pathname)}});
      if(!['GET','HEAD'].includes(request.method)) return new Response(null,{status:405,headers:{...PRIVATE_HEADERS,allow:'GET, HEAD'}});
      const markdown=renderMarkdown(path);
      const html=markdown===null ? renderPage(path) : null;
      if(markdown===null && html===null) return new Response(request.method==='HEAD'?null:'資料が見つかりません。',{status:404,headers:PRIVATE_HEADERS});
      return new Response(request.method==='HEAD'?null:(markdown??html),{headers:{...PRIVATE_HEADERS,'content-type':markdown===null?'text/html; charset=utf-8':'text/markdown; charset=utf-8',...(markdown===null?{}:{'content-disposition':'attachment; filename="'+path.split('/').at(-1)+'"'})}});
    }
    const response=await published.fetch(request,env,ctx);
    const adminHtml=(path.startsWith('/admin/') && !/^\/admin\/(?:login|logout)(?:\/|$)/.test(path)) || path==='/ops' || path.startsWith('/ops/');
    if(!adminHtml || request.method!=='GET' || response.status!==200 || !response.headers.get('content-type')?.includes('text/html')) return response;
    // Existing application already enforces its authentication and all APIs remain unchanged.
    // Check again before decorating any admin HTML, including legacy entry aliases.
    if(await authorized(request,env,ctx)!==200) return response;
    const html=applyShell(await response.text(),url);
    const headers=new Headers(response.headers);
    for(const name of ['content-length','content-encoding','etag']) headers.delete(name);
    for(const [name,value] of Object.entries(PRIVATE_HEADERS)) headers.set(name,value);
    return new Response(html,{status:response.status,headers});
  }
};
