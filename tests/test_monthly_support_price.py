import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "site" / "build_portal.py"
SPEC = importlib.util.spec_from_file_location("monthly_support_price_portal", MODULE_PATH)
portal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portal)


class MonthlySupportPriceTest(unittest.TestCase):
    def test_public_homepage_uses_the_88000_yen_monthly_support_price(self) -> None:
        page = portal.render_portal([], [])

        self.assertTrue("AI伴走支援" in page, "AI伴走支援を公開ページへ表示する")
        self.assertTrue("月額88,000円" in page, "公開ページを月額88,000円へ統一する")
        self.assertNotIn("月額10万円", page)
        self.assertNotIn("月額 100,000円（税込）× 6ヶ月", page)

    def test_ai_support_structured_offer_uses_the_88000_yen_monthly_price(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        support = next(
            node
            for node in graph
            if node.get("@id") == portal.SITE_URL + "/#service-ai-support"
        )

        self.assertEqual("88000", support["offers"]["price"])
        self.assertEqual("JPY", support["offers"]["priceCurrency"])
        self.assertEqual(
            portal.MONTHLY_SUPPORT_BOOK_URL,
            support["offers"]["url"],
        )


if __name__ == "__main__":
    unittest.main()
