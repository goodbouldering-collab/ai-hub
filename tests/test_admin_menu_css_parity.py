import unittest
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ADMIN_CSS = (ROOT / "site/static/admin/admin-common.css").read_text(encoding="utf-8")
TOKENS_CSS = (ROOT / "site/static/design-system/tokens.css").read_text(encoding="utf-8")
STUDIO_CSS = (ROOT / "site/static/admin/apps/styles.css").read_text(encoding="utf-8")
STUDIO_CONTENT_CSS = (ROOT / "site/static/admin/apps/styles-content.css").read_text(encoding="utf-8")
COMMAND_CENTER_CSS = (ROOT / "site/static/admin/command-center.css").read_text(encoding="utf-8")

MENU_HTML = """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body.legacy-header-transition header.site-header {
      transition: background .3s, box-shadow .3s, backdrop-filter .3s;
    }
  </style>
  __STYLESHEETS__
</head>
<body>
  <header class="site-header admin-shared-header" id="site-header">
    <div class="site-header-inner">
      <a class="site-logo admin-shared-brand" href="/admin">
        <span class="admin-shared-brand-name">AIclimb</span>
        <span class="admin-shared-brand-context">管理画面</span>
      </a>
      <div class="admin-page-context"><strong>管理ホーム</strong></div>
      <nav class="site-nav admin-slide-nav" aria-label="管理ページ固定メニュー">
        <div class="admin-scroll-menu">
          <details class="admin-menu-desktop-group is-current-group" data-menu-group="content" open>
            <summary class="admin-menu-group-trigger">
              制作・発信
              <span class="admin-menu-group-chevron" aria-hidden="true">⌄</span>
            </summary>
            <div class="admin-menu-popover" data-menu-layout="single">
              <div class="admin-menu-popover-heading"><strong>制作・発信</strong><small>ブログとSNS制作</small></div>
              <div class="admin-menu-popover-sections">
                <div class="admin-menu-popover-links">
                  <a class="admin-menu-popover-link is-current" href="/admin/blog">
                    <span class="admin-menu-link-copy"><strong>ブログ管理</strong><small>記事の確認と公開</small></span>
                    <span class="admin-menu-link-arrow" aria-hidden="true">→</span>
                  </a>
                </div>
              </div>
            </div>
          </details>
        </div>
      </nav>
      <button class="mobile-toggle" type="button" aria-label="管理メニューを開く">
        <span class="mobile-toggle-icon" aria-hidden="true"><span></span><span></span><span></span></span>
        <span class="mobile-toggle-text">メニュー</span>
      </button>
    </div>
    <div class="mobile-nav" id="mobile-nav" hidden>
      <div class="mobile-nav-panel mobile-nav-panel--admin">
        <details class="admin-menu-mobile-group is-current-group" open>
          <summary class="admin-menu-mobile-summary">
            <span class="admin-menu-mobile-copy"><strong>制作・発信</strong><small>ブログとSNS制作</small></span>
            <span class="admin-menu-mobile-count">1件</span>
          </summary>
          <div class="admin-menu-mobile-content">
            <div class="mobile-link-list">
              <a class="admin-shared-mobile-link is-current" href="/admin/blog">
                <span class="mobile-link-title">ブログ管理</span>
                <small>記事の確認と公開</small>
              </a>
            </div>
          </div>
        </details>
      </div>
    </div>
  </header>
</body>
</html>"""


