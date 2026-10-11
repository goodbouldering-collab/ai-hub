import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import worker from '../deployment/admin-workspace/worker.mjs';
import bundledWorker from '../deployment/admin-workspace/published-worker.mjs';
import { auxiliaryStore } from '../deployment/admin-workspace/auxiliary-store.mjs';
import { SOURCE_COUNTS, restoreAuxiliarySnapshot, compareFreshAuxiliarySource, exportAuxiliary } from '../scripts/auxiliary-snapshot.mjs';
import { checkHistoryTarget } from '../scripts/auxiliary-history.mjs';
import { randomBytes } from 'node:crypto';
import { encryptBackup, decryptBackup } from '../scripts/auxiliary-transfer-vault.mjs';
import { buildAuxiliaryEncryptedQuery, decodeAuxiliarySource, parseLosslessSourceRow, SOURCE_PROJECT } from '../scripts/auxiliary-encrypted-source.mjs';
import { validateApproval, validateFreeze, restoreInMemory } from '../scripts/auxiliary-transfer-cli.mjs';

function d1(){
  const sql=new DatabaseSync(':memory:');sql.exec(readFileSync(new URL('../cloudflare-runtime/migrations/0001_auxiliary_data.sql',import.meta.url),'utf8'));
  const db={prepare(query){const args=[];return {bind(...values){args.push(...values);return this;},async all(){return {success:true,results:sql.prepare(query).all(...args)};},async first(){return sql.prepare(query).get(...args)||null;},async run(){return {success:true,meta:sql.prepare(query).run(...args)};}};},async batch(statements){sql.exec('BEGIN');try{const results=[];for(const s of statements)results.push(await s.run());sql.exec('COMMIT');return results;}catch(e){sql.exec('ROLLBACK');throw e;}},close(){sql.close();}};
  return db;
}
const origin='https://unit.example';
const env={ADMIN_PASS:'synthetic-only-password',ADMIN_SESSION_SECRET:'synthetic-only-secret',ADMIN_LOGIN_LIMITER:{limit:async()=>({success:true})},AUXILIARY_BACKEND:'d1',AUXILIARY_WRITES:'enabled',ASSETS:{fetch:async()=>new Response('public fixture')}};
const ctx={waitUntil(){}};
async function login(environment){const response=await worker.fetch(new Request(origin+'/admin/login',{method:'POST',headers:{origin,'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({password:env.ADMIN_PASS})}),environment,ctx);assert.equal(response.status,303);return response.headers.get('set-cookie').split(';')[0];}
function request(path,cookie,body,headers={}){return new Request(origin+path,{method:body===undefined?'GET':'POST',headers:{cookie,origin,'content-type':'application/json',...headers},body:body===undefined?undefined:JSON.stringify(body)});}
const data='/api/admin/command-center/data';
test('actual existing auth precedes D1; no public API, no fallback, unchanged public assets',async t=>{
 const db=d1();t.after(()=>db.close());const environment={...env,AUX_DB:db},cookie=await login(environment);
 assert.equal((await worker.fetch(request(data,''),environment,ctx)).status,401);
 assert.equal((await worker.fetch(request(data,cookie),{...environment,ADMIN_PASS:undefined},ctx)).status,503);
 assert.equal((await worker.fetch(request(data,cookie),{...environment,AUX_DB:undefined},ctx)).status,503);
 assert.equal((await worker.fetch(request(data,cookie),{...environment,AUXILIARY_BACKEND:undefined},ctx)).status,503);
 assert.equal((await worker.fetch(new Request(origin+'/'),environment,ctx)).status,200);
 const response=await worker.fetch(request(data,cookie),environment,ctx);assert.equal(response.status,200);assert.match(response.headers.get('cache-control'),/private, no-store/);assert.deepEqual((await response.json()).tasks,[]);
});
test('all task/directive/execution actions persist, enforce owner and keep failure inputs unsent',async t=>{
 const db=d1();t.after(()=>db.close());const environment={...env,AUX_DB:db},cookie=await login(environment);
 const send=body=>worker.fetch(request(data,cookie,body),environment,ctx);
 const body={action:'create_task',businessId:'fixture',title:'synthetic task',dueDate:'2026-10-12',priority:2};
 assert.equal((await worker.fetch(request(data,cookie,body,{origin:'https://attacker.example'}),environment,ctx)).status,403);
 assert.equal((await worker.fetch(request(data,cookie,body),{...environment,AUXILIARY_WRITES:undefined},ctx)).status,503);
 assert.equal((await worker.fetch(request(data,cookie,{...body,title:'a'.repeat(70000)}),environment,ctx)).status,400);
 let response=await send(body);assert.equal(response.status,200);let task=(await response.json()).tasks[0];assert.equal(task.title,'synthetic task');
 assert.equal((await send({action:'update_task',id:task.id,status:'done'})).status,200);
 assert.equal((await worker.fetch(request(data,cookie,{action:'update_task',id:task.id,status:'planned'}),{...environment,COMMAND_CENTER_OWNER_ID:'another-owner'},ctx)).status,409);
 assert.equal((await send({action:'create_directive',id:'directive1',businessId:'fixture',mode:'hold',instruction:'fixture instruction'})).status,200);
 const execution={action:'record_execution',id:'exec1',directiveId:'directive1',businessId:'fixture',mode:'hold',instruction:'fixture instruction',status:'running',result:'fixture result'};
 assert.equal((await send(execution)).status,200);response=await send({...execution,status:'completed'});assert.equal((await response.json()).executions[0].status,'completed');
});
test('trade plans execute atomically once, preserve approvals, closed-only removal',async t=>{
 const db=d1();t.after(()=>db.close());const environment={...env,AUX_DB:db},cookie=await login(environment);
 const send=body=>worker.fetch(request(data,cookie,body),environment,ctx);
 const response=await send({action:'create_trade_plan',market:'fixture',symbol:'TEST',tradeStyle:'cash',direction:'long'});assert.equal(response.status,200);const plan=(await response.json()).tradePlans[0];
 const execute={action:'execute_trade_plan',id:plan.id,tradedAt:'2026-10-12',entryPrice:10,quantity:1};
 assert.equal((await send(execute)).status,409);assert.equal((await send({action:'approve_trade_plan',id:plan.id})).status,200);
 assert.equal((await send(execute)).status,200);assert.equal((await send(execute)).status,409);
 const dashboard=await (await worker.fetch(request(data,cookie),environment,ctx)).json();assert.equal(dashboard.trades.length,1);
 const trade=dashboard.trades[0];assert.equal((await send({action:'delete_trade',id:trade.id})).status,409);
 assert.equal((await send({action:'close_trade',id:trade.id,pnl:-1})).status,200);assert.equal((await send({action:'delete_trade',id:trade.id})).status,200);
});
test('SNS history is private read-only; no SNS send or new credentials',async t=>{
 const db=d1();t.after(()=>db.close());const environment={...env,AUX_DB:db},cookie=await login(environment);
 await auxiliaryStore(db).insert('portal.sns_posts',{id:1,created_at:'2026-10-12T00:00:00Z',text:'synthetic history',x_status:'skipped',threads_status:'skipped'});
 const path='/api/admin/sns-history';assert.equal((await worker.fetch(request(path,''),environment,ctx)).status,401);
 assert.equal((await worker.fetch(request(path,cookie,{}),environment,ctx)).status,405);
 const result=await (await worker.fetch(request(path,cookie),environment,ctx)).json();assert.equal(result.posts[0].text,'synthetic history');
 assert.equal((await worker.fetch(request('/api/admin/sns-post',cookie,{}),environment,ctx)).status,503);
});
function snapshot(){const tables={};for(const [name,count] of Object.entries(SOURCE_COUNTS)){tables[name]=Array.from({length:count},(_,i)=>name==='ai_watch.articles'?{hash:'fixture'+i,source:'fixture',url:'https://example.org/'+i,title:'synthetic',first_seen:'2026-01-01',last_seen:'2026-01-01'}:name==='command_center.projects'?{business_id:'fixture'+i,owner_id:'site-owner',display_name:'synthetic'}:{id:'fixture'+i,owner_id:'site-owner',business_id:'fixture0',instruction:'synthetic only',created_at:'2026-01-01T00:00:00Z',extra_preserved:{nested:true}});}
 return {version:1,source:'ai-hub-supabase-auxiliary',portalTableFound:false,capturedAt:'2026-01-01T00:00:00Z',tables};}
test('all 33 synthetic rows restore byte-equivalently; resume and fresh comparison do not overwrite',async t=>{
 const db=d1(),freshDb=d1();t.after(()=>{db.close();freshDb.close();});const source=snapshot();
 await auxiliaryStore(db).insert('command_center.projects',source.tables['command_center.projects'][0]);
 const receipt=await restoreAuxiliarySnapshot(db,source);assert.equal(receipt.rows,33);assert.equal(receipt.sourceReverified,false);
 assert.equal((await restoreAuxiliarySnapshot(db,source)).sha256,receipt.sha256);
 assert.equal((await restoreAuxiliarySnapshot(freshDb,source)).sha256,receipt.sha256);
 assert.equal((await compareFreshAuxiliarySource(db,source,{...source,capturedAt:new Date(Date.parse(receipt.readbackAt)+1000).toISOString()},receipt)).sourceReverified,true);
 await assert.rejects(compareFreshAuxiliarySource(db,source,{...source,capturedAt:'2026-10-12T00:01:00Z'}),/after destination/);
 const changed=structuredClone(source);changed.tables['command_center.tasks'][0].instruction='changed';await assert.rejects(restoreAuxiliarySnapshot(db,changed),/differs/);
 await auxiliaryStore(db).update('command_center.tasks','fixture0','site-owner',row=>({...row,status:'done'}));await assert.rejects(restoreAuxiliarySnapshot(db,source),/no overwrite/);
 assert.equal((await exportAuxiliary(db))['command_center.tasks'][0].status,'done');
 const scope=structuredClone(source);scope.tables['command_center.relay_nonces'].push({nonce:'fixture'});await assert.rejects(restoreAuxiliarySnapshot(freshDb,scope),/count changed/);
});
test('article history preserves original content and first_seen, classifies duplicate hashes',async t=>{
 const db=d1();t.after(()=>db.close());const store=auxiliaryStore(db);
 const article={hash:'fixture',source:'fixture',category:'test',title:'original',url:'https://example.org',body:'original',published:null};
 assert.deepEqual(await store.upsertArticles([article,article]),{newHashes:['fixture'],existingHashes:['fixture']});
 const before=await store.get('ai_watch.articles','fixture','');await store.upsertArticles([{...article,title:'changed'}]);const after=await store.get('ai_watch.articles','fixture','');
 assert.equal(after.row.title,'original');assert.equal(after.row.first_seen,before.row.first_seen);
});
test('article writer requires the exact registered canonical D1 and enabled write gate',()=>{
 const db={binding:'AUX_DB',database_name:'aiclimb-auxiliary',database_id:'00000000-0000-0000-0000-000000000001'};
 const registry={cloudflareAccount:{accountId:'fixture-account'},projects:{'AI相談':{sourceRoot:'C:/Project/AI相談',target:{status:'verified',name:'aiclimb',workingDirectory:'work/genspark-profile-edit/cloudflare-runtime',d1Bindings:[{binding:'AUX_DB',status:'verified',databaseName:db.database_name,databaseId:db.database_id}]}}}};
 const config={name:'aiclimb',account_id:'fixture-account',d1_databases:[db],vars:{AUXILIARY_BACKEND:'d1',AUXILIARY_WRITES:'enabled'}},cwd='C:/Project/AI相談/work/genspark-profile-edit/cloudflare-runtime';
 assert.equal(checkHistoryTarget(registry,config,cwd).db.database_name,'aiclimb-auxiliary');
 assert.throws(()=>checkHistoryTarget(registry,config,'C:/Project/AI相談/work/other'),/Canonical/);
 assert.throws(()=>checkHistoryTarget(registry,{...config,account_id:'other'},cwd),/Registered/);
 assert.throws(()=>checkHistoryTarget(registry,{...config,vars:{}},cwd),/not enabled/);
 assert.throws(()=>checkHistoryTarget(registry,{...config,d1_databases:[]},cwd),/Registered/);
});
test('published bundle handles the actual D1 API and HEAD with the unchanged login cookie',async t=>{
 const db=d1();t.after(()=>db.close());const environment={...env,AUX_DB:db},cookie=await login(environment);
 assert.equal((await bundledWorker.fetch(request(data,''),environment,ctx)).status,401);
 const response=await bundledWorker.fetch(request(data,cookie,{action:'create_task',businessId:'fixture',title:'bundle fixture',dueDate:'2026-10-12'}),environment,ctx);
 assert.equal(response.status,200);assert.equal((await response.json()).tasks[0].title,'bundle fixture');
 const head=await bundledWorker.fetch(new Request(origin+data+'/',{method:'HEAD',headers:{cookie}}),environment,ctx);assert.equal(head.status,200);assert.equal(await head.text(),'');assert.match(head.headers.get('cache-control'),/no-store/);
 const malformed=await bundledWorker.fetch(request(data,cookie,{action:'create_task',businessId:'fixture',title:'invalid date',dueDate:'2026-99-99'}),environment,ctx);assert.equal(malformed.status,400);
});
test('source SQL selects only approved auxiliary tables and encrypts changed-scope failures',()=>{
 const publicKey='-----BEGIN PGP PUBLIC KEY BLOCK-----\nQUJD\n-----END PGP PUBLIC KEY BLOCK-----';
 const query=buildAuxiliaryEncryptedQuery({id:'synthetic-source',publicKey});
 assert.match(query,/pgp_pub_encrypt/);assert.match(query,/CASE WHEN/);assert.match(query,/to_regclass\('portal.sns_posts'\) IS NULL/);
 assert.doesNotMatch(query,/\b(auth|storage|public)\./);assert.doesNotMatch(query,/FROM portal\.sns_posts/);
 for(const [name,count]of Object.entries(SOURCE_COUNTS))if(name!=='portal.sns_posts')assert.ok(query.includes(`count(*) FROM ${name})=${count}`));
 assert.throws(()=>buildAuxiliaryEncryptedQuery({id:"x'; DROP",publicKey}),/snapshot ID/);
 assert.throws(()=>buildAuxiliaryEncryptedQuery({id:'fixture',publicKey:publicKey.replace('QUJD',"QUJD'")}),/public key/);
 assert.match(query,/jsonb_agg\(to_jsonb\(r\)::text/);
 const source=snapshot();const value={...source,wireFormat:'json-row-text-v1',tables:Object.fromEntries(Object.entries(source.tables).map(([name,rows])=>[name,rows.map(row=>JSON.stringify(row))])),sourceProject:SOURCE_PROJECT,snapshotId:'fixture'};assert.equal(decodeAuxiliarySource(Buffer.from(JSON.stringify(value)),'fixture').sourceProject,SOURCE_PROJECT);
 assert.throws(()=>decodeAuxiliarySource(Buffer.from(JSON.stringify({...value,sourceProject:'other'})),'fixture'),/identity/);
 const lossy=structuredClone(value);lossy.tables['command_center.tasks'][0]='{"id":"fixture","owner_id":"site-owner","nested":{"amount":9007199254740993}}';assert.throws(()=>decodeAuxiliarySource(Buffer.from(JSON.stringify(lossy)),'fixture'),/precision/);
});
test('PostgreSQL row text rejects numeric precision loss before parsing and ignores quoted digits',()=>{
 for(const raw of ['{"id":9007199254740993}','{"nested":[0.123456789012345678901]}','{"tiny":1e-999}','{"large":1e999}'])assert.throws(()=>parseLosslessSourceRow(raw),/precision/);
 assert.deepEqual(parseLosslessSourceRow('{"id":9007199254740991,"price":12.5000,"x":1e3,"tiny":1e-10}'),{id:9007199254740991,price:12.5,x:1000,tiny:1e-10});
 const quoted={id:'9007199254740993',text:'escaped "0.123456789012345678901" 1e999'};assert.deepEqual(parseLosslessSourceRow(JSON.stringify(quoted)),quoted);
});
test('AES backup restores the complete fixture; altered ciphertext and another business key fail',async()=>{
 const key=randomBytes(32),source=snapshot(),encrypted=encryptBackup(source,key);
 const restored=decryptBackup(encrypted,key);assert.deepEqual(restored,source);
 assert.equal((await restoreInMemory(restored)).rows,33);
 assert.throws(()=>decryptBackup(encrypted,randomBytes(32)),/vault/);
 const changed=structuredClone(encrypted);changed.ciphertext=(changed.ciphertext[0]==='A'?'B':'A')+changed.ciphertext.slice(1);assert.throws(()=>decryptBackup(changed,key),/vault/);
 assert.throws(()=>decryptBackup({...encrypted,format:'notesthe-encrypted-transfer-v1'},key),/vault/);
 key.fill(0);
});
test('production transfer requires scoped approval plus recent source and destination freeze evidence',()=>{
 const now=Date.now(),approval={format:'ai-hub-auxiliary-transfer-approval-v1',authorized:true,approvalReference:'synthetic-only',sourceProject:SOURCE_PROJECT,rows:33,commandCenterRows:30,authRows:0,databaseName:'aiclimb-auxiliary',databaseId:'fixture-id',expiresAt:new Date(now+10000).toISOString()};
 validateApproval(approval,{databaseId:'fixture-id',now});assert.throws(()=>validateApproval({...approval,authRows:1},{now}),/approval/);assert.throws(()=>validateApproval(approval,{databaseId:'other',now}),/differs/);
 const freeze={format:'ai-hub-auxiliary-freeze-v1',worker:'aiclimb',sourceWritersStopped:true,d1WritesDisabled:true,evidence:'tmp/synthetic.json',checkedAt:new Date(now).toISOString()};validateFreeze(freeze,now);
 assert.throws(()=>validateFreeze({...freeze,sourceWritersStopped:false},now),/freeze/);assert.throws(()=>validateFreeze(freeze,now+1800001),/freeze/);
});
