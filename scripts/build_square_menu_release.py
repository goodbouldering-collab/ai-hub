"""Build a menu-only release against a hash-verified production baseline."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.square_menu import apply_square_menu

INPUTS = ['core/square_menu.py', 'scripts/build_square_menu_release.py',
          'deployment/square-menu/baseline.json', 'deployment/admin-workspace/published-worker.mjs',
          'cloudflare-runtime/wrangler-profile-release.jsonc']

def digest(data):
    return hashlib.sha256(data).hexdigest()

def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}

def build(baseline, output, sha):
    contract = json.loads((ROOT/'deployment/square-menu/baseline.json').read_text(encoding='utf-8'))
    assert hashes(baseline) == contract['assets'], 'Baseline changed'
    assert not output.exists(), 'Use a new output directory'
    worker = (ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n', b'\n')
    assert digest(worker) == contract['worker_sha256']
    if sha:
        for name in INPUTS:
            committed = subprocess.check_output(['git', 'show', f'{sha}:{name}'], cwd=ROOT)
            assert (ROOT/name).read_bytes().replace(b'\r\n', b'\n') == committed.replace(b'\r\n', b'\n'), name
    def copy(src, dst):
        if Path(src) == baseline/'index.html':
            return shutil.copyfile(src, dst)
        os.link(src, dst)
        return dst
    shutil.copytree(baseline, output/'public', copy_function=copy)
    before = (baseline/'index.html').read_bytes().decode('utf-8')
    after = apply_square_menu(before)
    assert apply_square_menu(after) == after
    assert '60分・5,500円' not in after
    assert 'AI個別相談120分｜AI時代のなんでも相談' in after
    assert '初回相談30分・無料。その後の伴走支援' in after
    assert "bookingMeta: '20分・無料'" in after
    (output/'public/index.html').write_bytes(after.encode('utf-8'))
    assets = hashes(output/'public')
    assert [p for p in assets if assets[p] != contract['assets'][p]] == ['index.html']
    (output/'runtime').mkdir()
    (output/'runtime/published-worker.mjs').write_bytes(worker)
    result = dict(source_sha=sha, assets=assets, changed_assets=['index.html'], unchanged_assets=len(assets)-1,
                  worker_sha256=digest(worker), inputs=INPUTS, source_inputs_clean=bool(sha))
    (output/'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'assets'}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-sha')
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
