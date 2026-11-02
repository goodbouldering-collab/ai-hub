"""Build a homepage-only release from a hash-verified public baseline."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.compact_cards import apply_compact_cards
from core.editorial_feed import _ElementSpans


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


def build(baseline, output, source_sha):
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    before = hashes(baseline / 'public')
    assert before == previous['assets'], 'Baseline assets changed'
    worker = baseline / 'runtime/published-worker.mjs'
    assert digest(worker) == previous['worker_sha256'], 'Worker changed'
    assert not output.exists(), 'Use a fresh release directory'
    original = (baseline / 'public/index.html').read_bytes().decode('utf-8')
    updated = apply_compact_cards(original)
    assert apply_compact_cards(updated) == updated, 'Transformation must be idempotent'
    for name in ('all-works', 'lectures', 'packages', 'blog', 'faq'):
        def section(doc):
            (a, b), = _ElementSpans(doc, element_id=name).spans
            return doc[a:b]
        expected = section(original)
        if name == 'all-works':
            for a, b in reversed(_ElementSpans(expected, 'pf-card').spans):
                if '/img/portfolio/rieru-seikotsu.jpg' in expected[a:b]:
                    expected = expected[:a] + expected[b:]
        assert expected == section(updated), name
    assert '/img/portfolio/rieru-seikotsu.jpg' not in updated
    (_, works_end), = _ElementSpans(updated, element_id='all-works').spans
    (lectures_start, _), = _ElementSpans(updated, element_id='lectures').spans
    assert works_end == lectures_start, 'Materials must immediately follow works'
    shutil.copytree(baseline / 'public', output / 'public')
    (output / 'runtime').mkdir()
    shutil.copyfile(worker, output / 'runtime/published-worker.mjs')
    (output / 'public/index.html').write_bytes(updated.encode('utf-8'))
    after = hashes(output / 'public')
    changed = [n for n in before if before[n] != after[n]]
    assert changed == ['index.html'] and before.keys() == after.keys()
    inputs = ['core/compact_cards.py', 'core/editorial_feed.py', 'site/templates/ai-news/compact-cards.css', 'scripts/build_compact_cards_release.py']
    report = dict(source_sha=source_sha, baseline_source_sha=previous['source_sha'], assets=after,
                  changed_assets=changed, unchanged_assets=len(before)-1,
                  worker_sha256=digest(worker), source_inputs_sha256={n:digest(ROOT/n) for n in inputs},
                  section_contents_unchanged_except_retired_work=True, materials_immediately_after_works=True)
    (output / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('assets','source_inputs_sha256')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
