import importlib.util
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"
SITE_PATH = ROOT / "site" / "build_site.py"

PUBLIC_LINKS = [
    ("/", "ホーム"),
    ("/#all-works", "実績"),
    ("/blog/index.html", "ブログ"),
    ("/#lectures", "資料"),
    ("/#faq", "FAQ"),
    ("/#seven-day-courses", "AIオンラインサロン"),
]
ADMIN_LINK = ("/admin", "管理ページ")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


portal = load_module("portal_navigation_under_test", PORTAL_PATH)
site_builder = load_module("site_navigation_under_test", SITE_PATH)


def links_in(fragment: str) -> list[tuple[str, str]]:
    links = re.findall(r"<a\b[^>]*href='([^']+)'[^>]*>(.*?)</a>", fragment, re.DOTALL)
    return [
        (href, re.sub(r"<[^>]+>", "", label).replace("›", "").strip())
        for href, label in links
    ]


def section(html: str, class_name: str) -> str:
    match = re.search(
        rf"<nav class='{re.escape(class_name)}'[^>]*>(?P<body>.*?)</nav>",
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group("body")


def admin_link(html: str) -> tuple[str, str]:
    match = re.search(
        r"<a\b[^>]*class='[^']*\b(?:nav-admin|mobile-admin-link)\b[^']*'"
        r"[^>]*href='([^']+)'[^>]*>(.*?)</a>",
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group(1), re.sub(r"<[^>]+>", "", match.group(2)).strip()


class PublicNavigationParityTest(unittest.TestCase):
    def assert_header_has_one_menu_contract(self, header: str) -> None:
        self.assertEqual(PUBLIC_LINKS + [ADMIN_LINK], links_in(section(header, "site-nav")))
        self.assertEqual(PUBLIC_LINKS, links_in(section(header, "mobile-public-links")))
        self.assertEqual(ADMIN_LINK, admin_link(header))
        self.assertNotIn("AIエージェント講習</a>", section(header, "site-nav"))
        self.assertNotIn("個別相談</a>", section(header, "site-nav"))
        self.assertNotIn("mobile-nav-head", header)

    def test_home_and_generated_headers_use_the_same_menu_contract(self) -> None:
        self.assert_header_has_one_menu_contract(portal._render_header_focused())
        self.assert_header_has_one_menu_contract(
            site_builder.render_top_nav(path_prefix="../", current_id="blog", include_run=False)
        )


if __name__ == "__main__":
    unittest.main()
