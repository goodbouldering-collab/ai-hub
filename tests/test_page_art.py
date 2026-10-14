import unittest
from core.page_art import apply_page_art, normalize

class PageArtTests(unittest.TestCase):
    def test_home_is_byte_identical_even_with_old_images(self):
        text='<img src="/img/blog-codex-ai-world-hero-20260617.png">\r\n'
        self.assertEqual(apply_page_art(text,'index.html'),text)

    def test_article_only_changes_known_image_and_preserves_copy(self):
        old='/img/blog-codex-ai-world-hero-20260617.png'
        source=f'<h2>本文の順序と数字33</h2><img src="{old}" alt="元の説明"><a href="/contact">相談</a>'
        updated=apply_page_art(source,'blog/2026-06-17-codex-ai-world.html')
        self.assertIn('paper-20261015',updated)
        self.assertIn('<h2>本文の順序と数字33</h2>',updated)
        self.assertIn('alt="元の説明"',updated)
        self.assertIn('<a href="/contact">相談</a>',updated)
        self.assertEqual(apply_page_art(updated,'blog/2026-06-17-codex-ai-world.html'),updated)

    def test_unknown_page_and_external_image_are_unchanged(self):
        source='<img src="https://example.org/img/blog-codex-ai-world-hero-20260617.png">'
        self.assertEqual(apply_page_art(source,'blog/2026-06-17-codex-ai-world.html'),source)
        self.assertEqual(apply_page_art(source,'admin/index.html'),source)

    def test_relative_paths(self):
        self.assertEqual(normalize('./img/course-path-coding.webp?v=1','programming-map.html'),'/img/course-path-coding.webp')

    def test_portrait_overrides_legacy_inline_crop_and_stays_idempotent(self):
        source='<html><head></head><body><div class="speaker-art"><img src="/img/speaker-portrait-painting.webp" style="object-fit:cover!important"></div></body></html>'
        result=apply_page_art(source,'speaker.html')
        self.assertNotIn('object-fit:cover',result)
        self.assertIn('speaker-portrait-gubboru-cafe-20260719.webp',result)
        self.assertIn('aspect-ratio:1/1!important',result)
        self.assertEqual(apply_page_art(result,'speaker.html'),result)

if __name__=='__main__': unittest.main()
