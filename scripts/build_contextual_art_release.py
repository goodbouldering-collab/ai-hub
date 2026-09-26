"""Replace contextual artwork on the verified release while preserving all copy and interactions."""
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
    assert digest(baseline/'verification.json')=='8682e6a831cd068343ba1c60681894afd030ad5552eb2cac61fcab4233cfa8d7'
    assert digest(runtime_base/'verification.json')=='8682e6a831cd068343ba1c60681894afd030ad5552eb2cac61fcab4233cfa8d7'
    old=json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    runtime_old=json.loads((runtime_base/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha']=='2d1408a6390a3d79037fad9fde0389e028474c90'
    before_assets=hashes(baseline/'public');before_runtime=hashes(runtime_base/'runtime')
    assert before_assets==old['assets'] and before_runtime==runtime_old['runtime']
    assert digest(runtime_base/'compiled/public-entry.js')=='660ea63c15bd961ede1d711532b3dd90e91690e7b4bace165902259af8d94072'
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
    write(login,re.sub(r'(editorial\.css\?v=)[a-zA-Z0-9-]+',lambda m:m[1]+EDITORIAL_VERSION,login.read_text(encoding='utf-8')))
    owned=['design-system/studio/editorial.css']
    names=['soft-'+n for n in 'hero agent personal code support salon site prepare try keep login'.split()]+['lesson-'+n for n in 'agent practice rag site salon climbing coding'.split()]
    owned+=['design-system/studio/images/'+n+'.webp' for n in names]
    for name in owned:
        p=output/'public'/name
        if p.exists():p.unlink()
        shutil.copyfile(ROOT/'site/static'/name,p)
    assets=hashes(output/'public');runtime=hashes(output/'runtime')
    changed=sorted(p for p in assets if assets[p]!=before_assets.get(p))
    assert set(assets)==set(before_assets)
    assert set(changed)==set(owned+changed_html)
    assert {p for p in runtime if runtime[p]!=before_runtime[p]}=={'worker/admin-assets.generated.mjs','worker/login-page.mjs'}
    assert hashes(baseline/'public')==before_assets and hashes(runtime_base/'runtime')==before_runtime
    sources=['scripts/build_contextual_art_release.py','core/art_direction.py','docs/design/contextual-images-20260926.json','tests/test_art_direction.py','cloudflare-runtime/wrangler-profile-release.jsonc','cloudflare-runtime/wrangler-glass-build.jsonc','deployment/profile/package.json','deployment/profile/package-lock.json']+['site/static/'+p for p in owned]
    status=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_inputs={p:digest(ROOT/p) for p in sources},source_inputs_clean=not status,source_input_status=status,baseline_version='090e9c88-72dd-4752-801d-3d53558c0f34',assets=assets,runtime=runtime,changed_assets=changed,unchanged_assets=len(assets)-len(changed),baseline_unchanged=True,deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','unchanged_assets']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.baseline.resolve(),a.output.resolve())
