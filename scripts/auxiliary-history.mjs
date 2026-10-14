import { readFile, writeFile, mkdtemp, mkdir } from 'node:fs/promises';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { auxiliaryStore } from '../deployment/admin-workspace/auxiliary-store.mjs';
const run=promisify(execFile),root=fileURLToPath(new URL('../',import.meta.url));
export function checkHistoryTarget(registry,config,cwd,{frozen=false}={}) {
  const project=registry.projects?.['AI相談'],target=project?.target;
  const db=config.d1_databases?.find(item=>item.binding==='AUX_DB'),registered=target?.d1Bindings?.find(item=>item.binding==='AUX_DB');
  if(target?.status!=='verified'||target.name!=='aiclimb'||config.name!==target.name||resolve(project.sourceRoot,target.workingDirectory)!==resolve(cwd))throw Error('Canonical AI相談 target required');
  if(config.account_id!==registry.cloudflareAccount?.accountId||!config.account_id||db?.database_name!=='aiclimb-auxiliary'||!/^[a-f0-9-]{36}$/i.test(db?.database_id??'')||registered?.status!=='verified'||registered.databaseId!==db.database_id||registered.databaseName!==db.database_name)throw Error('Registered auxiliary D1 required');
  if(frozen) {
    if(config.vars?.AUXILIARY_BACKEND!=='disabled'||config.vars?.AUXILIARY_WRITES!=='frozen')throw Error('Explicit auxiliary freeze required');
  } else if(config.vars?.AUXILIARY_BACKEND!=='d1'||config.vars?.AUXILIARY_WRITES!=='enabled')throw Error('Auxiliary writes are not enabled');
  return {project,db};
}
export async function openAuxiliaryRemote({registryPath=process.env.CLOUDFLARE_TARGET_REGISTRY||'C:/Project/docs/cloudflare-targets.json',frozen=false}={}) {
  const registry=JSON.parse(await readFile(registryPath,'utf8'));
  const project=registry.projects?.['AI相談'];
  const config=JSON.parse(await readFile(resolve(project.sourceRoot,project.target.configPath),'utf8'));
  const cwd=join(root,'cloudflare-runtime'),{db}=checkHistoryTarget(registry,config,cwd,{frozen});
  const head=(await run('git',['rev-parse','HEAD'],{cwd:root})).stdout.trim();
  const remote=(await run('git',['ls-remote','origin','refs/heads/main'],{cwd:root})).stdout.trim().split(/\s+/)[0];
  if(head!==remote)throw Error('Integrated source required');
  const inputs=['scripts/auxiliary-history.mjs','deployment/admin-workspace/auxiliary-store.mjs','core/differ.py','core/d1_history.py','cloudflare-runtime/wrangler-profile-release.jsonc'];
  if(frozen)inputs.push('scripts/auxiliary-snapshot.mjs','scripts/auxiliary-encrypted-source.mjs','scripts/auxiliary-transfer-vault.mjs','scripts/auxiliary-transfer-cli.mjs','cloudflare-runtime/migrations/0001_auxiliary_data.sql');
  if((await run('git',['status','--porcelain','--untracked-files=all','--',...inputs],{cwd:root})).stdout.trim())throw Error('History inputs must be committed');
  const guard=resolve(dirname(registryPath),'../scripts/assert-cloudflare-target.ps1');
  await run('powershell.exe',['-NoProfile','-ExecutionPolicy','Bypass','-File',guard,'-ProjectRoot',project.sourceRoot,'-TargetKey','default','-ForDeploy'],{cwd,windowsHide:true,timeout:120000});
  await mkdir(join(root,'tmp'),{recursive:true});
  const folder=await mkdtemp(join(root,'tmp','aux-history-')),configPath=join(folder,'wrangler.json');
  await writeFile(configPath,JSON.stringify({name:config.name,account_id:config.account_id,compatibility_date:config.compatibility_date,d1_databases:[{...db,remote:true}]}));
  const {getPlatformProxy}=await import('wrangler');
  const proxy=await getPlatformProxy({configPath,envFiles:[],persist:false,remoteBindings:true});
  if(!proxy.env.AUX_DB){await proxy.dispose();throw Error('Auxiliary D1 unavailable');}
  return {db:proxy.env.AUX_DB,databaseId:db.database_id,dispose:()=>proxy.dispose()};
}
export async function runHistory(articles,options={}) {
  if(!Array.isArray(articles)||articles.length>200)throw Error('Invalid article batch');
  for(const article of articles) {
    if(!article||Object.keys(article).some(key=>!['hash','source','category','title','url','body','published'].includes(key))||typeof article.hash!=='string'||!/^[a-f0-9]{16,64}$/.test(article.hash)||!['source','category','title','url'].every(key=>typeof article[key]==='string'))throw Error('Invalid public article');
    const url=new URL(article.url);if(url.protocol!=='https:'||url.username||url.password)throw Error('Invalid article URL');
  }
  const proxy=await openAuxiliaryRemote(options);
  try{return await auxiliaryStore(proxy.db).upsertArticles(articles);}finally{await proxy.dispose();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {
    if(process.argv[2]!=='upsert')throw Error('Use upsert with a JSON public-article array on stdin');
    let body='',size=0;for await(const chunk of process.stdin){size+=chunk.length;if(size>8*1024*1024)throw Error('Input too large');body+=chunk;}
    const result=await runHistory(JSON.parse(body));process.stdout.write(JSON.stringify(result)+'\n');
  }catch{process.stderr.write('Article history failed; verify the registered D1, canonical source and write gate. No fallback was used.\n');process.exitCode=1;}
}
