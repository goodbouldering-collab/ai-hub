import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
const require=createRequire(resolve(process.env.UX_TEST_DEPS||'tmp/dom-test','package.json'));
const {JSDOM}=require('jsdom');
const release=process.env.UX_RELEASE||'tmp/makers-release';
const js=readFileSync('site/static/design-system/studio/focused-ux.js','utf8');
const raw=readFileSync(release+'/runtime/worker/admin-assets.generated.mjs','utf8');
const admin=JSON.parse(raw.slice(raw.indexOf('{'),raw.lastIndexOf('}')+1))['/admin'].body;
function setup(html,path='/'){
 const dom=new JSDOM(html,{url:'https://aiclimb.aiclimb.workers.dev'+path,runScripts:'outside-only'});
 const w=dom.window;
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true};
 w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};
 w.HTMLElement.prototype.scrollIntoView=function(){};
 w.eval(js);return dom;
}
const home=readFileSync(release+'/public/index.html','utf8');
test('all six courses remain available; each purpose shows the correct services',()=>{
 const d=setup(home).window.document;
 const bar=d.querySelector('[aria-label="コースを目的で絞る"]');assert.ok(bar);
 const visible=()=>[...d.querySelectorAll('.compact-course-card')].filter(c=>!c.hidden);
 assert.equal(visible().length,6);bar.children[2].click();assert.equal(visible().length,1);assert.match(visible()[0].textContent,/伴走/);
 bar.children[3].click();assert.equal(visible().length,1);assert.match(visible()[0].textContent,/制作/);
 bar.children[1].click();assert.equal(visible().length,4);bar.children[0].click();assert.equal(visible().length,6);
});
test('search dialog filters, handles empty results, and restores focus',()=>{
 const {window:w}=setup(home),d=w.document,launch=d.querySelector('.ux-launcher');assert.ok(launch);launch.focus();launch.click();
 const dialog=d.querySelector('dialog'),input=dialog.querySelector('input');assert.equal(dialog.open,true);assert.equal(d.activeElement,input);
 input.value='診断';input.dispatchEvent(new w.Event('input'));assert.equal([...dialog.querySelectorAll('a')].filter(a=>!a.hidden).length,2);
 input.value='存在しない検索語';input.dispatchEvent(new w.Event('input'));assert.equal(dialog.querySelector('.ux-empty').hidden,false);
 dialog.querySelector('button').click();assert.equal(dialog.open,false);assert.equal(d.activeElement,launch);
 w.eval(js);assert.equal(d.querySelectorAll('.ux-launcher').length,1);
});
test('admin home reveals tasks while preserving existing editing forms',()=>{
 const {window:w}=setup(admin,'/admin'),d=w.document;
 assert.equal(d.querySelector('[data-ux-admin-hub]').hidden,false);assert.equal(d.querySelector('body > .container').hidden,true);
 const b=d.querySelector('.ux-task-browser'),input=b.querySelector('input');input.value='動画';input.dispatchEvent(new w.Event('input'));
 assert.equal([...b.querySelectorAll('.ux-task-card')].filter(a=>!a.hidden).length,1);
 input.value='ＳＮＳ';input.dispatchEvent(new w.Event('input'));assert.equal([...b.querySelectorAll('.ux-task-card')].filter(a=>!a.hidden).length,2);
 b.querySelector('[data-ux-filter="all"]').click();assert.equal(input.value,'');assert.equal([...b.querySelectorAll('.ux-task-card')].filter(a=>!a.hidden).length,10);
});
test('blog editor subroutes do not hide the original editing container',()=>{
 const d=setup(admin,'/admin/blog/editor').window.document;assert.equal(d.querySelector('[data-ux-admin-hub]').hidden,true);assert.equal(d.querySelector('body > .container').hidden,false);
});
test('direct links restore filtered courses and malformed hashes are safe',()=>{
 const {window:w}=setup(home),d=w.document;d.querySelector('[aria-label="コースを目的で絞る"]').children[2].click();
 w.location.hash='#ai-app-site';w.dispatchEvent(new w.HashChangeEvent('hashchange'));assert.equal(d.getElementById('ai-app-site').hidden,false);
 w.location.hash='#%';assert.doesNotThrow(()=>w.dispatchEvent(new w.HashChangeEvent('hashchange')));
});