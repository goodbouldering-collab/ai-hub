import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { SHELL_STYLE, applyShell } from './shell.mjs';
import { ROUTES, OPERATION_SECTIONS } from './routes.mjs';
import { renderPage } from './pages.mjs';
test('current-page navigation preserves drafts; other destinations and modified clicks remain native',()=>{
 const script=SHELL_STYLE.match(/<script data-workspace-navigation>([\s\S]*?)<\/script>/)[1];
 for(const path of [...ROUTES.map(r=>r.path),'/admin/materials','/admin/operations',...OPERATION_SECTIONS.map(s=>s.path)]){
  let listener;
  const location=new URL('https://test.example'+path+'?draft=123');
  vm.runInNewContext(script,{URL,location,document:{addEventListener:(name,fn,capture)=>{assert.equal(name,'click');assert.equal(capture,true);listener=fn;}}});
  const invoke=(href,extra={},target='')=>{let prevented=false,stopped=false;listener({button:0,target:{closest:()=>({href,target,hasAttribute:()=>false})},preventDefault:()=>{prevented=true;},stopImmediatePropagation:()=>{stopped=true;},...extra});return [prevented,stopped];};
  assert.deepEqual(invoke(location.origin+path),[true,true],path);
  assert.deepEqual(invoke(location.href),[true,true]);
  for(const modifier of ['ctrlKey','metaKey','shiftKey','altKey'])assert.deepEqual(invoke(location.href,{[modifier]:true}),[false,false]);
  for(const href of [location.origin+'/admin/logout',location.origin+path+'?draft=other',location.href+'#section','https://other.example'+path])assert.deepEqual(invoke(href),[false,false]);
  assert.deepEqual(invoke(location.href,{},'_blank'),[false,false]);
  assert.deepEqual(invoke(location.href,{button:1}),[false,false]);
  const html=applyShell(renderPage(path)||'<html><head></head><body><main>editor</main></body></html>',location);
  assert.equal((html.match(/<script data-workspace-navigation>/g)||[]).length,1,path);
 }
});
