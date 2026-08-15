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
  __STYLESHEETS__
</head>
<body>
  <header class="site-header admin-shared-header" id="site-header">
    <div class="site-header-inner">
      <a class="site-logo admin-shared-brand" href="/admin">
        <span class="admin-shared-brand-name">AI相談</span>
        <span class="admin-shared-brand-context">管理画面</span>
      </a>
      <div class="admin-page-context"><strong>管理ホーム</strong></div>
      <nav class="site-nav admin-slide-nav" aria-label="管理ページ固定メニュー">
        <div class="admin-scroll-menu">
          <a class="admin-scroll-link" href="/admin/command-center">実行指令室</a>
          <a class="admin-scroll-link" href="/admin/blog">ブログ管理</a>
        </div>
      </nav>
      <button class="mobile-toggle" type="button" aria-label="補助メニューを開く">
        <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </div>
    <div class="mobile-nav" id="mobile-nav" hidden>
      <div class="mobile-nav-panel mobile-nav-panel--admin">
        <section class="admin-shared-mobile-section">
          <span class="mobile-nav-label">管理</span>
          <div class="mobile-link-list">
            <a class="admin-shared-mobile-link" href="/admin/command-center">
              <span class="mobile-link-title">実行指令室</span>
              <small>予定・指示・相場・Codexをまとめて動かす</small>
            </a>
          </div>
        </section>
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
          return {
            header: read("header.site-header", [
              "position", "height", "min-height", "background-color", "border-bottom-color",
              "border-bottom-width", "box-shadow", "z-index", "padding"
            ]),
            inner: read(".site-header-inner", [
              "display", "flex-direction", "align-items", "justify-content", "gap", "max-width",
              "min-height", "padding", "margin"
            ]),
            brand: read(".admin-shared-brand", [
              "font-family", "font-size", "font-weight", "line-height", "color", "text-decoration-line"
            ]),
            nav: read(".site-nav", ["display", "align-items", "gap", "height", "overflow-x", "flex-wrap"]),
            link: read(".admin-scroll-link", [
              "font-family", "font-size", "font-weight", "line-height", "height", "min-height", "padding",
              "border-radius", "color", "background-color"
            ]),
            toggle: read(".mobile-toggle", [
              "display", "width", "height", "min-width", "min-height", "border-radius", "background-color", "color"
            ]),
            mobileNav: read(".mobile-nav", [
              "display", "position", "inset", "width", "max-height", "padding", "overflow-y", "background-color",
              "border-radius", "box-shadow"
            ]),
            mobilePanel: read(".mobile-nav-panel", [
              "display", "grid-template-columns", "gap", "width", "max-width", "margin", "padding", "background-color"
            ]),
            mobileLink: read(".admin-shared-mobile-link", [
              "display", "min-height", "padding", "gap", "border-color", "border-radius", "background-color",
              "color", "font-family", "text-decoration-line"
            ]),
            mobileLabel: read(".mobile-nav-label", [
              "display", "padding", "font-family", "font-size", "font-weight", "line-height", "letter-spacing", "color"
            ]),
            mobileTitle: read(".mobile-link-title", [
              "display", "font-family", "font-size", "font-weight", "line-height", "color"
            ]),
            mobileDescription: read(".admin-shared-mobile-link small", [
              "display", "font-family", "font-size", "font-weight", "line-height", "color"
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
                for width, height in ((1280, 900), (390, 844)):
                    fingerprints = {}
                    for body_class in (
                        "admin-page admin-shared-menu-active",
                        "admin-studio-page admin-shared-menu-active admin-shared-menu-offset",
                        "admin-page command-center-page admin-shared-menu-active admin-shared-menu-offset",
                        "ops-page admin-shared-menu-active",
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


if __name__ == "__main__":
    unittest.main()
