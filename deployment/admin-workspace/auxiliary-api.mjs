import { auxiliaryStore, Conflict } from './auxiliary-store.mjs';

const HEADERS = {'cache-control':'private, no-store','x-content-type-options':'nosniff','x-robots-tag':'noindex, nofollow'};
const json = (value, status=200) => Response.json(value, {status, headers:HEADERS});
export const auxiliaryPath = path => ['/api/admin/command-center/data','/api/admin/sns-history'].includes(path);
const fields = {
  projects:'business_id display_name status status_label production_url hint last_review_date',
  tasks:'id business_id title reason priority status due_date effort blocker category created_at updated_at',
  directives:'id business_id mode instruction created_at',
  directive_executions:'id directive_id owner_id business_id mode instruction status summary result error thread_id version has_changes started_at completed_at updated_at',
  trades:'id traded_at market symbol direction status entry_price quantity risk_amount pnl memo',
  trade_plans:'id market symbol name trade_style direction signal_score reference_price quantity stop_price target_price max_loss thesis invalidation source_as_of status trade_id created_at updated_at',
  sns_posts:'id created_at text image_url x_status x_post_id x_error threads_status threads_post_id threads_error',
};
const orders = {projects:'display_name',tasks:'updated_at',directives:'created_at',directive_executions:'updated_at',trades:'traded_at',trade_plans:'created_at',sns_posts:'created_at'};
const camel = key => key.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
function mapAuxiliaryRow(table,row) {
  const result = Object.fromEntries(fields[table].split(' ').map(key=>[camel(key),row[key] ?? '']));
  if(table==='directives') result.createdAtLabel = new Intl.DateTimeFormat('ja-JP',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit',timeZone:'Asia/Tokyo'}).format(new Date(row.created_at));
  return result;
}
async function readAuxiliaryRows(store,table,owner,limit=200) {
  return (await store.list(table==='sns_posts'?'portal.sns_posts':'command_center.'+table,owner)).map(item=>item.row)
    .sort((a,b)=>String(b[orders[table]]??'').localeCompare(String(a[orders[table]]??''))).slice(0,limit).map(row=>mapAuxiliaryRow(table,row));
}
async function dashboard(store,owner) {
  const names = ['projects','tasks','directives','directive_executions','trades','trade_plans'];
  const values = await Promise.all(names.map(name=>readAuxiliaryRows(store,name,owner)));
  return {ownerId:owner,projects:values[0],tasks:values[1],directives:values[2],executions:values[3],trades:values[4],tradePlans:values[5],generatedAt:new Date().toISOString()};
}
class Invalid extends Error {}
function inputString(body,key,max,required=false) {
  const value = body[key];
  if (value == null && !required) return '';
  if (typeof value !== 'string' || value.length>max || (required&&!value.trim())) throw new Invalid('入力内容を確認してください。');
  return value.trim();
}
function inputNumber(body,key,min=0,max=Number.MAX_SAFE_INTEGER,fallback=0) {
  const value=body[key] == null ? fallback : Number(body[key]);
  if(!Number.isFinite(value)||value<min||value>max) throw new Invalid('数値を確認してください。');
  return value;
}
function inputChoice(body,key,allowed) {const value=inputString(body,key,40,true);if(!allowed.includes(value)) throw new Invalid('選択内容を確認してください。');return value;}
function inputDate(body,key) {const value=inputString(body,key,10,true);if(!/^\d{4}-\d{2}-\d{2}$/.test(value)||!Number.isFinite(Date.parse(value))||new Date(value).toISOString().slice(0,10)!==value) throw new Invalid('日付を確認してください。');return value;}
async function readBody(request) {
  if(!request.headers.get('content-type')?.toLowerCase().startsWith('application/json')) throw new Invalid('JSONが必要です。');
  const reader=request.body?.getReader();if(!reader) throw new Invalid('入力がありません。');
  let size=0;const chunks=[];
  try{for(;;){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>64*1024){await reader.cancel();throw new Invalid('入力が大きすぎます。');}chunks.push(value);}}finally{reader.releaseLock();}
  const buffer=new Uint8Array(size);let offset=0;for(const chunk of chunks){buffer.set(chunk,offset);offset+=chunk.length;}
  let body;try{body=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(buffer));}catch{throw new Invalid('JSONを確認してください。');}
  if(!body||typeof body!=='object'||Array.isArray(body)) throw new Invalid('JSONを確認してください。');
  return body;
}
async function act(store,owner,body) {
  const action=inputString(body,'action',40,true),timestamp=new Date().toISOString();
  const id=()=>inputString(body,'id',120,true);
  const base=()=>({id:crypto.randomUUID(),owner_id:owner,created_at:timestamp,updated_at:timestamp});
  const update=(table,key,changes,allowed)=>store.update('command_center.'+table,key,owner,row=>{if(allowed&&!allowed.includes(row.status))throw new Conflict('状態が変更されています。');return {...row,...changes,updated_at:timestamp};});
  if(action==='create_task') await store.insert('command_center.tasks',{...base(),business_id:inputString(body,'businessId',80,true),title:inputString(body,'title',180,true),due_date:inputDate(body,'dueDate'),priority:inputNumber(body,'priority',1,5,2),reason:inputString(body,'reason',500),status:'planned',effort:'',blocker:'',category:'追加'});
  else if(action==='update_task') await update('tasks',id(),{status:inputChoice(body,'status',['today','planned','waiting','done'])});
  else if(action==='create_directive') await store.insert('command_center.directives',{...base(),id:inputString(body,'id',120)||crypto.randomUUID(),business_id:inputString(body,'businessId',80,true),mode:inputChoice(body,'mode',['research','draft','implement','hold']),instruction:inputString(body,'instruction',800,true)});
  else if(action==='record_execution') {
    const key=id(),row={id:key,directive_id:inputString(body,'directiveId',120,true),owner_id:owner,business_id:inputString(body,'businessId',80,true),mode:inputChoice(body,'mode',['research','draft','implement','hold']),instruction:inputString(body,'instruction',800,true),status:inputChoice(body,'status',['starting','running','waiting_approval','completed','failed','interrupted']),summary:inputString(body,'summary',2000),result:inputString(body,'result',50000),error:inputString(body,'error',2000),thread_id:inputString(body,'threadId',200),version:inputNumber(body,'version',1,100,1),has_changes:body.hasChanges===true,started_at:inputString(body,'startedAt',40)||timestamp,completed_at:inputString(body,'completedAt',40)||null,updated_at:timestamp};
    if(await store.get('command_center.directive_executions',key,owner)) await update('directive_executions',key,row);
    else await store.insert('command_center.directive_executions',row);
  } else if(action==='create_trade'||action==='create_trade_plan') {
    const symbol=inputString(body,'symbol',40,true).toUpperCase();if(!/^[A-Z0-9.\-]{1,40}$/.test(symbol))throw new Invalid('銘柄を確認してください。');
    const common={...base(),market:inputString(body,'market',40,true),symbol,direction:inputChoice(body,'direction',['long','short'])};
    if(action==='create_trade')await store.insert('command_center.trades',{...common,traded_at:inputDate(body,'tradedAt'),status:'open',entry_price:inputNumber(body,'entryPrice'),quantity:inputNumber(body,'quantity'),risk_amount:inputNumber(body,'riskAmount'),pnl:0,memo:inputString(body,'memo',500)});
    else await store.insert('command_center.trade_plans',{...common,name:inputString(body,'name',120),trade_style:inputChoice(body,'tradeStyle',['cash','margin']),signal_score:inputNumber(body,'signalScore',0,100),reference_price:inputNumber(body,'referencePrice'),quantity:inputNumber(body,'quantity'),stop_price:inputNumber(body,'stopPrice'),target_price:inputNumber(body,'targetPrice'),max_loss:inputNumber(body,'maxLoss'),thesis:inputString(body,'thesis',1000),invalidation:inputString(body,'invalidation',1000),source_as_of:inputString(body,'sourceAsOf',50),status:'draft',trade_id:''});
  } else if(action==='approve_trade_plan') await update('trade_plans',id(),{status:'approved'},['draft']);
  else if(action==='cancel_trade_plan') await update('trade_plans',id(),{status:'cancelled'},['draft','approved']);
  else if(action==='execute_trade_plan') await store.executeTrade({id:id(),tradedAt:inputDate(body,'tradedAt'),entryPrice:inputNumber(body,'entryPrice',Number.MIN_VALUE),quantity:inputNumber(body,'quantity',Number.MIN_VALUE),riskAmount:inputNumber(body,'riskAmount')},owner);
  else if(action==='close_trade') await update('trades',id(),{status:'closed',pnl:inputNumber(body,'pnl',-Number.MAX_SAFE_INTEGER)},['open']);
  else if(action==='delete_trade') await store.removeClosedTrade(id(),owner);
  else throw new Invalid('対応していない操作です。');
}
// Called only after the current admin session has been verified by worker.mjs.
export async function auxiliaryApi(request,env) {
  const path=new URL(request.url).pathname.replace(/\/+$/,'');if(!auxiliaryPath(path))return null;
  const allowed=path.endsWith('/sns-history')?['GET','HEAD']:['GET','HEAD','POST'];
  if(!allowed.includes(request.method))return new Response(null,{status:405,headers:{...HEADERS,allow:allowed.join(', ')}});
  if(env.AUXILIARY_BACKEND!=='d1'||!env.AUX_DB)return json({error:'共有保存先は接続待ちです。既存データは変更されていません。'},503);
  if(request.method==='POST') {
    if(request.headers.get('origin')!==new URL(request.url).origin||request.headers.get('sec-fetch-site')==='cross-site') return json({error:'管理画面からやり直してください。'},403);
    if(env.AUXILIARY_WRITES!=='enabled')return json({error:'データ移行の確認中です。入力を保持してお待ちください。'},503);
  }
  try {
    const store=auxiliaryStore(env.AUX_DB),owner=env.COMMAND_CENTER_OWNER_ID||'site-owner';
    if(typeof owner!=='string'||!owner.trim()||owner.length>120)throw Error('Invalid owner');
    if(request.method==='POST')await act(store,owner,await readBody(request));
    const result=path.endsWith('/sns-history')?{posts:await readAuxiliaryRows(store,'sns_posts','',30)}:await dashboard(store,owner);
    return request.method==='HEAD'?new Response(null,{headers:HEADERS}):json(result);
  }catch(error){return json({error:error instanceof Invalid?error.message:error instanceof Conflict?'データが変更されています。再読込して確認してください。':'保存先を確認できません。時間をおいて再試行してください。'},error instanceof Invalid?400:error instanceof Conflict?409:503);}
}
