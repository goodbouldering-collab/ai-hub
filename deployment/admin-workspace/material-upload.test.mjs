import test from 'node:test';
import assert from 'node:assert/strict';
import { materialApi } from './material-upload.mjs';
import worker from './worker.mjs';
test('upload, list and download require the existing admin session',async()=>{
 for(const method of ['GET','POST','HEAD']){
  const response=await worker.fetch(new Request('https://admin.test/api/admin/material-files',{method}),{ADMIN_PASS:'local-test-only',ADMIN_SESSION_SECRET:'local-test-only'},{waitUntil(){}});
  assert.equal(response.status,401);
 }
});
test('private uploads require same-origin, bounded files and configured storage',async()=>{
 const request=(body,origin='https://admin.test')=>new Request('https://admin.test/api/admin/material-files',{method:'POST',headers:{origin},body});
 const form=new FormData();form.set('file',new File(['private note'],'メモ.txt'));
 assert.equal((await materialApi(request(form),{})).status,503);
 const entries=new Map();const bucket={put:async(k,body,options)=>entries.set(k,{body,...options}),list:async()=>({objects:[],truncated:false})};
 assert.equal((await materialApi(request(form,'https://evil.test'),{ADMIN_DOCUMENTS:bucket})).status,403);
 const saved=await materialApi(request(form),{ADMIN_DOCUMENTS:bucket});assert.equal(saved.status,201);assert.equal(entries.size,1);
 assert.match(saved.headers.get('cache-control'),/no-store/);
 const bad=new FormData();bad.set('file',new File(['<script>'],'x.html'));
 assert.equal((await materialApi(request(bad),{ADMIN_DOCUMENTS:bucket})).status,400);
 assert.equal((await materialApi(new Request('https://admin.test/api/admin/material-files?id=../secret'),{ADMIN_DOCUMENTS:bucket})).status,400);
});
test('storage failures are actionable and downloads remain attachments, including HEAD',async()=>{
 const url='https://admin.test/api/admin/material-files';
 const broken={list:async()=>{throw Error('private backend detail');}};
 const failure=await materialApi(new Request(url),{ADMIN_DOCUMENTS:broken});
 assert.equal(failure.status,503);assert.doesNotMatch(await failure.text(),/private backend/);
 const bucket={get:async()=>({body:'private text',customMetadata:{name:'内部資料.txt'}})};
 const id='12345678-1234-1234-1234-123456789abc';
 const download=await materialApi(new Request(url+'?id='+id),{ADMIN_DOCUMENTS:bucket});
 assert.equal(await download.text(),'private text');assert.match(download.headers.get('content-disposition'),/^attachment/);
 assert.equal(download.headers.get('content-type'),'application/octet-stream');
 const head=await materialApi(new Request(url+'?id='+id,{method:'HEAD'}),{ADMIN_DOCUMENTS:bucket});assert.equal(await head.text(),'');
});
