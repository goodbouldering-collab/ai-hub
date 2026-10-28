// Local UI fixture only: never deploy this server or its fake API results.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createDiagnosisWorker } from '../deployment/meo-diagnosis/worker.mjs';
const root=path.resolve(process.argv[2]);
const target='ChIJtestTarget123';
const worker=createDiagnosisWorker({
  lookup:async()=>[{address:'93.184.216.34',family:4}],
  fetchImpl:async(url,options)=>{
    if(url==='https://places.googleapis.com/v1/places:searchText'){
      const body=JSON.parse(options.body);
      const ids=body.textQuery.includes('青空珈琲')?[target,'ChIJtestOther123']:['ChIJtestOther123','ChIJtestThird123',target];
      return Response.json({places:ids.map(id=>({id}))});
    }
    return new Response('<title>青空珈琲</title><h1>青空珈琲</h1><p>滋賀県彦根市のカフェです</p>',{headers:{'content-type':'text/html'}});
  },
  previous:{fetch:async request=>{
    const pathname=decodeURIComponent(new URL(request.url).pathname);const file=path.resolve(root,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
    if(!file.startsWith(root+path.sep))return new Response('',{status:404});
    try{let data=await fs.readFile(file);if(file.endsWith('.html'))data=Buffer.from(data.toString().replace('<body','<body data-test-fixture="true"').replace('</body>','<p style="position:fixed;top:0;right:0;z-index:99999;background:#fff;color:#000">テスト用・実際の順位ではありません</p></body>'));return new Response(data,{headers:{'content-type':file.endsWith('.mjs')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.html')?'text/html':'application/octet-stream'}});}catch{return new Response('',{status:404});}
  }}
});
http.createServer(async(req,res)=>{try{const parts=[];for await(const part of req)parts.push(part);const response=await worker.fetch(new Request('http://127.0.0.1:4458'+req.url,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:Buffer.concat(parts)}:{})}),{GOOGLE_PLACES_API_KEY:'TEST_ONLY_NOT_A_REAL_KEY'});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));}catch{res.writeHead(500);res.end('fixture_error');}}).listen(4458,'127.0.0.1',()=>console.log('TEST ONLY http://127.0.0.1:4458'));
