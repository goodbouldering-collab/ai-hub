import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {build, hashes} from './build-ai-kids-release.mjs';

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
    assert.throws(()=>build({baseline,output,expected:contract,sha:'a'.repeat(40)}),/exists/);
    writeFileSync(join(baseline,'index.html'),'changed');
    const rejected=join(dir,'rejected');
    assert.throws(()=>build({baseline,output:rejected,expected:contract,sha:'a'.repeat(40)}),/Baseline/);
    assert.equal(existsSync(rejected),false);
  }finally{rmSync(dir,{recursive:true,force:true});}
});