def _serve_admin_fixture(route, body_class):
    url = route.request.url
    if url.endswith("/admin/admin-common.css"):
        route.fulfill(status=200, content_type="text/css", body=ADMIN_CSS)
        return
    if url.endswith("/design-system/tokens.css"):
        route.fulfill(status=200, content_type="text/css", body=TOKENS_CSS)
        return
    if url.endswith("/admin/apps/styles.css"):
        route.fulfill(status=200, content_type="text/css", body=STUDIO_CSS)
        return
    if url.endswith("/admin/apps/styles-content.css"):
        route.fulfill(status=200, content_type="text/css", body=STUDIO_CONTENT_CSS)
        return
    if url.endswith("/admin/command-center.css"):
        route.fulfill(status=200, content_type="text/css", body=COMMAND_CENTER_CSS)
        return

    if "admin-studio-page" in body_class:
        stylesheets = """
          <link rel="stylesheet" href="/admin/apps/styles.css">
          <link rel="stylesheet" href="/admin/apps/styles-content.css">
          <link rel="stylesheet" href="/admin/admin-common.css">
        """
    elif "command-center-page" in body_class:
        stylesheets = """
          <link rel="stylesheet" href="/admin/admin-common.css">
          <link rel="stylesheet" href="/admin/command-center.css">
        """
    else:
        stylesheets = '<link rel="stylesheet" href="/admin/admin-common.css">'

    route.fulfill(
        status=200,
        content_type="text/html; charset=utf-8",
        body=(
            MENU_HTML.replace("__STYLESHEETS__", stylesheets)
            .replace("<body>", f'<body class="{body_class}">')
        ),
    )


def _menu_fingerprint(page):
    return page.evaluate(
        """() => {
          const read = (selector, properties) => {
            const styles = getComputedStyle(document.querySelector(selector));
            return Object.fromEntries(properties.map((property) => [property, styles.getPropertyValue(property)]));
          };
          const desktop = innerWidth > 900;
          return {
            header: read("header.site-header", [
              "position", "height", "min-height", "background-color", "border-bottom-color",
              "border-bottom-width", "box-shadow", "z-index", "padding", "transition-property",
              "transition-duration"
            ]),
            inner: read(".site-header-inner", [
              "display", "flex-direction", "align-items", "justify-content", "gap", "max-width",
              "min-height", "padding", "margin"
            ]),
            brand: read(".admin-shared-brand", [
              "font-family", "font-size", "font-weight", "line-height", "color", "text-decoration-line"
            ]),
            nav: read(".site-nav", ["display", "align-items", "gap", "height", "overflow-x", "flex-wrap"]),
            groupTrigger: desktop ? read(".admin-menu-group-trigger", [
              "display", "height", "min-height", "padding", "gap", "border-radius", "color",
              "background-color", "font-family", "font-size", "font-weight", "line-height"
            ]) : null,
            popover: desktop ? read(".admin-menu-popover", [
              "display", "position", "top", "right", "width", "max-height", "padding", "overflow-y",
              "border-radius", "background-color", "box-shadow", "z-index"
            ]) : null,
            popoverLink: desktop ? read(".admin-menu-popover-link", [
              "font-family", "font-size", "font-weight", "line-height", "height", "min-height", "padding",
              "border-radius", "color", "background-color"
            ]) : null,
            toggle: read(".mobile-toggle", [
              "display", "width", "height", "min-width", "min-height", "border-radius", "background-color", "color"
            ]),
            mobileNav: desktop ? null : read(".mobile-nav", [
              "display", "position", "inset", "width", "max-height", "padding", "overflow-y", "background-color",
              "border-radius", "box-shadow"
            ]),
            mobilePanel: desktop ? null : read(".mobile-nav-panel", [
              "display", "grid-template-columns", "gap", "width", "max-width", "margin", "padding", "background-color"
            ]),
            mobileLink: desktop ? null : read(".admin-shared-mobile-link", [
              "display", "min-height", "padding", "gap", "border-color", "border-radius", "background-color",
              "color", "font-family", "font-size", "font-weight", "line-height", "text-decoration-line"
            ]),
            mobileTitle: desktop ? null : read(".mobile-link-title", [
              "display", "font-family", "font-size", "font-weight", "line-height", "color"
            ]),
            mobileDescription: desktop ? null : read(".admin-shared-mobile-link small", [
              "display", "font-family", "font-size", "font-weight", "line-height", "color"
            ]),
            mobileSummary: desktop ? null : read(".admin-menu-mobile-summary", [
              "display", "min-height", "height", "padding", "color", "background-color"
            ]),
            mobileContent: desktop ? null : read(".admin-menu-mobile-content", [
              "display", "padding", "gap"
            ])
          };
        }"""
    )


