import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
const root=new URL('../',import.meta.url);
const [baseline,output,sourceSha]=process.argv.slice(2);
if(!baseline||!output||!/^[a-f0-9]{40}$/.test(sourceSha||'')) throw Error('Usage: node scripts/build_admin_flat_release.mjs <baseline/public> <new-output> <source-sha>');
const contract=JSON.parse(await fs.readFile(new URL('deployment/admin-workspace/flat-release-baseline.json',root),'utf8'));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const entries=(await fs.readdir(baseline,{recursive:true,withFileTypes:true})).filter(e=>e.isFile());
if(entries.length!==Object.keys(contract.assets).length) throw Error('Baseline file set differs');
for(const entry of entries){const relative=path.relative(baseline,path.join(entry.parentPath,entry.name)).replaceAll('\\','/');if(hash(await fs.readFile(path.join(baseline,relative)))!==contract.assets[relative]) throw Error('Baseline mismatch: '+relative);}
await fs.mkdir(output); // Never overwrite prior release evidence.
// These verified assets are immutable in an admin-only release. Link them on
// the same volume instead of duplicating large videos; only the Worker changes.
for(const entry of entries){
  const source=path.join(entry.parentPath,entry.name);
  const target=path.join(output,'public',path.relative(baseline,source));
  await fs.mkdir(path.dirname(target),{recursive:true});
  await fs.link(source,target);
}
await fs.mkdir(path.join(output,'runtime'));
const worker=await fs.readFile(new URL('deployment/admin-workspace/published-worker.mjs',root));
await fs.writeFile(path.join(output,'runtime/published-worker.mjs'),worker);
const verification={source_sha:sourceSha,baseline_source_sha:contract.source_sha,assets:contract.assets,changed_assets:[],worker_sha256:hash(worker)};
await fs.writeFile(path.join(output,'verification.json'),JSON.stringify(verification,null,2)+'\n');
console.log(JSON.stringify({sourceSha,unchangedAssets:entries.length,workerBytes:worker.length,workerSha256:verification.worker_sha256}));
