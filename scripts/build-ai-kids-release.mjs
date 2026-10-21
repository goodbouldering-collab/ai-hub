import {readdirSync,readFileSync,writeFileSync,mkdirSync,copyFileSync,existsSync} from 'node:fs';
import {resolve,join,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const releaseFiles=['ai-kids/index.html','ai-kids/worksheets.html','ai-kids/assets/parent-child-discovery.png','ai-kids/assets/compare-and-create.png'];
export function hashes(directory){
  const result={};
  function walk(folder){
    for(const entry of readdirSync(folder,{withFileTypes:true})){
      const path=join(folder,entry.name);
      assert(!entry.isSymbolicLink(),'Symlinks are not release inputs');
      if(entry.isDirectory())walk(path);
      else result[relative(directory,path).replaceAll('\\','/')]=createHash('sha256').update(readFileSync(path)).digest('hex');
    }
  }
  walk(directory);
  return result;
}
export function build({baseline,output,expected,sha}){
  assert.match(sha,/^[a-f0-9]{40}$/,'Require full source SHA');
  assert(!existsSync(output),'Output exists; use a fresh directory');
  const destination=relative(resolve(baseline),resolve(output));
  assert(destination.startsWith('..') || resolve(output).split(':')[0]!==resolve(baseline).split(':')[0],'Output must be outside baseline');
  assert.deepEqual(hashes(baseline),expected,'Baseline mismatch');
  // Explicit allowlist: unrelated baseline assets cannot be replaced by source-tree files.
  const sources=releaseFiles.map(name=>[name,readFileSync(join(root,'site/static',name))]);
  for(const name of Object.keys(expected)){
    const dest=join(output,'public',name);
    mkdirSync(dirname(dest),{recursive:true});
    copyFileSync(join(baseline,name),dest);
  }
  for(const [name,bytes] of sources){
    const target=join(output,'public',name);
    mkdirSync(dirname(target),{recursive:true});
    writeFileSync(target,bytes);
  }
  const assets=hashes(join(output,'public'));
  for(const [name,digest] of Object.entries(expected))if(!releaseFiles.includes(name))assert.equal(assets[name],digest);
  assert.deepEqual(Object.keys(assets).sort(),[...new Set([...Object.keys(expected),...releaseFiles])].sort());
  const addedAssets=releaseFiles.filter(name=>!Object.hasOwn(expected,name));
  const changedAssets=releaseFiles.filter(name=>Object.hasOwn(expected,name)&&assets[name]!==expected[name]);
  const result={source_sha:sha,assets,addedAssets,changedAssets,unchangedAssets:Object.keys(expected).length-changedAssets.length};
  writeFileSync(join(output,'verification.json'),JSON.stringify(result,null,2));
  return result;
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const [baseline,output,sha]=process.argv.slice(2);
  assert(baseline&&output&&sha,'Usage: node scripts/build-ai-kids-release.mjs BASELINE OUTPUT SHA');
  const contract=JSON.parse(readFileSync(join(root,'deployment/ai-kids/baseline.json'),'utf8'));
  const worker=readFileSync(join(root,'deployment/admin-workspace/published-worker.mjs'),'utf8').replaceAll('\r\n','\n');
  assert.equal(createHash('sha256').update(worker).digest('hex'),contract.worker_sha256,'Published Worker changed');
  const result=build({baseline:resolve(baseline),output:resolve(output),expected:contract.assets,sha});
  console.log(JSON.stringify({source_sha:sha,addedAssets:result.addedAssets,changedAssets:result.changedAssets,unchangedAssets:result.unchangedAssets}));
}
