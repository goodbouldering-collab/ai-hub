import json
import re
import unittest
from pathlib import Path
from core.voice_memo_course import apply_voice_memo_course, course_data, square_description
from core.square_menu import apply_square_menu
from core.home_blog_layout import compact_home_blog

ROOT = Path(__file__).resolve().parents[1]


class VoiceMemoCourseTests(unittest.TestCase):
    def test_course_replaces_only_selected_card_and_survives_daily_rebuild(self):
        before = (ROOT/'site/templates/ai-news/home.html').read_text(encoding='utf-8')
        after = apply_voice_memo_course(before)
        cards = lambda text: re.findall(r'<article\b.*?</article>', text, re.S)
        self.assertEqual(len(cards(before)), len(cards(after)))
        for old, new in zip(cards(before), cards(after)):
            if course_data()['square']['item_id'] not in old:
                self.assertEqual(old, new)
            else:
                self.assertIn('8,800円', new)
                self.assertIn('120分', new)
                self.assertIn('受講後にできること', new)
                self.assertNotIn('受講された方の感想', new)
                self.assertNotIn('blockquote', new)
        rebuilt = apply_square_menu(after)
        self.assertEqual(apply_square_menu(rebuilt), rebuilt)
        self.assertIn(course_data()['name'], rebuilt)

    def test_schema_preserves_unrelated_prices(self):
        card = '<article class="compact-course-card">S7GERYVDIPRV76DKXCC3WJWH</article>'
        schema = {'@graph': [{'@type': 'Course', 'name': 'AIコーディング講習', 'offers': {'price': '11000'}, 'review': {'text': 'old'}}, {'@type': 'Course', 'name': '別の講習', 'offers': {'price': 11000}}]}
        after = apply_voice_memo_course(card + '<script type="application/ld+json">' + json.dumps(schema) + '</script>')
        data = json.loads(re.search(r'<script.*?>(.*?)</script>', after, re.S)[1])['@graph']
        self.assertEqual(data[0]['offers']['price'], '8800')
        self.assertNotIn('review', data[0])
        self.assertEqual(data[1]['offers']['price'], 11000)

    def test_bookable_course_copy_and_scoped_compact_layout(self):
        c = course_data()
        self.assertIn('8,800円', square_description(c))
        self.assertIn('AIエージェント講習を1回以上', square_description(c))
        source = '<head></head><section id="blog"><h2>ブログ</h2></section>'
        after = compact_home_blog(source)
        self.assertEqual(compact_home_blog(after), after)
        self.assertEqual(after[after.index('<section'):], source[source.index('<section'):])
        self.assertEqual(compact_home_blog('<head></head><main>Archive</main>'), '<head></head><main>Archive</main>')
