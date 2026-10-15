import test from 'node:test';
import assert from 'node:assert/strict';
import source from './worker.mjs';
import bundle from './published-worker.mjs';
import { ROUTES, canonicalUrl } from './routes.mjs';
import { applyShell } from './shell.mjs';
import { renderPage } from './pages.mjs';

test('retired landing pages resolve to a single function, retaining context',()=>{
  assert.equal(canonicalUrl('/admin/create?draft=1#step-2'),'/admin/blog-create?draft=1#step-2');
  assert.equal(canonicalUrl('/admin/prompts?q=one'),'/admin/ops?q=one#sec-prompts');
  assert.equal(canonicalUrl('/ops/prompts'),'/admin/ops#sec-prompts');
  assert.equal(canonicalUrl('/admin/ops'),'/admin/ops');
});
test('home catalogue lists each current function exactly once',()=>{
  const html=applyShell(renderPage('/admin'),new URL('https://test.example/admin')).match(/<main[\s\S]*?<\/main>/)[0];
  for(const route of ROUTES.filter(r=>!r.archive)){
    assert.equal([...html.matchAll(/href="([^"]+)"/g)].filter(m=>m[1]===route.path).length,1,route.path);
  }
  assert.doesNotMatch(html,/href="\/admin\/(create|prompts|sns-cross-media-dashboard)"/);
});
test('creation navigation has one destination each and replaces legacy menus without touching editor',()=>{
  const html='<html><head></head><body><nav class="studio-tabs"><a id="studio-nav-back" href="/admin/blog-editor">Back</a></nav><nav class="blog-page-nav"><a href="/admin/blog">全体</a><a href="/admin/blog/generate">生成</a></nav><textarea id="editor"></textarea><script>initializeEditor()</script></body></html>';
  const result=applyShell(html,new URL('https://test.example/admin/blog-create'));
  assert.doesNotMatch(result,/<nav class="(?:studio-tabs|blog-page-nav)"/);
  assert.equal((result.match(/aria-label="制作・発信メニュー"/g)||[]).length,1);
  const nav=result.match(/<nav[^>]*aria-label="制作・発信メニュー"[\s\S]*?<\/nav>/)[0];
  const links=[...nav.matchAll(/href="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(links).size,links.length);
  assert.equal(links.length,ROUTES.filter(r=>r.group==='create').length);
  assert.match(result,/id="editor"/);assert.match(result,/initializeEditor/);
});
for(const worker of [source,bundle]) test('retired pages remain authenticated and redirect without executing actions',async()=>{
  const origin='https://test.example';
  const env={ADMIN_PASS:'test-only',ADMIN_SESSION_SECRET:'test-only-session-secret',ADMIN_LOGIN_LIMITER:{limit:async()=>({success:true})}};
  const ctx={waitUntil(){}};
  const login=await worker.fetch(new Request(origin+'/admin/login',{method:'POST',headers:{origin,'content-type':'application/x-www-form-urlencoded'},body:'password=test-only'}),env,ctx);
  const cookie=login.headers.get('set-cookie').split(';')[0];
  for(const [old,target] of [['/admin/create','/admin/blog-create'],['/admin/prompts','/admin/ops#sec-prompts'],['/ops/prompts','/admin/ops#sec-prompts']]){
    assert.equal((await worker.fetch(new Request(origin+old),env,ctx)).status,303);
    const result=await worker.fetch(new Request(origin+old,{headers:{cookie}}),env,ctx);
    assert.equal(result.status,302);assert.equal(result.headers.get('location'),target);
    assert.equal((await worker.fetch(new Request(origin+old,{method:'POST',headers:{cookie}}),env,ctx)).status,405);
  }
});

test('separate pages retain their own contents and no global function grid',()=>{
 const home=renderPage('/admin'),materials=renderPage('/admin/materials'),operations=renderPage('/admin/operations');
 assert.match(materials,/id="material-search"/);assert.match(materials,/id="material-list"/);assert.match(materials,/data-material-search/);assert.match(operations,/予定・指示/);assert.match(operations,/相場・取引の管理/);
 assert.notEqual(home,materials);assert.notEqual(home,operations);
 for(const page of [home,materials,operations])assert.doesNotMatch(page,/workspace-button-grid/);
 const result=applyShell('<html><head></head><body><main><textarea id="editor"></textarea></main></body></html>',new URL('https://test.example/admin/blog-create'));
 assert.match(result,/制作・発信メニュー/);assert.doesNotMatch(result,/href="\/admin\/trade"/);assert.match(result,/id="editor"/);
});
