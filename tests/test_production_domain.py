import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "site" / "dist"
CURRENT_ORIGIN = "https://aiclimb.vercel.app"
RETIRED_ORIGIN = "https://" + "ai" + "-hub-jp" + ".vercel.app"
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".txt", ".webmanifest", ".xml"}


class ProductionDomainBuildTests(unittest.TestCase):
    def test_default_build_emits_only_the_current_production_origin(self):
        env = os.environ.copy()
        env.pop("AIHUB_SITE_URL", None)
        env.pop("AIWATCH_SITE_URL", None)
        result = subprocess.run(
            [sys.executable, "site/build_site.py"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        rendered = "\n".join(
            path.read_text(encoding="utf-8")
            for path in DIST.rglob("*")
            if path.is_file() and path.suffix in TEXT_SUFFIXES
        )
        self.assertIn(CURRENT_ORIGIN, rendered)
        self.assertNotIn(RETIRED_ORIGIN, rendered)


if __name__ == "__main__":
    unittest.main()
