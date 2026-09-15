"""Apply the committed glass theme to the registered, verified profile release."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.studio_design import decorate_public_tree, decorate_runtime


def hashes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


def build():
    baseline = ROOT / '.profile-release/public'
    expected = json.loads((ROOT / 'deployment/profile/glass-baseline.json').read_text(encoding='utf-8'))
    runtime_manifest = json.loads((ROOT / 'deployment/profile/baseline.json').read_text(encoding='utf-8'))
    runtime = ROOT / 'deployment/profile/runtime'
    assert hashes(baseline) == expected['assets'], 'Current profile baseline changed'
    assert hashes(runtime) == runtime_manifest['runtime'], 'Current runtime changed'
    output = ROOT / '.glass-release'
    assert not output.exists(), 'Use a fresh release destination'
    shutil.copytree(baseline, output / 'public')
    shutil.copytree(runtime, output / 'runtime')
    decorate_public_tree(output / 'public')
    decorate_runtime(output / 'runtime')
    result = {'source_sha': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
              'assets': hashes(output / 'public'), 'runtime': hashes(output / 'runtime'),
              'deployed': False}
    (output / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'source_sha': result['source_sha'], 'assets': len(result['assets'])}))


if __name__ == '__main__':
    build()
