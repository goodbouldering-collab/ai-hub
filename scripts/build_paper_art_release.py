"""Build a bounded design release from the verified production assets."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.paper_art import apply_paper_art
from core.hero_copy import apply_hero_copy
from core.diagnosis_copy import apply_diagnosis_copy

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def build(baseline, output, sha):
    contract=json.loads((ROOT/'deployment/paper-art/baseline.json').read_text(encoding='utf8'))
    assert hashes(baseline)==contract['assets'], 'Production baseline changed'
    assert not output.exists(), 'Use a fresh release directory'
    shutil.copytree(baseline,output/'public')
    for name in ('index.html','blog/index.html'):
        before=(baseline/name).read_text(encoding='utf8')
        after=apply_paper_art(before)
        if name=='index.html': after=apply_diagnosis_copy(apply_hero_copy(after))
        assert apply_paper_art(after)==after
        (output/'public'/name).write_text(after,encoding='utf8',newline='\n')
    art=Path('design-system/studio/images/paper-20261014')
    shutil.copytree(ROOT/'site/static'/art,output/'public'/art)
    assets=hashes(output/'public')
    changed=sorted(k for k in contract['assets'] if assets[k]!=contract['assets'][k])
    assert changed==['blog/index.html','index.html']
    added=sorted(set(assets)-set(contract['assets']))
    assert len(added)==8 and all(k.startswith(str(art).replace('\\','/')) for k in added)
    worker=(ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(worker).hexdigest()==contract['worker_sha256']
    result=dict(source_sha=sha,assets=assets,changed_assets=changed,added_assets=added,
                unchanged_assets=len(contract['assets'])-2,worker_sha256=contract['worker_sha256'])
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='assets'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--source-sha')
    a=p.parse_args();build(a.baseline,a.output,a.source_sha)
