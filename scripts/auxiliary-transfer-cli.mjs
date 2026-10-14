import { DatabaseSync } from 'node:sqlite';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SOURCE_PROJECT, snapshotId, buildAuxiliaryEncryptedQuery, decodeAuxiliarySource } from './auxiliary-encrypted-source.mjs';
import { VAULT_DIRECTORY, initializeVault, openVault } from './auxiliary-transfer-vault.mjs';
import { restoreAuxiliarySnapshot, compareFreshAuxiliarySource, SOURCE_COUNTS } from './auxiliary-snapshot.mjs';
import { openAuxiliaryRemote, checkHistoryTarget } from './auxiliary-history.mjs';

const root=fileURLToPath(new URL('../',import.meta.url));
const registryPath=process.env.CLOUDFLARE_TARGET_REGISTRY||'C:/Project/docs/cloudflare-targets.json';
const schemaUrl=new URL('../cloudflare-runtime/migrations/0001_auxiliary_data.sql',import.meta.url);
export function validateApproval(approval,{databaseId,now=Date.now()}={}) {
  if(approval?.format!=='ai-hub-auxiliary-transfer-approval-v1'||approval.authorized!==true||!approval.approvalReference?.trim()||approval.sourceProject!==SOURCE_PROJECT||approval.rows!==33||approval.commandCenterRows!==30||approval.authRows!==0||approval.databaseName!=='aiclimb-auxiliary'||!Number.isFinite(Date.parse(approval.expiresAt))||Date.parse(approval.expiresAt)<now)throw Error('Scoped auxiliary transfer approval required');
  if(databaseId&&approval.databaseId!==databaseId)throw Error('Approved destination differs');
}
export function validateFreeze(freeze,now=Date.now()) {
  const checked=Date.parse(freeze?.checkedAt);
  if(freeze?.format!=='ai-hub-auxiliary-freeze-v1'||freeze.worker!=='aiclimb'||freeze.sourceWritersStopped!==true||freeze.d1WritesDisabled!==true||!freeze.evidence?.trim()||!Number.isFinite(checked)||checked>now||now-checked>30*60*1000)throw Error('Fresh source/target freeze evidence required');
}
export async function restoreInMemory(snapshot) {
  const sql=new DatabaseSync(':memory:');
  try {
    sql.exec(await readFile(schemaUrl,'utf8'));
    const db={prepare(query){const args=[];return {bind(...v){args.push(...v);return this;},async all(){return {success:true,results:sql.prepare(query).all(...args)};},async first(){return sql.prepare(query).get(...args)||null;},async run(){return {success:true,meta:sql.prepare(query).run(...args)};}};},async batch(statements){sql.exec('BEGIN');try{const results=[];for(const stmt of statements)results.push(await stmt.run());sql.exec('COMMIT');return results;}catch(e){sql.exec('ROLLBACK');throw e;}}};
    return await restoreAuxiliarySnapshot(db,snapshot);
  }finally{sql.close();}
}
async function run(command,id,initialId) {
  if(command==='plan')return {sourceProject:SOURCE_PROJECT,counts:SOURCE_COUNTS,portalTableFound:false,destination:'aiclimb-auxiliary / AUX_DB',vault:VAULT_DIRECTORY,productionRead:false,productionWrite:false};
  const approval=JSON.parse(await readFile(join(root,'tmp','auxiliary-transfer-approval.json'),'utf8'));
  validateApproval(approval);
  if(command==='init')return initializeVault();
  snapshotId(id);
  if(command==='query') {
    const publicKey=await readFile(join(VAULT_DIRECTORY,'public.asc'),'utf8');
    await writeFile(join(VAULT_DIRECTORY,id+'.sql'),buildAuxiliaryEncryptedQuery({id,publicKey}),{flag:'wx'});
    return {queryPrepared:true,snapshotId:id,ciphertextOnly:true};
  }
  const vault=await openVault();
  try {
    if(command==='prepare') {
      const bytes=await vault.decryptSource(id);let snapshot;
      try{snapshot=decodeAuxiliarySource(bytes,id);}finally{bytes.fill(0);}
      if(Date.now()-Date.parse(snapshot.capturedAt)>30*60*1000||Date.parse(snapshot.capturedAt)>Date.now())throw Error('Fresh source required');
      const backup=await vault.write(id,snapshot);
      const receipt=await restoreInMemory(await vault.read(id));
      return {...receipt,encryptedBackupVerified:backup.verified};
    }
    const snapshot=await vault.read(id);
    if(command==='restore-local')return restoreInMemory(snapshot);
    if(!['import','finalize'].includes(command))throw Error('Unknown command');
    const freeze=JSON.parse(await readFile(join(root,'tmp','auxiliary-transfer-freeze.json'),'utf8'));validateFreeze(freeze);
    const evidence=resolve(root,freeze.evidence);
    if(!evidence.startsWith(resolve(root)+'\\')&&!evidence.startsWith(resolve(root)+'/'))throw Error('Freeze evidence outside canonical source');
    if(!(await readFile(evidence)).length)throw Error('Freeze evidence unavailable');
    const registry=JSON.parse(await readFile(registryPath,'utf8')),project=registry.projects?.['AI相談'];
    const config=JSON.parse(await readFile(resolve(project.sourceRoot,project.target.configPath),'utf8'));
    const {db}=checkHistoryTarget(registry,config,join(root,'cloudflare-runtime'),{frozen:true});
    validateApproval(approval,{databaseId:db.database_id});
    if(Date.now()-Date.parse(snapshot.capturedAt)>30*60*1000||Date.parse(snapshot.capturedAt)>Date.now())throw Error('Fresh source required');
    // Always restore the actual encrypted backup before the remote connection.
    await restoreInMemory(snapshot);
    const remote=await openAuxiliaryRemote({registryPath,frozen:true});
    try {
      if(command==='import') {
        const tables=(await remote.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '_cf_%'").all()).results;
        if(tables.some(table=>table.name!=='auxiliary_records'&&table.name!=='d1_migrations'))throw Error('Dedicated empty/auxiliary database required');
        for(const query of (await readFile(schemaUrl,'utf8')).replace(/--[^\n]*/g,'').split(';').map(s=>s.trim()).filter(Boolean))await remote.db.prepare(query).run();
        const receipt=await restoreAuxiliarySnapshot(remote.db,snapshot),path=join(VAULT_DIRECTORY,id+'.readback.json');
        // Restart may re-check identical rows but cannot move the original
        // readback timestamp forward or overwrite a prior receipt.
        try{await writeFile(path,JSON.stringify(receipt)+'\n',{flag:'wx'});}catch(error){if(error.code!=='EEXIST')throw error;const old=JSON.parse(await readFile(path,'utf8'));if(old.sha256!==receipt.sha256)throw Error('Receipt differs');}
        return receipt;
      }
      snapshotId(initialId);
      const original=await vault.read(initialId),receipt=JSON.parse(await readFile(join(VAULT_DIRECTORY,initialId+'.readback.json'),'utf8'));
      return compareFreshAuxiliarySource(remote.db,original,snapshot,receipt);
    }finally{await remote.dispose();}
  }finally{vault.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try{console.log(JSON.stringify(await run(process.argv[2]||'plan',process.argv[3],process.argv[4])));}
  catch{console.error('Auxiliary transfer stopped. Verify scope, approved target, encrypted backup, freeze and source comparison. No plaintext was printed.');process.exitCode=1;}
}
