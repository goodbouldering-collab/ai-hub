import test from 'node:test';
import assert from 'node:assert/strict';
import source from './worker.mjs';
import bundle from './published-worker.mjs';
import { ROUTES, canonicalUrl, rewriteNavigation, operationSectionAt } from './routes.mjs';
const origin='https://fixture.example';
const env={ADMIN_PASS:'local-fixture',ADMIN_SESSION_SECRET:'local-fixture-only-32-characters-secret',ADMIN_LOGIN_LIMITER:{limit:async()=>({success:true})},ASSETS:{fetch:async()=>new Response('<html><head><title>Watch</title></head><body><main>fixture</main></body></html>',{headers:{'content-type':'text/html'}})}};
const ctx={waitUntil(){}};
for(const [name,worker] of [['source',source],['bundle',bundle]]){
  test(name+': every registered page is a protected direct child, aliases keep queries, and HEAD is empty',async()=>{
    const login=await worker.fetch(new Request(origin+'/admin/login',{method:'POST',headers:{origin,'content-type':'application/x-www-form-urlencoded'},body:'password=local-fixture'}),env,ctx);
    const cookie=login.headers.get('set-cookie').split(';')[0];
    for(const route of ROUTES){
      assert.match(route.path,/^\/admin\/[^/]+$/);
      const denied=await worker.fetch(new Request(origin+route.path),env,ctx);assert.equal(denied.status,303,route.path);
      const r=await worker.fetch(new Request(origin+route.path,{headers:{cookie}}),env,ctx);assert.equal(r.status,200,route.path);
      assert.match(r.headers.get('cache-control'),/private, no-store/);
      const html=await r.text();
      if(route.group==='operations') assert.match(html,/aria-label="運営・分析メニュー"/,route.path);
      if(route.kind==='command'){
        const section=operationSectionAt(route.path);
        const nav=html.match(/<nav class="cc-local-nav"[\s\S]*?<\/nav>/)[0];
        for(const item of ROUTES.filter(item=>item.group==='operations'&&!item.archive)) assert.equal(nav.includes('href="'+item.path+'"'),section.routes.includes(item),route.path+' '+item.path);
        assert.doesNotMatch(html,/<details class="cc-market-nav"/);
        assert.match(html,/id="cc-content"/);
      }
      assert.match(html,/<title>AI相談<\/title>/,route.path);
      assert.match(html,/data-admin-theme/,route.path);
      assert.equal((html.match(/id="workspace-header"/g)||[]).length,1,route.path);
      if(route.kind==='studio') assert.ok(html.indexOf('<base href="/admin/apps/">')<html.indexOf('<link'), 'base must precede relative stylesheet loads');
      for(const [,href] of html.matchAll(/<a\b[^>]*href="(\/admin\/[^"?#]+)/g)) assert.doesNotMatch(href,/^\/admin\/(blog|command-center|materials|apps)\//,route.path+' '+href);
      const head=await worker.fetch(new Request(origin+route.path,{method:'HEAD',headers:{cookie}}),env,ctx);assert.equal(head.status,200,route.path);assert.equal(await head.text(),'');
      if(route.legacy!==route.path){
        const old=await worker.fetch(new Request(origin+route.legacy+'?symbol=6857',{headers:{cookie}}),env,ctx);
        assert.equal(old.status,302,route.legacy);assert.match(old.headers.get('location'),/symbol=6857/);
      }
    }
    const docList=await worker.fetch(new Request(origin+'/api/ops/doc',{headers:{cookie}}),env,ctx);
    const docs=(await docList.json()).docs;assert.ok(docs.length>100);assert.ok(docs.every(d=>!Object.hasOwn(d,'body')));
    const doc=await worker.fetch(new Request(origin+'/api/ops/doc?file='+docs[0].slug,{headers:{cookie}}),env,ctx);assert.equal(doc.status,200);assert.ok((await doc.json()).html);
    assert.equal((await worker.fetch(new Request(origin+'/api/ops/doc?file=../../AGENTS',{headers:{cookie}}),env,ctx)).status,404);
    assert.equal((await worker.fetch(new Request(origin+'/admin/watch?path=../../AGENTS',{headers:{cookie}}),env,ctx)).status,404);
    for(const api of ['/api/ops/doc','/api/admin/status','/api/admin/migration','/api/content-studio/api/profiles','/api/ops/prompts']){
      const denied=await worker.fetch(new Request(origin+api),env,ctx);assert.equal(denied.status,401,api);
      const missing=await worker.fetch(new Request(origin+api,{headers:{cookie}}),{...env,ADMIN_PASS:undefined},ctx);assert.equal(missing.status,503,api);
    }
    const profile=await worker.fetch(new Request(origin+'/api/content-studio/api/profiles',{headers:{cookie}}),env,ctx);
    assert.deepEqual((await profile.json()).profiles.map(p=>p.id),['ai-hub']);
    const config=await worker.fetch(new Request(origin+'/admin/apps/content-studio.config.json',{headers:{cookie}}),env,ctx);assert.equal((await config.json()).adminUrl,'/admin/blog-editor');
    const studio=await worker.fetch(new Request(origin+'/admin/apps/studio-core.js',{headers:{cookie}}),env,ctx);const js=await studio.text();assert.doesNotMatch(js,/localAdmin \? "\.\/(blog|reel)\.html"/);
    const pending=await worker.fetch(new Request(origin+'/api/ops/prompts',{method:'POST',headers:{cookie}}),env,ctx);assert.equal(pending.status,503);assert.match((await pending.json()).error,/接続待ち/);
  });
}
test('only internal view URLs are rewritten; API, external destination and editor query survive',()=>{
  assert.equal(canonicalUrl('/admin/command-center/security?symbol=6857#prices'),'/admin/security?symbol=6857#prices');
  assert.equal(canonicalUrl('https://outside.example/admin/blog/editor'),'https://outside.example/admin/blog/editor');
  const script='fetch("/api/admin/command-center/security");location.href="/admin/command-center/security?symbol="+symbol;';
  assert.match(rewriteNavigation(script),/fetch\("\/api\/admin\/command-center\/security"\)/);
  assert.match(rewriteNavigation(script),/location.href="\/admin\/security\?symbol="/);
  assert.equal(rewriteNavigation('blog.href = localAdmin ? "./blog.html" : "/blog";', {studio:true}),'blog.href = localAdmin ? "/admin/blog-create" : "/blog";');
  assert.equal(rewriteNavigation('import "./studio-core.js";', {studio:true}),'import "./studio-core.js";');
});
