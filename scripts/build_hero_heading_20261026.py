"""Replace only the two approved heading strings in a verified release."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.hero_copy import TITLE, SUBTITLE

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

baseline, output = [Path(p).resolve() for p in sys.argv[1:3]]
if sys.platform == 'win32':
    baseline, output = [Path('\\\\?\\' + str(p)) for p in (baseline, output)]
manifest = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
assert hashes(baseline / 'public') == manifest['assets']
assert not output.exists()
shutil.copytree(baseline / 'public', output / 'public')
page = output / 'public/index.html'
before = page.read_bytes().decode('utf-8')
after = before
for old, new in [('彦根で使えるAIを学ぶ', TITLE), ('AIエージェント動いてますか？', SUBTITLE)]:
    assert after.count(old) == 1, old
    after = after.replace(old, new)
    assert after.count(new) == 1, new
assert after.replace(TITLE, '彦根で使えるAIを学ぶ').replace(SUBTITLE, 'AIエージェント動いてますか？') == before
page.write_bytes(after.encode('utf-8'))
assets = hashes(output / 'public')
assert assets.keys() == manifest['assets'].keys()
assert [p for p in assets if assets[p] != manifest['assets'][p]] == ['index.html']
result = {'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'assets': assets, 'changed': ['index.html'], 'validation': 'Only two exact strings changed'}
(output / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k != 'assets'}))
