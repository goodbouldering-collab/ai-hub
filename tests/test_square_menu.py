import json
import re
import unittest
from pathlib import Path
from core.square_menu import apply_square_menu

ROOT = Path(__file__).resolve().parents[1]

class SquareMenuTests(unittest.TestCase):
    def test_real_home_menu_and_daily_rebuild(self):
        before = (ROOT/'site/templates/ai-news/home.html').read_text(encoding='utf-8')
        after = apply_square_menu(before)
        self.assertEqual(apply_square_menu(after), after)
        self.assertIn('AI個別相談120分｜AI時代のなんでも相談', after)
        self.assertIn('初回相談30分・無料。その後の伴走支援', after)
        self.assertIn("bookingMeta: '20分・無料'", after)
        self.assertNotIn('60分・5,500円', after)
        old_cards = re.findall(r'<article\b.*?</article>', before, re.S)
        new_cards = re.findall(r'<article\b.*?</article>', after, re.S)
        self.assertEqual(len(old_cards), len(new_cards))
        targets = ('TO3XHZT6XP3OM4QBDYMW7TZP', 'S7GERYVDIPRV76DKXCC3WJWH', 'V57YTNICA2KV2TN7ENARAVQE')
        for old, new in zip(old_cards, new_cards):
            if not any(service in old for service in targets):
                self.assertEqual(old, new)

    def test_nested_offer_updates_only_individual_price(self):
        data = {'@graph': [{'name': 'AI個別講習 60分', 'offers': {'price': '5500'}},
                           {'name': 'AIエージェント講習', 'offers': {'price': '5500'}}]}
        source = '<script type="application/ld+json">'+json.dumps(data, ensure_ascii=False)+'</script>'
        result = json.loads(apply_square_menu(source).split('>', 1)[1].split('</script>')[0])
        self.assertEqual(result['@graph'][0]['offers']['price'], '8800')
        self.assertEqual(result['@graph'][1]['offers']['price'], '5500')

if __name__ == '__main__':
    unittest.main()
