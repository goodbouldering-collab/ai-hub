"""Add verified social links to a hash-verified release without rebuilding other pages."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.official_social import render_official_social

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

baseline, output = map(Path, sys.argv[1:3])
manifest = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
before = hashes(baseline / 'public')
assert before == manifest['assets'], 'Baseline changed'
assert not output.exists(), 'Use a fresh release folder'
shutil.copytree(baseline / 'public', output / 'public')
index = output / 'public/index.html'
source = index.read_text(encoding='utf-8')
marker = "<a class='footer-cta' href='#contact'>AIアプリサイト自作を相談する</a>"
assert source.count(marker) == 1
assert 'id=\'official-social\'' not in source
source = source.replace(marker, marker + render_official_social(), 1)
index.write_text(source, encoding='utf-8', newline='')
after = hashes(output / 'public')
assert [k for k in before if before[k] != after[k]] == ['index.html']
assert before.keys() == after.keys()
result = {'source_sha': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(), 'assets':after, 'changed':['index.html'], 'baseline_source_sha':manifest['source_sha']}
(output / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'changed':result['changed'],'assets':len(after),'source_sha':result['source_sha']}))
