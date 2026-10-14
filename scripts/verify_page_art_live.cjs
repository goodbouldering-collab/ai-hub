const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
async function main(){
  const manifest=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
  const art=JSON.parse(fs.readFileSync(path.join(root,'config/page-art.json'),'utf8'));
  const names=[...new Set(['index.html','blog/index.html','ai-news/index.html',...manifest.changed_assets,...manifest.added_assets,...art.home_protected.map(p=>p.slice(1))])];
  let cursor=0;const results=[];
  await Promise.all(Array.from({length:6},async()=>{
    while(cursor<names.length){
      const name=names[cursor++],url='https://aiclimb.aiclimb.workers.dev/'+(name==='index.html'?'':name);
      const response=await fetch(url,{signal:AbortSignal.timeout(25000)});
      const bytes=Buffer.from(await response.arrayBuffer());
      const sha=crypto.createHash('sha256').update(bytes).digest('hex');
      results.push({path:name,status:response.status,sha256:sha,match:response.status===200&&sha===manifest.assets[name]});
    }
  }));
  for(const [route,status] of [['health',200],['admin',303],['api/admin/ping',401]]){
    const response=await fetch('https://aiclimb.aiclimb.workers.dev/'+route,{redirect:'manual',signal:AbortSignal.timeout(20000)});
    results.push({path:route,status:response.status,match:response.status===status});
  }
  results.sort((a,b)=>a.path.localeCompare(b.path));
  fs.writeFileSync(process.argv[3],JSON.stringify({source_sha:manifest.source_sha,checked_at:new Date().toISOString(),results},null,2)+'\n');
  const failed=results.filter(r=>!r.match);
  console.log(JSON.stringify({checked:results.length,failed},null,2));
  if(failed.length)process.exitCode=1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
