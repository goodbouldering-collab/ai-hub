"""Restore the approved photographic series without reverting newer copy or functionality."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.art_direction import decorate_art_direction

BASELINE_SHA='f88e138f9987a64c0b488b21fd5dbbb474d6a7123d25afbc803820830294b939'
RUNTIME_SHA='721c4fce84bf2baab549b50aaba8b95555aea819d6c42a36d820bf20d0910375'
RETIRED='design-system/studio/paper-design.css'
OWNED=['design-system/studio/editorial.css','design-system/studio/images/soft-hero.webp']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(root):return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
def write(p,text):
    # Output may share hardlinks with the immutable baseline.
    if p.exists():p.unlink()
    p.write_text(text,encoding='utf-8',newline='\n')
def preserve(before,after):
    from bs4 import BeautifulSoup
    a,b=[BeautifulSoup(t,'html.parser') for t in (before,after)]
    assert list(a.stripped_strings)==list(b.stripped_strings),'Visible content changed'
    for selector in ['form','script']:
        assert [str(x) for x in a.select(selector)]==[str(x) for x in b.select(selector)],selector
    for selector,key in [('a','href'),('section','id')]:
        assert [x.get(key) for x in a.select(selector)]==[x.get(key) for x in b.select(selector)],selector
    assert [x.get('src','').split('?')[0] for x in a.select('img')]==[x.get('src','').split('?')[0] for x in b.select('img')]
    assert not b.select('link[href*="paper-design.css"],body.studio-paper')
def build(baseline,runtime_base,output):
    assert digest(baseline/'verification.json')==BASELINE_SHA
    assert digest(runtime_base/'verification.json')==RUNTIME_SHA
    old=json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    old_runtime=json.loads((runtime_base/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha']=='04cff0090c79ba359376b06e2aa217e70e0213d5'
    assets_before=hashes(baseline/'public');runtime_before=hashes(runtime_base/'runtime')
    assert assets_before==old['assets'] and runtime_before==old_runtime['runtime']
    assert digest(runtime_base/'compiled/public-entry.js')==old['worker_sha256']
    assert output.is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline/'public',output/'public',copy_function=os.link)
    shutil.copytree(runtime_base/'runtime',output/'runtime')
    changed_html=[]
    for p in (output/'public').rglob('*.html'):
        before=p.read_text(encoding='utf-8');after=decorate_art_direction(before)
        preserve(before,after)
        if before!=after:write(p,after);changed_html.append(p.relative_to(output/'public').as_posix())
    p=output/'runtime/worker/admin-assets.generated.mjs'
    raw=p.read_text(encoding='utf-8');start=raw.index('{');end=raw.rfind('}')+1
    entries=json.loads(raw[start:end]);admin_pages=0
    for entry in entries.values():
        if 'text/html' in entry['type']:
            before=entry['body'];entry['body']=decorate_art_direction(before)
            preserve(before,entry['body']);admin_pages+=1
    assert admin_pages>=2
    write(p,raw[:start]+json.dumps(entries,ensure_ascii=False,separators=(',',':'))+raw[end:])
    p=output/'runtime/worker/login-page.mjs'
    before=p.read_text(encoding='utf-8');after=decorate_art_direction(before)
    preserve(before,after);write(p,after)
    for name in OWNED:
        src=ROOT/'site/static'/name;p=output/'public'/name
        if name.endswith('.css'):write(p,src.read_text(encoding='utf-8'))
        else:
            p.unlink();shutil.copyfile(src,p)
    (output/'public'/RETIRED).unlink()
    assets=hashes(output/'public');runtime=hashes(output/'runtime')
    changed=sorted(p for p in assets if assets[p]!=assets_before.get(p))
    assert set(assets)==set(assets_before)-{RETIRED}
    assert set(changed)==set(OWNED+changed_html)
    assert set(runtime)==set(runtime_before)
    assert {p for p in runtime if runtime[p]!=runtime_before[p]}=={'worker/admin-assets.generated.mjs','worker/login-page.mjs'}
    assert hashes(baseline/'public')==assets_before and hashes(runtime_base/'runtime')==runtime_before
    sources=['scripts/build_restore_contextual_release.py','core/art_direction.py','tests/test_art_direction.py','docs/design/contextual-images-20260926.json','cloudflare-runtime/wrangler-profile-release.jsonc','cloudflare-runtime/wrangler-glass-build.jsonc','deployment/profile/package.json','deployment/profile/package-lock.json']+['site/static/'+p for p in OWNED]
    status=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_inputs={p:digest(ROOT/p) for p in sources},source_inputs_clean=not status,source_input_status=status,baseline_version='6a67263b-a6c8-4759-a7bc-b0ea174832d1',assets=assets,runtime=runtime,changed_assets=changed,removed_assets=[RETIRED],unchanged_assets=len(assets)-len(changed),baseline_unchanged=True,deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','unchanged_assets']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime-base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.baseline.resolve(),a.runtime_base.resolve(),a.output.resolve())
