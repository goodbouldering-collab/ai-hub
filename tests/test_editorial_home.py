import re
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from core.editorial_home import apply_editorial_home, replace_home_art

ROOT = Path(__file__).resolve().parents[1]

class EditorialHomeTests(unittest.TestCase):
    def test_real_course_copy_prices_controls_and_destinations_are_preserved(self):
        source = (ROOT / 'site/templates/ai-news/home.html').read_text(encoding='utf-8')
        result = apply_editorial_home(source)
        before, after = [BeautifulSoup(x, 'html.parser') for x in (source, result)]
        old_cards, new_cards = before.select('.compact-course-card'), after.select('.compact-course-card')
        self.assertEqual(len(old_cards), 6)
        self.assertEqual(len(new_cards), 6)
        for old, new in zip(old_cards, new_cards):
            self.assertEqual(old.get_text(' ', strip=True), new.get_text(' ', strip=True))
            self.assertEqual([a['href'] for a in old.select('a[href]')], [a['href'] for a in new.select('a[href]')])
            self.assertEqual([str(d) for d in old.select('details')], [str(d) for d in new.select('details')])
            self.assertIsNotNone(new.select_one(':scope > .editorial-course-lead .compact-course-heading'))
            self.assertIsNotNone(new.select_one(':scope > .editorial-course-lead .compact-course-meta'))
            self.assertIsNotNone(new.select_one(':scope > .studio-course-body .compact-course-tail'))
        self.assertEqual(apply_editorial_home(result), result)

    def test_only_explanatory_artwork_changes(self):
        source = '<head></head><img src="/design-system/studio/images/soft-hero.webp?v=old" alt="old"><img src="/img/speaker.webp" alt="講師"><img src="/img/portfolio/site.jpg" alt="実績">'
        result = replace_home_art(source)
        self.assertIn('/photo-20261011/hero.webp', result)
        self.assertIn('<img src="/img/speaker.webp" alt="講師">', result)
        self.assertIn('<img src="/img/portfolio/site.jpg" alt="実績">', result)
        self.assertEqual(replace_home_art(result), result)

    def test_unrelated_sections_and_scripts_remain_exact(self):
        source = '<head><style>keep</style></head><main><section id="speaker">写真と紹介</section><script>const x = 1;</script></main>'
        result = apply_editorial_home(source, 'rules')
        self.assertEqual(re.sub(r'<style id="editorial-home-style">.*?</style>', '', result, flags=re.S), source)

    def test_missing_course_price_fails_instead_of_dropping_content(self):
        source = '<head></head><article class="compact-course-card"><img class="compact-course-visual"><div class="studio-course-body"><h3>broken</h3></div></article>'
        with self.assertRaises(ValueError):
            apply_editorial_home(source)

if __name__ == '__main__':
    unittest.main()