def _launch_chromium(playwright):
    try:
        return playwright.chromium.launch()
    except PlaywrightError as default_error:
        for executable in (
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ):
            if executable.exists():
                return playwright.chromium.launch(executable_path=str(executable))
        raise default_error


class AdminMenuCssParityTests(unittest.TestCase):
    maxDiff = None

    def test_shared_menu_has_identical_computed_css_on_every_admin_shell(self):
        """A body-level page theme must not restyle the shared fixed menu."""
        with sync_playwright() as playwright:
            browser = _launch_chromium(playwright)
            try:
                for width, height in ((1280, 900), (820, 900), (390, 844)):
                    fingerprints = {}
                    for body_class in (
                        "admin-page admin-shared-menu-active",
                        "admin-page admin-shared-menu-active legacy-header-transition",
                        "admin-studio-page admin-shared-menu-active admin-shared-menu-offset",
                        "admin-page command-center-page admin-shared-menu-active admin-shared-menu-offset",
                        "ops-page admin-shared-menu-active legacy-header-transition",
                    ):
                        page = browser.new_page(viewport={"width": width, "height": height})
                        page.route("**/*", lambda route, _request, shell=body_class: _serve_admin_fixture(route, shell))
                        page.goto("https://local.test/admin/probe", wait_until="load")
                        if width == 390:
                            page.evaluate(
                                """() => {
                                  const drawer = document.querySelector(".mobile-nav");
                                  drawer.hidden = false;
                                  drawer.classList.add("open");
                                }"""
                            )
                        fingerprints[body_class] = _menu_fingerprint(page)
                        page.close()

                    expected = fingerprints["admin-page admin-shared-menu-active"]
                    for body_class, actual in fingerprints.items():
                        self.assertEqual(
                            actual,
                            expected,
                            f"{body_class} diverged from the shared menu at {width}px",
                        )
            finally:
                browser.close()

    def test_shared_menu_matches_the_public_header_layout_contract(self):
        """Admin keeps its destinations while matching public header geometry."""
        with sync_playwright() as playwright:
            browser = _launch_chromium(playwright)
            try:
                body_class = "admin-page admin-shared-menu-active"

                desktop = browser.new_page(viewport={"width": 1280, "height": 900})
                desktop.route("**/*", lambda route, _request: _serve_admin_fixture(route, body_class))
                desktop.goto("https://local.test/admin/probe", wait_until="load")
                desktop_contract = desktop.evaluate(
                    """() => {
                      const inner = document.querySelector('.site-header-inner');
                      const nav = document.querySelector('.admin-slide-nav');
                      const brand = document.querySelector('.admin-shared-brand');
                      const innerStyle = getComputedStyle(inner);
                      const navStyle = getComputedStyle(nav);
                      const innerRect = inner.getBoundingClientRect();
                      const navRect = nav.getBoundingClientRect();
                      const brandRect = brand.getBoundingClientRect();
                      return {
                        innerMaxWidth: innerStyle.maxWidth,
                        innerPadding: innerStyle.padding,
                        innerGap: innerStyle.gap,
                        navDisplay: navStyle.display,
                        navFlex: navStyle.flex,
                        navRightGap: Math.round(innerRect.right - navRect.right),
                        navStartsAfterBrand: navRect.left > brandRect.right,
                        toggleDisplay: getComputedStyle(document.querySelector('.mobile-toggle')).display
                      };
                    }"""
                )
                self.assertEqual(desktop_contract["innerMaxWidth"], "1400px")
                self.assertEqual(desktop_contract["innerPadding"], "10px 18px")
                self.assertEqual(desktop_contract["innerGap"], "12px")
                self.assertEqual(desktop_contract["navDisplay"], "flex")
                self.assertEqual(desktop_contract["navFlex"], "0 0 auto")
                self.assertEqual(desktop_contract["navRightGap"], 18)
                self.assertTrue(desktop_contract["navStartsAfterBrand"])
                self.assertEqual(desktop_contract["toggleDisplay"], "none")
                desktop.close()

                for width, height in ((820, 900), (390, 844)):
                    mobile = browser.new_page(viewport={"width": width, "height": height})
                    mobile.route("**/*", lambda route, _request: _serve_admin_fixture(route, body_class))
                    mobile.goto("https://local.test/admin/probe", wait_until="load")
                    mobile.evaluate(
                        """() => {
                          const drawer = document.querySelector('.mobile-nav');
                          drawer.hidden = false;
                          drawer.classList.add('open');
                          document.body.classList.add('admin-shared-menu-open');
                        }"""
                    )
                    mobile_contract = mobile.evaluate(
                        """() => {
                          const read = (selector) => {
                            const element = document.querySelector(selector);
                            const style = getComputedStyle(element);
                            const rect = element.getBoundingClientRect();
                            return {
                              display: style.display,
                              width: style.width,
                              minWidth: style.minWidth,
                              height: style.height,
                              padding: style.padding,
                              gap: style.gap,
                              inset: style.inset,
                              backgroundColor: style.backgroundColor,
                              boxShadow: style.boxShadow,
                              left: Math.round(rect.left),
                              right: Math.round(rect.right)
                            };
                          };
                          return {
                            headerHeight: Math.round(document.querySelector('.admin-shared-header').getBoundingClientRect().height),
                            inner: read('.site-header-inner'),
                            nav: read('.admin-slide-nav'),
                            toggle: read('.mobile-toggle'),
                            drawer: read('.mobile-nav'),
                            panel: read('.mobile-nav-panel--admin'),
                            clientWidth: document.documentElement.clientWidth,
                            headerRight: Math.round(document.querySelector('.admin-shared-header').getBoundingClientRect().right),
                            bodyOverflow: getComputedStyle(document.body).overflow
                          };
                        }"""
                    )
                    self.assertEqual(mobile_contract["headerHeight"], 64)
                    self.assertEqual(mobile_contract["inner"]["padding"], "8px 14px")
                    self.assertEqual(mobile_contract["inner"]["gap"], "8px")
                    self.assertEqual(mobile_contract["nav"]["display"], "none")
                    self.assertEqual(mobile_contract["toggle"]["display"], "flex")
                    self.assertEqual(mobile_contract["toggle"]["minWidth"], "94px")
                    self.assertEqual(mobile_contract["toggle"]["height"], "44px")
                    self.assertEqual(mobile_contract["toggle"]["padding"], "0px 12px")
                    self.assertEqual(mobile_contract["toggle"]["gap"], "8px")
                    self.assertEqual(mobile_contract["drawer"]["inset"], "64px 0px 0px")
                    self.assertEqual(mobile_contract["drawer"]["backgroundColor"], "rgba(10, 23, 40, 0.38)")
                    self.assertGreater(mobile_contract["panel"]["left"], 0)
                    self.assertEqual(mobile_contract["panel"]["right"], mobile_contract["headerRight"])
                    self.assertNotEqual(mobile_contract["panel"]["boxShadow"], "none")
                    self.assertIn("hidden", mobile_contract["bodyOverflow"])
                    mobile.close()
            finally:
                browser.close()

    def test_short_and_long_admin_pages_keep_the_same_fixed_header_alignment(self):
        """Opening a short admin page must not shift the shared header sideways."""
        with sync_playwright() as playwright:
            browser = _launch_chromium(playwright)
            try:
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                body_class = "admin-page admin-shared-menu-active"
                page.route("**/*", lambda route, _request: _serve_admin_fixture(route, body_class))
                page.goto("https://local.test/admin/probe", wait_until="load")

                def alignment():
                    return page.evaluate(
                        """() => {
                          const rect = document.querySelector("header.site-header").getBoundingClientRect();
                          return {
                            clientWidth: document.documentElement.clientWidth,
                            gutter: getComputedStyle(document.documentElement).scrollbarGutter,
                            headerLeft: Math.round(rect.left),
                            headerRight: Math.round(rect.right),
                            headerWidth: Math.round(rect.width)
                          };
                        }"""
                    )

                short_page = alignment()
                self.assertEqual(short_page["gutter"], "stable")
                page.evaluate("() => { document.body.style.minHeight = '1800px'; }")
                page.wait_for_timeout(50)
                long_page = alignment()

                self.assertEqual(long_page, short_page)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
