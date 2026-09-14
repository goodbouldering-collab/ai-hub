"""Reproduce a profile-only release from the verified current production snapshot."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def hashes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


def build(baseline):
    manifest = json.loads((ROOT / 'deployment/profile/baseline.json').read_text(encoding='utf-8'))
    assert hashes(baseline / 'public') == manifest['assets'], 'Unverified asset input'
    assert hashes(ROOT / 'deployment/profile/runtime') == manifest['runtime'], 'Runtime source changed'
    assert hashlib.sha256((ROOT / 'deployment/profile/published-worker.mjs').read_bytes()).hexdigest() == manifest['worker_bundle_sha256'], 'Published Worker bundle changed'
    output = ROOT / '.profile-release/public'
    if output.exists():
        assert set(hashes(output)) == set(manifest['assets']), 'Unexpected output inventory'
    shutil.copytree(baseline / 'public', output, dirs_exist_ok=True)
    spec = importlib.util.spec_from_file_location('profile_patch', ROOT / 'scripts/apply-speaker-career.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply(baseline / 'public', output)
    result = hashes(output)
    assert result.keys() == manifest['assets'].keys()
    changed = sorted(k for k in result if result[k] != manifest['assets'][k])
    assert changed == ['index.html', 'speaker.html'], changed
    verification = {'baseline_version': manifest['version'], 'changed_assets': changed,
                    'runtime_modules_unchanged': len(manifest['runtime']), 'assets': result}
    (ROOT / '.profile-release/verification.json').write_text(json.dumps(verification, indent=2) + '\n', encoding='utf-8')
    print('Verified release:', len(result), 'assets;', changed, '; runtime unchanged')


if __name__ == '__main__':
    build(Path(sys.argv[1]))
