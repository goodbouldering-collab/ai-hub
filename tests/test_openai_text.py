import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

from core.openai_text import generate_text, configured_api_key


class OpenAITextTests(unittest.TestCase):
    def test_shared_key_is_reused_without_rewriting_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            shared = root / ".env.shared"
            original = "OPENAI_API_KEY=test-only-shared-key\n"
            shared.write_text(original, encoding="utf-8")
            worktree = root / "work" / "isolated"
            worktree.mkdir(parents=True)
            with patch.dict("os.environ", {}, clear=True):
                self.assertEqual(configured_api_key(worktree), "test-only-shared-key")
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-only-environment"}, clear=True):
                self.assertEqual(configured_api_key(worktree), "test-only-environment")
            self.assertEqual(shared.read_text(encoding="utf-8"), original)

    def test_responses_request_and_text_after_reasoning(self):
        response = Mock(status_code=200)
        response.json.return_value = {"status": "completed", "output": [
            {"type": "reasoning", "summary": []},
            {"type": "message", "content": [{"type": "output_text", "text": "結果"}]},
        ]}
        requester = Mock(return_value=response)
        self.assertEqual(generate_text("指示", "入力", api_key="test-only", requester=requester), "結果")
        args, kwargs = requester.call_args
        self.assertEqual(args[0], "https://api.openai.com/v1/responses")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-only")
        self.assertFalse(kwargs["json"]["store"])
        self.assertEqual(kwargs["json"]["instructions"], "指示")
        self.assertFalse(kwargs["allow_redirects"])

    def test_incomplete_and_refusal_are_not_accepted(self):
        for payload in [
            {"status": "incomplete", "output": [{"type": "message", "content": [{"type": "output_text", "text": "partial"}]}]},
            {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal", "refusal": "refused"}]}]},
        ]:
            response = Mock(status_code=200)
            response.json.return_value = payload
            with self.assertRaises(ValueError):
                generate_text("指示", "入力", api_key="test-only", requester=Mock(return_value=response))

    def test_upstream_error_does_not_echo_credentials_or_payload(self):
        response = Mock(status_code=401, text="test-only credential")
        with self.assertRaisesRegex(RuntimeError, "OpenAI HTTP 401") as caught:
            generate_text("指示", "入力", api_key="test-only", requester=Mock(return_value=response))
        self.assertNotIn("test-only", str(caught.exception))

    def test_editorial_file_does_not_require_an_api_key_or_network(self):
        from tests.test_codex_update_log_updater import _load_updater
        updater = _load_updater()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.md"
            editorial = Path(directory) / "editorial.json"
            source.write_text("official fixture", encoding="utf-8")
            editorial.write_text(json.dumps({"hook": "prepared fixture"}), encoding="utf-8")
            def update_article(article, source_text, editor, **kwargs):
                self.assertEqual(editor("current", "period", "source", False), {"hook": "prepared fixture"})
                return False
            with patch.dict("os.environ", {}, clear=True), patch.object(updater, "update_article", side_effect=update_article), patch.object(updater, "generate_editorial") as generate:
                self.assertEqual(updater.main(["--source-file", str(source), "--editorial-file", str(editorial)]), 0)
                generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
