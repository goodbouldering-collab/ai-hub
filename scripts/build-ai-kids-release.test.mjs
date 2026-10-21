import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {build, hashes, releaseFiles} from './build-ai-kids-release.mjs';

test('adds the reference page without changing any pinned public asset',()=>{
  const dir=mkdtempSync(join(tmpdir(),'ai-kids-'));
  try{
    const baseline=join(dir,'baseline');mkdirSync(baseline);
    writeFileSync(join(baseline,'index.html'),'existing homepage');
    const contract=hashes(baseline), output=join(dir,'release');
    assert.throws(()=>build({baseline,output:join(baseline,'nested'),expected:contract,sha:'a'.repeat(40)}),/outside baseline/);
    assert.throws(()=>build({baseline,output,expected:contract,sha:'uncommitted'}),/source SHA/);
    assert.equal(existsSync(output),false);
    const result=build({baseline,output,expected:contract,sha:'a'.repeat(40)});
    assert.equal(readFileSync(join(output,'public/index.html'),'utf8'),'existing homepage');
    const page=readFileSync(join(output,'public/ai-kids/index.html'),'utf8');
    assert.match(page,/noindex,follow/);
    assert.match(page,/81USstM1BF4/);
    assert.match(page,/料金・日時：未定/);
    assert.doesNotMatch(page,/<form|<iframe|<script/i);
    assert.equal(result.unchangedAssets,1);
    assert.deepEqual(result.addedAssets,releaseFiles);
    assert.match(readFileSync(join(output,'public/ai-kids/worksheets.html'),'utf8'),/page-break-after:always/);
    assert.throws(()=>build({baseline,output,expected:contract,sha:'a'.repeat(40)}),/exists/);
    writeFileSync(join(baseline,'index.html'),'changed');
    const rejected=join(dir,'rejected');
    assert.throws(()=>build({baseline,output:rejected,expected:contract,sha:'a'.repeat(40)}),/Baseline/);
    assert.equal(existsSync(rejected),false);
  }finally{rmSync(dir,{recursive:true,force:true});}
});

test('updates the existing kids page and preserves every other baseline asset',()=>{
  const dir=mkdtempSync(join(tmpdir(),'ai-kids-update-'));
  try{
    const baseline=join(dir,'baseline');mkdirSync(join(baseline,'ai-kids'),{recursive:true});
    writeFileSync(join(baseline,'index.html'),'unchanged home');
    writeFileSync(join(baseline,'ai-kids/index.html'),'old kids page');
    writeFileSync(join(baseline,'ai-kids/keep.txt'),'unlisted asset must survive');
    const result=build({baseline,output:join(dir,'release'),expected:hashes(baseline),sha:'b'.repeat(40)});
    assert.deepEqual(result.changedAssets,['ai-kids/index.html']);
    assert.equal(result.addedAssets.length,3);
    assert.equal(result.unchangedAssets,2);
    assert.equal(readFileSync(join(dir,'release/public/ai-kids/keep.txt'),'utf8'),'unlisted asset must survive');
    for(const name of releaseFiles)assert.ok(result.assets[name]);
  }finally{rmSync(dir,{recursive:true,force:true});}
});
