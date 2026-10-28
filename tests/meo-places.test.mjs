import test from 'node:test';
import assert from 'node:assert/strict';
import { extractLocalProfile, runPlacesSearch, PLACES_FIELD_MASK } from '../api/_lib/meo-places.mjs';
import { createDiagnosisWorker, publicDocumentFetcher } from '../deployment/meo-diagnosis/worker.mjs';
const input = { action: 'rank', storeName: '青空珈琲', area: '滋賀県彦根市', keyword: 'カフェ', placeId: 'ChIJtarget12345', confirmed: true };
const validLookup = async () => [{ address: '93.184.216.34', family: 4 }];
const request = (path, body, ip = Math.random().toString()) => new Request('https://example.com' + path, { method:'POST', headers:{'content-type':'application/json','cf-connecting-ip':ip}, body:JSON.stringify(body) });
test('extracts named local business and exposes distinct branches for confirmation', () => {
  const profile = extractLocalProfile('<script type="application/ld+json">'+JSON.stringify({'@graph':[
    {'@type':'CafeOrCoffeeShop',name:'青空珈琲',address:{addressRegion:'滋賀県',addressLocality:'彦根市'}},
    {'@type':'CafeOrCoffeeShop',name:'青空珈琲 長浜店',address:{addressRegion:'滋賀県',addressLocality:'長浜市'}}
  ]})+'</script>');
  assert.equal(profile.storeName,'青空珈琲'); assert.equal(profile.area,'滋賀県彦根市'); assert.equal(profile.keyword,'カフェ'); assert.equal(profile.alternatives.length,2);
});
test('fallback uses page content without inventing missing area or category', () => {
  const p = extractLocalProfile('',{title:'青空 | ホーム',description:'滋賀県彦根市のカフェです'});
  assert.equal(p.storeName,'青空'); assert.equal(p.area,'滋賀県彦根市'); assert.equal(p.keyword,'カフェ');
  assert.equal(extractLocalProfile('',{title:'オンライン講座'}).area,'');
});
test('free fields only, fixed Google endpoint, three-page bound, preserves API order', async () => {
  const calls = [];
  const result = await runPlacesSearch(input,{apiKey:'TEST_ONLY',fetchImpl:async (url,options) => {
    calls.push({url,options,body:JSON.parse(options.body)});
    return Response.json(calls.length === 1 ? {places:[{id:'ChIJother12345'}],nextPageToken:'page2'} : {places:[{id:input.placeId}],nextPageToken:'page3'});
  }});
  assert.equal(result.rank,2); assert.equal(result.examined,2); assert.equal(calls.length,2);
  for(const c of calls){assert.equal(c.url,'https://places.googleapis.com/v1/places:searchText');assert.equal(c.options.headers['X-Goog-FieldMask'],PLACES_FIELD_MASK);assert.equal(c.options.redirect,'error');assert.equal(c.body.textQuery,'滋賀県彦根市 カフェ');}
  assert.equal(calls[1].body.pageToken,'page2'); assert.match(result.disclaimer,/実際のMEO順位とは異なり/);
});
test('candidate search does not claim identity and returns Maps links, no paid details', async () => {
  let count=0; const result=await runPlacesSearch({...input,action:'candidates'},{apiKey:'TEST',fetchImpl:async () => {count++;return Response.json({places:[{id:input.placeId}]});}});
  assert.equal(count,1);assert.equal(result.rank,undefined);assert.equal(result.candidates[0].id,input.placeId);assert.match(result.candidates[0].mapsUrl,/query_place_id/);
});
test('missing target, zero results, provider errors and unavailable key never become rank zero', async () => {
  const empty=await runPlacesSearch(input,{apiKey:'TEST',fetchImpl:async()=>Response.json({})});assert.equal(empty.rank,null);assert.equal(empty.examined,0);
  let count=0;const limit=await runPlacesSearch(input,{apiKey:'TEST',fetchImpl:async()=>{count++;return Response.json({places:[{id:'ChIJother12345'}],nextPageToken:'p'+count});}});assert.equal(count,3);assert.equal(limit.rank,null);assert.equal(limit.hasMore,true);
  await assert.rejects(runPlacesSearch(input,{}),e=>e.code==='places_not_configured');
  for(const status of [403,429,500]) await assert.rejects(runPlacesSearch(input,{apiKey:'SECRET_TEST',fetchImpl:async()=>new Response('SECRET_TEST',{status})}),e=>!e.message.includes('SECRET_TEST')&&e.status>=429);
});
test('rejects invalid rank requests before calling Google', async () => {
  for(const invalid of [{area:''},{confirmed:false},{placeId:'x'},{keyword:'青空珈琲'}]) await assert.rejects(runPlacesSearch({...input,...invalid},{apiKey:'TEST',fetchImpl:()=>{throw new Error('must not call');}}),e=>e.status===400);
});
test('public fetch rejects private DNS and redirect before requesting that destination', async () => {
  let calls=0; const fetcher=publicDocumentFetcher(async()=>{calls++;return new Response(null,{status:302,headers:{location:'http://127.0.0.1/private'}});},validLookup);
  await assert.rejects(fetcher('https://example.com',{}));assert.equal(calls,1);
  const privateDns=publicDocumentFetcher(()=>{throw Error('must not fetch');},async()=>[{address:'10.0.0.1',family:4}]);await assert.rejects(privateDns('https://example.com',{}));
});
test('public fetch caps body length, decodes EUC-JP and strips caller credentials', async () => {
  const {default:iconv}=await import('iconv-lite');let seen;
  const f=publicDocumentFetcher(async(_url,options)=>{seen=options;return new Response(iconv.encode('彦根市','euc-jp'),{headers:{'content-type':'text/html;charset=euc-jp'}});},validLookup);
  assert.equal((await f('https://example.com')).body,'彦根市');assert.deepEqual(Object.keys(seen.headers).sort(),['accept','user-agent']);
  await assert.rejects(f('https://example.com',{maxBytes:2}));
});
test('Worker restores audit, extracts profile, reports disconnected Places, protects methods and origin', async () => {
  const worker=createDiagnosisWorker({lookup:validLookup,fetchImpl:async()=>new Response('<title>青空珈琲</title><h1>青空珈琲</h1><p>滋賀県彦根市のカフェ</p>',{headers:{'content-type':'text/html'}}),previous:{fetch:()=>new Response('unchanged')}});
  const result=await worker.fetch(request('/api/seo-llmo-audit',{url:'https://example.com'}),{});
  assert.equal(result.status,200);const payload=await result.json();assert.equal(payload.report.localProfile.storeName,'青空珈琲');assert.equal(payload.report.localProfile.keyword,'カフェ');assert.ok(Number.isFinite(payload.report.score));
  const off=await worker.fetch(request('/api/meo-places',input),{});assert.equal(off.status,503);assert.match(off.headers.get('cache-control'),/no-store/);
  assert.deepEqual(await (await worker.fetch(new Request('https://example.com/api/meo-places'),{})).json(),{configured:false,billingMode:'ids-only'});
  assert.equal((await worker.fetch(new Request('https://example.com/api/seo-llmo-audit'),{})).status,405);
  assert.equal((await worker.fetch(new Request('https://example.com/api/meo-places',{method:'POST',headers:{origin:'https://evil.example'},body:'{}'}),{})).status,403);
  assert.equal(await (await worker.fetch(new Request('https://example.com/admin'),{})).text(),'unchanged');
});
test('Worker rejects oversized streams and rate limits without allowing unlimited key abuse', async () => {
  const worker=createDiagnosisWorker();
  assert.equal((await worker.fetch(request('/api/meo-places',{x:'x'.repeat(17000)}),{})).status,413);
  for(let i=0;i<20;i++) await worker.fetch(request('/api/meo-places',{},'limit-test'),{});
  const limited=await worker.fetch(request('/api/meo-places',{},'limit-test'),{});assert.equal(limited.status,429);
});
