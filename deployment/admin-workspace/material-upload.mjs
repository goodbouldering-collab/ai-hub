import { json, PRIVATE_HEADERS } from './migration.mjs';
const MAX=10*1024*1024;
export async function materialApi(request,env){
 try {
  const response=await handleMaterialRequest(request,env);
  return request.method==='HEAD'?new Response(null,response):response;
 } catch {
  return json({error:'保存先に接続できません。再送する前に資料一覧を開き直して保存状況を確認してください。'},503);
 }
}
async function handleMaterialRequest(request,env){
 const url=new URL(request.url),store=env.ADMIN_DOCUMENTS;
 if(!store)return json({error:'内部資料の非公開ストレージが未接続です。管理者に接続を依頼してください。'},503);
 if(request.method==='POST'){
  if(request.headers.get('origin')!==url.origin)return json({error:'同じ管理画面からアップロードしてください。'},403);
  if(Number(request.headers.get('content-length'))>MAX+65536)return json({error:'10MB以下のファイルを選んでください。'},413);
  const reader=request.body?.getReader();if(!reader)return json({error:'ファイルを選んでください。'},400);
  let size=0;const chunks=[];
  while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>MAX+65536){await reader.cancel();return json({error:'10MB以下のファイルを選んでください。'},413);}chunks.push(value);}
  let form;try{form=await new Response(new Blob(chunks),{headers:{'content-type':request.headers.get('content-type')||''}}).formData();}catch{return json({error:'ファイルを選び直してください。'},400);}
  const file=form.get('file');
  if(!(file instanceof File)||!file.size||file.size>MAX||!/[.](pdf|txt|md|csv|docx|xlsx|pptx|png|jpe?g|webp)$/i.test(file.name))return json({error:'PDF・文書・表計算・画像を10MB以下で選んでください。'},400);
  const id=crypto.randomUUID();const name=file.name.replace(/[\r\n\x00-\x1f/\\]/g,'_').slice(0,180);
  // Pass the File itself so R2 receives a known-length body.
  await store.put('documents/'+id,file,{customMetadata:{name},httpMetadata:{contentType:'application/octet-stream'}});
  return json({id,name},201);
 }
 if(!['GET','HEAD'].includes(request.method))return json({error:'対応していない操作です。'},405);
 const id=url.searchParams.get('id');
 if(id){
  if(!/^[a-f0-9-]{36}$/.test(id))return json({error:'資料が見つかりません。'},400);
  const file=await store.get('documents/'+id);if(!file)return json({error:'資料が見つかりません。'},404);
  return new Response(request.method==='HEAD'?null:file.body,{headers:{...PRIVATE_HEADERS,'content-type':'application/octet-stream','content-disposition':"attachment; filename*=UTF-8''"+encodeURIComponent(file.customMetadata?.name||'document')}});
 }
 const result=await store.list({prefix:'documents/',limit:100,cursor:url.searchParams.get('cursor')||undefined,include:['customMetadata']});
 return json({files:result.objects.map(item=>({id:item.key.slice(10),name:item.customMetadata?.name||'資料',size:item.size})),cursor:result.truncated?result.cursor:null});
}
export const uploadPanel=`<section class="workspace-section"><form id="material-upload"><label for="material-file">内部資料をアップロード</label><p><input id="material-file" type="file" accept=".pdf,.txt,.md,.csv,.docx,.xlsx,.pptx,.png,.jpg,.jpeg,.webp" required></p><button type="submit" class="workspace-action">アップロード</button></form><p id="upload-status" role="status">10MBまで。保存した資料は管理画面からのみ取得できます。</p><ul id="uploaded-materials" class="workspace-list"></ul><button id="more-materials" class="workspace-action" hidden>さらに表示</button></section><script>
(()=>{const status=document.getElementById('upload-status'),list=document.getElementById('uploaded-materials'),more=document.getElementById('more-materials');let cursor=null;
async function load(append=false){try{const r=await fetch('/api/admin/material-files'+(append&&cursor?'?cursor='+encodeURIComponent(cursor):''));const data=await r.json();if(!r.ok)throw Error(data.error);if(!append)list.replaceChildren();for(const file of data.files){const li=document.createElement('li'),a=document.createElement('a');a.textContent=file.name;a.href='/api/admin/material-files?id='+encodeURIComponent(file.id);li.append(a);list.append(li);}cursor=data.cursor;more.hidden=!cursor;}catch(error){status.textContent=error.message;}}
more.onclick=()=>load(true);document.getElementById('material-upload').onsubmit=async event=>{event.preventDefault();const button=event.target.querySelector('button'),file=document.getElementById('material-file').files[0];if(!file||file.size>10485760){status.textContent='10MB以下のファイルを選んでください。';return;}button.disabled=true;status.textContent='アップロード中…';try{const body=new FormData();body.set('file',file);const r=await fetch('/api/admin/material-files',{method:'POST',body});const data=await r.json();if(!r.ok)throw Error(data.error);status.textContent='保存しました。';event.target.reset();await load();}catch(error){status.textContent=error.message;}finally{button.disabled=false;}};load();})();</script>`;
