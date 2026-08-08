from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADMIN_CSS = ROOT / "site" / "static" / "admin" / "admin-common.css"


class AdminMobileNavigationTest(unittest.TestCase):
    def test_compact_header_keeps_all_admin_links_scrollable(self) -> None:
        source = ADMIN_CSS.read_text(encoding="utf-8")
        shared_menu_marker = "--admin-shared-quick-height: 50px;"
        marker_index = source.index(shared_menu_marker)
        media_start = source.rfind("@media (max-width: 1100px) {", 0, marker_index)
        compact_header_css = source[media_start : media_start + 3200]

        self.assertIn(
            "body.admin-page .admin-shared-header .site-nav.admin-slide-nav,\n"
            "  body.ops-page .admin-shared-header .site-nav.admin-slide-nav,\n"
            "  .admin-shared-header .site-nav.admin-slide-nav",
            compact_header_css,
        )
        self.assertIn("max-width: none !important;", compact_header_css)
        self.assertIn(
            "body.admin-page .admin-shared-header .admin-scroll-menu,\n"
            "  body.ops-page .admin-shared-header .admin-scroll-menu,\n"
            "  .admin-shared-header .admin-scroll-menu",
            compact_header_css,
        )
        self.assertIn("overflow-x: auto !important;", compact_header_css)


if __name__ == "__main__":
    unittest.main()
