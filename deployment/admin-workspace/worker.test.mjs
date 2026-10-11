import test from 'node:test';
import assert from 'node:assert/strict';
import source from './worker.mjs';
import bundle from './published-worker.mjs';
import { applyShell } from './shell.mjs';
import { DOCUMENTS } from './pages.mjs';

// Synthetic local credentials exercise the actual existing login implementation.
const env={ADMIN_PASS:'test-only-not-a-real-password',ADMIN_SESSION_SECRET:'test-only-session-secret',ADMIN_LOGIN_LIMITER:{limit:async()=>({success:true})},ASSETS:{fetch:async()=>new Response('public fixture',{headers:{'content-type':'text/html'}})}};
const ctx={waitUntil(){}};
const origin='https://unit.example';
for(const [name,worker] of [['source',source],['bundle',bundle]]){
  test(`${name}: real login gates all private HTML and downloads`,async()=>{
    const paths=['/admin','/admin/','/admin/hub.html','/admin/index.html','/admin/create','/admin/operations','/admin/materials',...DOCUMENTS.flatMap(d=>['/admin/materials/'+d.slug,'/admin/materials/'+d.slug+'.md'])];
    for(const path of paths){
      const denied=await worker.fetch(new Request(origin+path),env,ctx);
      assert.equal(denied.status,303,path);assert.match(denied.headers.get('location'),/^\/admin\/login/);
      assert.equal(await denied.text(),'');assert.match(denied.headers.get('cache-control'),/no-store/);
    }
    const login=await worker.fetch(new Request(origin+'/admin/login',{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded','origin':origin},body:new URLSearchParams({password:env.ADMIN_PASS,next:'/admin'})}),env,ctx);
    assert.equal(login.status,303);const cookie=login.headers.get('set-cookie').split(';')[0];
    for(const path of paths){
      const response=await worker.fetch(new Request(origin+path,{headers:{cookie}}),env,ctx);
      assert.equal(response.status,200,path);assert.match(response.headers.get('cache-control'),/private, no-store/);assert.match(response.headers.get('x-robots-tag'),/noindex/);
      const body=await response.text();
      if(path.endsWith('.md')){assert.match(body,/^# /);assert.match(response.headers.get('content-disposition'),/^attachment/);}
      else {assert.match(body,/<title>AI相談<\/title>/);assert.equal((body.match(/id="workspace-header"/g)||[]).length,1);}
      const head=await worker.fetch(new Request(origin+path,{method:'HEAD',headers:{cookie}}),env,ctx);assert.equal(head.status,200);assert.equal(await head.text(),'');
    }
    for(const [path,method,status] of [['/admin/materials/missing','GET',404],['/admin/materials','POST',405]]){
      const r=await worker.fetch(new Request(origin+path,{method,headers:{cookie}}),env,ctx);assert.equal(r.status,status);
    }
    const ping=await worker.fetch(new Request(origin+'/api/admin/ping',{headers:{cookie}}),env,ctx);assert.equal((await ping.json()).ok,true);
    assert.equal((await worker.fetch(new Request(origin+'/api/admin/ping'),env,ctx)).status,401);
    const anonymous=await worker.fetch(new Request(origin+'/admin/materials/artwork',{headers:{cookie:cookie+'broken'}}),env,ctx);assert.equal(anonymous.status,303);
    const publicPage=await worker.fetch(new Request(origin+'/ordinary-public-page'),env,ctx);assert.equal(await publicPage.text(),'public fixture');
  });
}
test('shell removes old menu, preserves editor IDs/scripts, and embeds only once',()=>{
  const html='<html><head><title>ブログ App Server</title></head><body><header class="topbar"><h1 id="studio-brand-heading">Blog</h1><span id="server-state">Ready</span></header><nav class="studio-tabs"><a id="studio-nav-back" href="/studio">Back</a></nav><textarea id="editor"></textarea><script src="/admin/admin-menu.js"></script><script>initializeEditor()</script></body></html>';
  const url=new URL(origin+'/admin/apps/blog.html');const result=applyShell(html,url);
  assert.match(result,/id="server-state"/);assert.match(result,/id="studio-brand-heading"/);assert.match(result,/id="editor"/);assert.match(result,/initializeEditor/);assert.doesNotMatch(result,/admin-menu\.js/);
  assert.match(result,/href="\/admin\/create" aria-current="page"/);assert.match(result,/id="studio-nav-back" href="\/admin\/create"/);
  assert.equal(applyShell(result,url),result);assert.equal(applyShell(html,new URL(url+'?embedded=1')),html);
  const old='<html><head></head><body><header class="site-header">OLD</header><main>Keep</main></body></html>';
  const replaced=applyShell(old,url);assert.doesNotMatch(replaced,/OLD/);assert.match(replaced,/<main>Keep<\/main>/);
});

test('missing auth configuration fails closed without a misleading login loop',async()=>{
  for(const worker of [source,bundle]){
    const response=await worker.fetch(new Request(origin+'/admin/materials'),{...env,ADMIN_PASS:undefined},ctx);
    assert.equal(response.status,503);assert.equal(response.headers.get('location'),null);
    assert.match(response.headers.get('cache-control'),/no-store/);
    assert.doesNotMatch(await response.text(),/毎日の運営チェック/);
  }
});
