"""Apply the paper design to the pinned production release without changing user journeys."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.art_direction import decorate_art_direction,EDITORIAL_VERSION
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(root):return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
def write(p,content):
    # Never modify the source release through a shared hardlink.
    if p.exists():p.unlink()
    p.write_text(content,encoding='utf-8',newline='\n')
def build(baseline,output):
    runtime_base=baseline
    assert digest(baseline/'verification.json')=='e048c6517c425e34fae2573b813fca34a3465ad056b38204b63b17c6b5dc4ea9'
    assert digest(runtime_base/'verification.json')=='e048c6517c425e34fae2573b813fca34a3465ad056b38204b63b17c6b5dc4ea9'
    old=json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    runtime_old=json.loads((runtime_base/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha']=='4afe4e5704db06a5fea6695eb03c7d8ca41eb666'
    before_assets=hashes(baseline/'public');before_runtime=hashes(runtime_base/'runtime')
    assert before_assets==old['assets'] and before_runtime==runtime_old['runtime']
    assert digest(runtime_base/'compiled/public-entry.js')=='151527592c77c87b248bd8360b144710a6fa281ccb6ef7e56dd8152ebc9d6628'
    assert output.resolve().is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline/'public',output/'public',copy_function=os.link)
    shutil.copytree(runtime_base/'runtime',output/'runtime')
    from bs4 import BeautifulSoup
    changed_html=[]
    for p in (output/'public').rglob('*.html'):
        before=p.read_text(encoding='utf-8');after=decorate_art_direction(before)
        a,b=[BeautifulSoup(t,'html.parser') for t in (before,after)]
        assert list(a.stripped_strings)==list(b.stripped_strings)
        assert [x.get('href') for x in a.select('a')]==[x.get('href') for x in b.select('a')]
        assert [str(x) for x in a.select('form')]==[str(x) for x in b.select('form')]
        assert [x.get('src','').split('?')[0] for x in a.select('img')]==[x.get('src','').split('?')[0] for x in b.select('img')]
        if before!=after:write(p,after);changed_html.append(p.relative_to(output/'public').as_posix())
    runtime_file=output/'runtime/worker/admin-assets.generated.mjs'
    raw=runtime_file.read_text(encoding='utf-8');start=raw.index('{');end=raw.rfind('}')+1
    entries=json.loads(raw[start:end]);html_count=0
    for route,entry in entries.items():
        if 'text/html' in entry['type']:
            before=entry['body'];entry['body']=decorate_art_direction(before);html_count+=1
            a,b=[BeautifulSoup(t,'html.parser') for t in (before,entry['body'])]
            assert list(a.stripped_strings)==list(b.stripped_strings)
            assert [str(x) for x in a.select('form')]==[str(x) for x in b.select('form')]
    assert html_count>=2
    write(runtime_file,raw[:start]+json.dumps(entries,ensure_ascii=False,separators=(',',':'))+raw[end:])
    login=output/'runtime/worker/login-page.mjs'
    write(login,decorate_art_direction(login.read_text(encoding='utf-8')))
    owned=['design-system/studio/editorial.css','design-system/studio/paper-design.css','design-system/studio/images/soft-hero.webp']
    for name in owned:
        p=output/'public'/name
        if p.exists():p.unlink()
        shutil.copyfile(ROOT/'site/static'/name,p)
    assets=hashes(output/'public');runtime=hashes(output/'runtime')
    changed=sorted(p for p in assets if assets[p]!=before_assets.get(p))
    assert set(assets)-set(before_assets)=={'design-system/studio/paper-design.css'}
    assert set(before_assets)<=set(assets)
    assert set(changed)==set(owned+changed_html)
    assert {p for p in runtime if runtime[p]!=before_runtime[p]}=={'worker/admin-assets.generated.mjs','worker/login-page.mjs'}
    assert hashes(baseline/'public')==before_assets and hashes(runtime_base/'runtime')==before_runtime
    sources=['scripts/build_paper_design_release.py','core/art_direction.py','docs/design/paper-design-20260926.json','tests/test_art_direction.py','tests/test_paper_design.py','cloudflare-runtime/wrangler-profile-release.jsonc','cloudflare-runtime/wrangler-glass-build.jsonc','deployment/profile/package.json','deployment/profile/package-lock.json']+['site/static/'+p for p in owned]
    status=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_inputs={p:digest(ROOT/p) for p in sources},source_inputs_clean=not status,source_input_status=status,baseline_version='f9797262-d1d5-4bc6-a80e-fa4c494f2fe2',assets=assets,runtime=runtime,changed_assets=changed,unchanged_assets=len(assets)-len(changed),baseline_unchanged=True,deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','unchanged_assets']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.baseline.resolve(),a.output.resolve())
