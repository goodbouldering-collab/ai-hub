import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
const root = path.resolve(import.meta.dirname, '..');
const [baseline, output] = process.argv.slice(2);
if (!baseline || !output) throw Error('Usage: node scripts/build_meo_release.mjs <verified-public> <new-output>');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const contract = JSON.parse(await fs.readFile(path.join(root,'deployment/meo-diagnosis/release-baseline.json'),'utf8'));
const entries = (await fs.readdir(baseline,{recursive:true,withFileTypes:true})).filter(e=>e.isFile());
if(entries.length!==Object.keys(contract.assets).length) throw Error('Baseline file count differs');
for(const entry of entries){const relative=path.relative(baseline,path.join(entry.parentPath,entry.name)).replaceAll('\\','/');if(hash(await fs.readFile(path.join(baseline,relative)))!==contract.assets[relative])throw Error('Baseline mismatch: '+relative);}
await fs.mkdir(output); // never overwrite previous release evidence
const source=path.join(root,'site/static/seo-llmo-diagnosis');
const changed = ['seo-llmo-diagnosis/index.html','seo-llmo-diagnosis/app.mjs','seo-llmo-diagnosis/styles.css'];
for(const entry of entries){const relative=path.relative(baseline,path.join(entry.parentPath,entry.name));const target=path.join(output,'public',relative);await fs.mkdir(path.dirname(target),{recursive:true});if(!changed.includes(relative.replaceAll('\\','/')))await fs.link(path.join(baseline,relative),target);}
const before=await fs.readFile(path.join(baseline,'seo-llmo-diagnosis/index.html'),'utf8');
const marker="<div id='audit-categories'";
if(before.split(marker).length!==2||before.includes('id="meo-panel"')) throw Error('Unexpected diagnosis baseline');
const panel=await fs.readFile(path.join(source,'meo-panel.html'),'utf8');
await fs.writeFile(path.join(output,'public/seo-llmo-diagnosis/index.html'),before.replace(marker,panel+marker));
for(const name of ['app.mjs','styles.css','meo.mjs'])await fs.copyFile(path.join(source,name),path.join(output,'public/seo-llmo-diagnosis',name));
const assets={};for(const entry of (await fs.readdir(path.join(output,'public'),{recursive:true,withFileTypes:true})).filter(e=>e.isFile())){const rel=path.relative(path.join(output,'public'),path.join(entry.parentPath,entry.name)).replaceAll('\\','/');assets[rel]=hash(await fs.readFile(path.join(output,'public',rel)));}
const actual=Object.keys(assets).filter(p=>assets[p]!==contract.assets[p]).sort();
const expected=[...changed,'seo-llmo-diagnosis/meo.mjs'].sort();if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Unexpected asset changes');
const verification={assets,changed:actual,unchanged:entries.length-changed.length,worker_sha256:hash(await fs.readFile(path.join(root,'deployment/meo-diagnosis/published-worker.mjs')))};
await fs.writeFile(path.join(output,'verification.json'),JSON.stringify(verification,null,2)+'\n');
console.log(JSON.stringify({changed:actual,unchanged:verification.unchanged,total:Object.keys(assets).length}));
