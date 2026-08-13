from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_SOURCE = ROOT / "site" / "build_portal.py"
SITE_SOURCE = ROOT / "site" / "build_site.py"
DIST = ROOT / "site" / "dist"


class PublicSlideMenuTest(unittest.TestCase):
    def test_homepage_source_uses_side_slide_contract(self) -> None:
        source = PORTAL_SOURCE.read_text(encoding="utf-8")

        self.assertIn("width: min(88vw, 380px) !important;", source)
        self.assertIn("transform: translateX(100%);", source)
        self.assertIn(
            ".mobile-nav.open .mobile-nav-panel--public {\n"
            "    transform: translateX(0);",
            source,
        )
        self.assertIn("aria-hidden='true'", source)
        self.assertIn("mobileNav.setAttribute('aria-hidden'", source)
        self.assertIn("if (e.target === mobileNav) setMobileMenu(false);", source)
        self.assertIn("@media (min-width: 901px)", source)
        self.assertIn("desktopMenuQuery.addEventListener('change'", source)
        self.assertIn("focusTarget.focus({ preventScroll: true });", source)
        self.assertIn("e.key !== 'Tab'", source)

    def test_generated_page_source_uses_side_slide_contract(self) -> None:
        source = SITE_SOURCE.read_text(encoding="utf-8")

        self.assertIn("width: min(88vw, 380px) !important;", source)
        self.assertIn("transform: translateX(100%);", source)
        self.assertIn(
            ".generated-mobile-nav.open .mobile-nav-panel--public {\n"
            "    transform: translateX(0);",
            source,
        )
        self.assertIn("id='mobile-nav' aria-hidden='true'", source)
        self.assertIn("n.setAttribute('aria-hidden'", source)
        self.assertIn("if(e.target===n)closeMobile();", source)
        self.assertIn("render_desktop_navigation", source)
        self.assertIn("render_mobile_navigation", source)
        self.assertNotIn("mobile-nav-head", source)
        self.assertIn("@media (min-width: 901px)", source)
        self.assertIn("closeMobileAtDesktop", source)
        self.assertIn("focus({preventScroll:true})", source)
        self.assertIn("e.key!=='Tab'", source)

    def test_representative_public_pages_are_rendered_with_slide_menu(self) -> None:
        pages = (
            DIST / "index.html",
            DIST / "lectures" / "2026-04-ai-kihon.html",
            DIST / "blog" / "index.html",
            DIST / "programming-map.html",
        )

        for page in pages:
            with self.subTest(page=page.relative_to(ROOT)):
                html = page.read_text(encoding="utf-8")
                self.assertIn("mobile-nav-panel--public", html)
                self.assertIn("transform: translateX(100%);", html)
                self.assertIn("transform: translateX(0);", html)
                self.assertIn("aria-hidden='true'", html)
                self.assertIn("<span>AIオンラインサロン</span>", html)


if __name__ == "__main__":
    unittest.main()
