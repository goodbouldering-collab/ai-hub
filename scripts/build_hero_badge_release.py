"""Apply only the seven approved homepage text changes to a pinned release."""
from pathlib import Path
import argparse, hashlib, json, os, re, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.hero_copy import SUBTITLE, TAGLINE

from bs4 import BeautifulSoup

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def transform(html):
    from core.hero_copy import apply_hero_copy
    return apply_hero_copy(html)


def build(baseline,output,sha):
    contract=json.loads((ROOT/'deployment/hero-badge/baseline.json').read_text(encoding='utf8'))
    assert hashes(baseline)==contract['assets'],'Baseline mismatch'
    assert not output.exists(),'Use fresh output'
    before=(baseline/'index.html').read_text(encoding='utf8');after=transform(before)
    assert transform(after)==after
    old,new=[BeautifulSoup(x,'html.parser') for x in (before,after)]
    for selector in ['img','script','#blog','#packages']:
        assert [str(e) for e in old.select(selector)]==[str(e) for e in new.select(selector)],selector
    assert [e.get('href') for e in old.select('a')]==[e.get('href') for e in new.select('a')]
    for name in contract['assets']:
        dest=output/'public'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if name=='index.html':dest.write_text(after,encoding='utf8',newline='\n')
        else:os.link(baseline/name,dest)
    assets=hashes(output/'public');changed=sorted(k for k in assets if assets[k]!=contract['assets'][k])
    assert changed==['index.html']
    worker=(ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n',b'\n')
    digest=hashlib.sha256(worker).hexdigest();assert digest==contract['worker_sha256']
    result=dict(source_sha=sha,assets=assets,changed_assets=changed,unchanged_assets=len(assets)-1,worker_sha256=digest)
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='assets'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-sha',required=True);a=p.parse_args();build(a.baseline,a.output,a.source_sha)

