import { SOURCE_COUNTS, validateSnapshot } from './auxiliary-snapshot.mjs';
import { TABLES } from '../deployment/admin-workspace/auxiliary-store.mjs';
export const SOURCE_PROJECT='zrawhzwtppmlxyhngnju';
export function snapshotId(value) {if(typeof value!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/.test(value))throw Error('Invalid snapshot ID');return value;}
export function buildAuxiliaryEncryptedQuery({id,publicKey}) {
  snapshotId(id);
  if(typeof publicKey!=='string'||publicKey.length>100000||!/^-----BEGIN PGP PUBLIC KEY BLOCK-----\r?\n[A-Za-z0-9+/=\r\n]+-----END PGP PUBLIC KEY BLOCK-----\s*$/.test(publicKey))throw Error('Invalid public key');
  const tables=Object.keys(SOURCE_COUNTS).filter(name=>name!=='portal.sns_posts');
  const counts=tables.map(name=>`(SELECT count(*) FROM ${name})=${SOURCE_COUNTS[name]}`).join(' AND ');
  const content=tables.map(name=>`'${name}',(SELECT coalesce(jsonb_agg(to_jsonb(r)::text ORDER BY r.${TABLES[name]}::text COLLATE "C"),'[]'::jsonb) FROM ${name} r)`).join(',');
  // Only the ten observed auxiliary tables. No auth, Storage, public, customer
  // business21 tables or unobserved portal table are selected. Changed scope
  // emits a small failure object, never newly appeared rows.
  const body=`SELECT CASE WHEN (${counts}) AND to_regclass('portal.sns_posts') IS NULL THEN jsonb_build_object('version',1,'wireFormat','json-row-text-v1','source','ai-hub-supabase-auxiliary','sourceProject','${SOURCE_PROJECT}','snapshotId','${id}','capturedAt',statement_timestamp()::text,'portalTableFound',false,'tables',jsonb_build_object(${content},'portal.sns_posts','[]'::jsonb)) ELSE jsonb_build_object('error','source_scope_changed') END AS snapshot`;
  return `SELECT encode(extensions.pgp_pub_encrypt(snapshot::text,extensions.dearmor('${publicKey.trim()}'),'cipher-algo=aes256,compress-algo=1'),'base64') AS encrypted_snapshot FROM (${body}) auxiliary_source`;
}
function decimalValue(token) {
  const match=/^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/.exec(token);
  if(!match)throw Error('Invalid source number');
  let coefficient=(match[2]+(match[3]||'')).replace(/^0+/,'');
  if(!coefficient)return '0';
  let exponent=BigInt(match[4]||'0')-BigInt((match[3]||'').length);
  const zeroes=/0+$/.exec(coefficient)?.[0].length||0;
  coefficient=coefficient.slice(0,coefficient.length-zeroes);exponent+=BigInt(zeroes);
  return match[1]+coefficient+'e'+exponent;
}
export function parseLosslessSourceRow(raw) {
  if(typeof raw!=='string'||Buffer.byteLength(raw,'utf8')>96*1024)throw Error('Invalid source row text');
  // Match entire JSON strings first so digits inside text/escaped quotes are
  // never treated as numeric values. Compare decimal values before JSON.parse
  // can round PostgreSQL bigint/numeric or nested JSON numbers.
  for(const match of raw.matchAll(/"(?:\\.|[^"\\])*"|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g)) {
    if(!match[1])continue;
    const number=Number(match[1]);
    if(!Number.isFinite(number)||decimalValue(match[1])!==decimalValue(String(number)))throw Error('Source numeric precision cannot be preserved');
  }
  const row=JSON.parse(raw);
  if(!row||typeof row!=='object'||Array.isArray(row))throw Error('Invalid source row');
  return row;
}
export function decodeAuxiliarySource(bytes,id) {
  if(!Buffer.isBuffer(bytes)||bytes.length>10000000)throw Error('Invalid encrypted source');
  const value=JSON.parse(bytes.toString('utf8'));
  if(value.sourceProject!==SOURCE_PROJECT||value.snapshotId!==snapshotId(id)||value.wireFormat!=='json-row-text-v1'||!Number.isFinite(Date.parse(value.capturedAt)))throw Error('Source identity changed');
  const tables=Object.fromEntries(Object.entries(value.tables||{}).map(([name,rows])=>{
    if(!Array.isArray(rows))throw Error('Invalid source table');
    return [name,rows.map(parseLosslessSourceRow)];
  }));
  const {wireFormat,...snapshot}=value;
  return validateSnapshot({...snapshot,tables});
}
