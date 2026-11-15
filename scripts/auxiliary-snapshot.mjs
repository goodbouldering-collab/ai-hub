import { createHash } from 'node:crypto';
import { auxiliaryStore, identity, TABLES } from '../deployment/admin-workspace/auxiliary-store.mjs';

export const SOURCE_COUNTS = Object.freeze({
  'command_center.projects':15,'command_center.tasks':8,'command_center.directives':5,
  'command_center.directive_executions':2,'command_center.trades':0,'command_center.trade_plans':0,
  'command_center.relay_state':0,'command_center.relay_requests':0,'command_center.relay_nonces':0,
  'ai_watch.articles':3,'portal.sns_posts':0,
});
const stable = value => Array.isArray(value)?value.map(stable):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,stable(value[key])])):value;
const text = value => JSON.stringify(stable(value));
export const digest = value => createHash('sha256').update(text(value)).digest('hex');
export function validateSnapshot(snapshot) {
  // The portal table was NOT found. This is not a claim that a live table has zero rows.
  if(snapshot?.version!==1||snapshot?.source!=='ai-hub-supabase-auxiliary'||snapshot?.portalTableFound!==false)throw Error('Unexpected source scope');
  if(Object.keys(snapshot.tables||{}).sort().join('|')!==Object.keys(TABLES).sort().join('|'))throw Error('Unexpected source tables');
  for(const [name,count] of Object.entries(SOURCE_COUNTS)) {
    const rows=snapshot.tables[name];if(!Array.isArray(rows)||rows.length!==count)throw Error('Source count changed');
    const keys=new Set();for(const row of rows){const {key}=identity(name,row);if(keys.has(key))throw Error('Duplicate source key');keys.add(key);}
  }
  return snapshot;
}
const normalized = tables => Object.fromEntries(Object.entries(tables).map(([name,rows])=>[name,[...rows].sort((a,b)=>identity(name,a).key.localeCompare(identity(name,b).key))]));
export async function exportAuxiliary(db) {
  const store=auxiliaryStore(db), tables={};
  for(const name of Object.keys(TABLES))tables[name]=(await store.raw(name)).map(item=>item.row);
  return normalized(tables);
}
export async function restoreAuxiliarySnapshot(db,snapshot) {
  validateSnapshot(snapshot);
  const store=auxiliaryStore(db),missing=[];
  // Inspect EVERY table before writing anything. Unknown destinations, changes,
  // and already-used D1 records block an import instead of overwriting data.
  for(const name of Object.keys(TABLES)) {
    const source=new Map(snapshot.tables[name].map(row=>[identity(name,row).key,row]));
    for(const item of await store.raw(name)) {
      const key=identity(name,item.row).key;
      if(item.revision!==1||!source.has(key)||text(source.get(key))!==text(item.row))throw Error('Destination differs; no overwrite');
      source.delete(key);
    }
    for(const row of source.values()){const {key,owner,payload}=identity(name,row);missing.push(db.prepare('INSERT INTO auxiliary_records(namespace, record_key, owner_id, payload) VALUES (?, ?, ?, ?)').bind(name,key,owner,payload));}
  }
  if(missing.length) {
    const results=await db.batch(missing);if(results.some(result=>result.success===false))throw Error('Import failed');
  }
  const expected=normalized(snapshot.tables),actual=await exportAuxiliary(db);
  if(digest(actual)!==digest(expected))throw Error('Full readback differs');
  return {rows:33,counts:SOURCE_COUNTS,sha256:digest(actual),readbackAt:new Date().toISOString(),sourceReverified:false};
}
export async function compareFreshAuxiliarySource(db,original,fresh,receipt) {
  validateSnapshot(original);validateSnapshot(fresh);
  if(!Number.isFinite(Date.parse(original.capturedAt))||!Number.isFinite(Date.parse(fresh.capturedAt))||Date.parse(fresh.capturedAt)<=Date.parse(original.capturedAt))throw Error('A new source observation is required');
  if(!receipt||receipt.sha256!==digest(normalized(original.tables))||!Number.isFinite(Date.parse(receipt.readbackAt))||Date.parse(fresh.capturedAt)<=Date.parse(receipt.readbackAt))throw Error('Source must be re-observed after destination readback');
  if(digest(normalized(original.tables))!==digest(normalized(fresh.tables)))throw Error('Source changed; keep writes frozen');
  const actual=await exportAuxiliary(db);
  if(digest(actual)!==digest(normalized(fresh.tables)))throw Error('Destination changed');
  return {rows:33,sha256:digest(actual),sourceReverified:true};
}
