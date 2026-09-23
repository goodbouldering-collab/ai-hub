"""Build against the verified September 22 public release, preserving news/API."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.art_direction import decorate_art_direction,EDITORIAL_VERSION
from core.compact_home import compact_home
from core.soft_studio import decorate_soft_playground

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(root):return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
def build(baseline,runtime_base,output):
    assert digest(baseline/'verification.json')=='b99de383691280c65fae7fa762121698e9ebb0524936209048521c552022c6ec'
    assert digest(runtime_base/'verification.json')=='5e51c2103b5d922da6b7dc18dbdb7bd8ed215c86d3398efe7a7c141911202262'
    old=json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha']=='6dbf2eef7b2065ac0ce358f7bcb8a32490e1829f'
    assert hashes(baseline/'public')==old['assets']
    runtime_old=json.loads((runtime_base/'verification.json').read_text(encoding='utf-8'))
    assert hashes(runtime_base/'runtime')==runtime_old['runtime']
    assert digest(baseline/'compiled/published-worker.mjs')=='baab871b7ffa55b70f49098d155bc7dfaad96cedb0fc5742334b9dbe9f305506'
    assert output.resolve().is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline/'public',output/'public');shutil.copytree(runtime_base/'runtime',output/'runtime')
    from bs4 import BeautifulSoup
    changed_html=[]
    for p in (output/'public').rglob('*.html'):
        before=p.read_text(encoding='utf-8');after=decorate_art_direction(before)
        if p==output/'public/index.html':
            after=decorate_soft_playground(compact_home(after))
            a,b=[BeautifulSoup(t,'html.parser') for t in (before,after)]
            assert [x.get('href') for x in a.select('a')]==[x.get('href') for x in b.select('a')]
            assert [str(x) for x in a.select('form,.compact-course-meta')]==[str(x) for x in b.select('form,.compact-course-meta')]
            assert b.select_one('.diagnosis-guide-row').find_next_sibling()['id']=='studio-playground'
            assert not b.select('.readiness-guide__summary,.focus-section-lead,.pf-sum')
            assert decorate_soft_playground(compact_home(after))==after
        if before!=after:p.write_text(after,encoding='utf-8',newline='\n');changed_html.append(p.relative_to(output/'public').as_posix())
    for p in (output/'runtime').rglob('*.mjs'):
        before=p.read_text(encoding='utf-8');after=re.sub(r'(editorial\.css\?v=)[a-zA-Z0-9-]+',lambda m:m[1]+EDITORIAL_VERSION,before)
        if before!=after:p.write_text(after,encoding='utf-8',newline='\n')
    names=['soft-'+n for n in 'hero agent personal code support salon site prepare try keep login'.split()]+['lesson-'+n for n in 'agent practice rag site salon climbing coding'.split()]
    owned=['design-system/studio/images/'+n+'.webp' for n in names]+['design-system/studio/editorial.css','design-system/studio/soft-playground.css']
    for name in owned:shutil.copyfile(ROOT/'site/static'/name,output/'public'/name)
    assets=hashes(output/'public');runtime=hashes(output/'runtime')
    changed=sorted(p for p in assets if assets[p]!=old['assets'][p])
    assert set(assets)==set(old['assets'])
    assert set(changed)==set(owned+changed_html)
    assert {p for p in runtime if runtime[p]!=runtime_old['runtime'][p]}=={'worker/admin-assets.generated.mjs','worker/login-page.mjs'}
    sources=['scripts/build_cyber_release.py','scripts/verify_warm_line_live.py','scripts/verify_editorial_live.py','core/art_direction.py','core/compact_home.py','core/soft_studio.py','core/studio_design.py','cloudflare-runtime/wrangler-profile-release.jsonc','cloudflare-runtime/wrangler-glass-build.jsonc','deployment/profile/package.json','deployment/profile/package-lock.json']+['site/static/'+p for p in owned]
    status=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_inputs={p:digest(ROOT/p) for p in sources},source_inputs_clean=not status,source_input_status=status,baseline_source_sha=old['source_sha'],baseline_version='ce1e01d2-3b6d-48de-828c-748fec6ca665',assets=assets,runtime=runtime,changed_assets=changed,unchanged_assets=len(assets)-len(changed),deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','unchanged_assets']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime-base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.baseline.resolve(),a.runtime_base.resolve(),a.output.resolve())
