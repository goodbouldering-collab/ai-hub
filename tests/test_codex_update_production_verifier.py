import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "scripts" / "verify_codex_update_production.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("codex_update_production_verifier", VERIFIER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, text: str, *, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code
        self.url = "https://aiclimb.vercel.app/blog/codex-update-log.html"
        self.headers = {"Content-Type": "text/html; charset=utf-8"}


class CodexUpdateProductionVerifierTest(unittest.TestCase):
    def test_reads_expected_fingerprint_and_waits_for_exact_deployment(self) -> None:
        verifier = _load_verifier()
        fingerprint = "a" * 64
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text(
                f'''---
content_series: codex-update-log
source_fingerprint: "{fingerprint}"
---

body
''',
                encoding="utf-8",
            )
            self.assertEqual(verifier.read_expected_fingerprint(article), fingerprint)

        responses = iter(
            [
                FakeResponse("<!-- source-fingerprint: old -->"),
                FakeResponse(f"<!-- source-fingerprint: {fingerprint} -->"),
            ]
        )
        sleeps: list[float] = []
        verified = verifier.wait_for_production(
            verifier.PRODUCTION_URL,
            fingerprint,
            requester=lambda *_args, **_kwargs: next(responses),
            sleeper=sleeps.append,
            attempts=3,
            interval=0.25,
        )

        self.assertEqual(verified, verifier.PRODUCTION_URL)
        self.assertEqual(sleeps, [0.25])

    def test_rejects_wrong_host_and_times_out_without_false_success(self) -> None:
        verifier = _load_verifier()
        fingerprint = "b" * 64
        with self.assertRaises(ValueError):
            verifier.wait_for_production(
                "https://example.com/blog/codex-update-log.html",
                fingerprint,
                requester=lambda *_args, **_kwargs: self.fail("must not request wrong host"),
                sleeper=lambda _seconds: None,
                attempts=1,
                interval=0,
            )

        with self.assertRaises(RuntimeError):
            verifier.wait_for_production(
                verifier.PRODUCTION_URL,
                fingerprint,
                requester=lambda *_args, **_kwargs: FakeResponse("old deployment"),
                sleeper=lambda _seconds: None,
                attempts=2,
                interval=0,
            )


if __name__ == "__main__":
    unittest.main()
