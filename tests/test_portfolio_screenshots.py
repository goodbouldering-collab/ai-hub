from __future__ import annotations

import unittest

from scripts.capture_portfolio_screenshots import safe_slug, screenshot_path, selected_items


class PortfolioScreenshotTests(unittest.TestCase):
    def test_safe_slug_normalizes_for_file_name(self) -> None:
        self.assertEqual(safe_slug("N Design / 彦根"), "n-design")

    def test_screenshot_path_is_public_static_jpeg(self) -> None:
        path, public_path = screenshot_path({"slug": "profit-hikone"})
        self.assertEqual(path.name, "profit-hikone.jpg")
        self.assertEqual(public_path, "/img/portfolio/profit-hikone.jpg")

    def test_selected_items_only_returns_live_sites(self) -> None:
        items = [
            {"name": "Live", "url": "https://example.com/", "status": "live"},
            {"name": "Dev", "url": "https://dev.example.com", "status": "dev"},
        ]
        self.assertEqual([item["name"] for item in selected_items(items)], ["Live"])
        self.assertEqual(
            [item["name"] for item in selected_items(items, "https://example.com")],
            ["Live"],
        )


if __name__ == "__main__":
    unittest.main()
