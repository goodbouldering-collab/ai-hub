import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "site" / "dist"
CURRENT_ORIGIN = "https://aiclimb.aiclimb.workers.dev"
DYNAMIC_ORIGIN = "https://aiclimb.vercel.app"
RETIRED_ORIGIN = "https://" + "ai" + "-hub-jp" + ".vercel.app"
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".txt", ".webmanifest", ".xml"}


class ProductionDomainBuildTests(unittest.TestCase):
    def test_default_build_uses_workers_as_the_public_origin(self):
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
            errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        rendered = "\n".join(
            path.read_text(encoding="utf-8")
            for path in DIST.rglob("*")
            if path.is_file() and path.suffix in TEXT_SUFFIXES
        )
        self.assertIn(CURRENT_ORIGIN, rendered)
        self.assertNotIn(RETIRED_ORIGIN, rendered)

        homepage = (DIST / "index.html").read_text(encoding="utf-8")
        sitemap = (DIST / "sitemap.xml").read_text(encoding="utf-8")
        programming_map = (DIST / "programming-map.html").read_text(encoding="utf-8")
        speed_monitor = (DIST / "speed-monitor.html").read_text(encoding="utf-8")

        self.assertIn(f"rel='canonical' href='{CURRENT_ORIGIN}/'", homepage)
        self.assertIn(f"<loc>{CURRENT_ORIGIN}/index.html</loc>", sitemap)
        self.assertNotIn(f"<loc>{DYNAMIC_ORIGIN}/", sitemap)
        self.assertIn(
            f'<link rel="canonical" href="{CURRENT_ORIGIN}/programming-map.html">',
            programming_map,
        )
        self.assertIn(
            f'<link rel="canonical" href="{CURRENT_ORIGIN}/speed-monitor.html">',
            speed_monitor,
        )
        self.assertNotIn(f"href='{DYNAMIC_ORIGIN}'", homepage)


if __name__ == "__main__":
    unittest.main()
