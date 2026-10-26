"""Rename only the approved course name in a verified release."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD = 'AI音声メモアプリ講座'
NEW = 'AI音声メモ講座'
course = json.loads((ROOT / 'config/voice-memo-course.json').read_text(encoding='utf-8'))
assert course['name'] == NEW + '｜録音を仕事の記録に変える'
assert course['square_name'] == '【' + NEW + '120分】録音を仕事の記録に変える'

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
assert before.count(OLD) == 4
assert NEW not in before
after = before.replace(OLD, NEW)
assert after.count(NEW) == 4 and OLD not in after
assert after.replace(NEW, OLD) == before
page.write_bytes(after.encode('utf-8'))
assets = hashes(output / 'public')
assert assets.keys() == manifest['assets'].keys()
assert [p for p in assets if assets[p] != manifest['assets'][p]] == ['index.html']
result = {'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'assets': assets, 'changed': ['index.html'], 'occurrences': 4,
          'validation': 'Only the approved course name changed; all links and other assets preserved'}
(output / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k != 'assets'}))
