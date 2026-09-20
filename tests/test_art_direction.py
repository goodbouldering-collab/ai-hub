import unittest
from core.art_direction import decorate_art_direction,PORTRAIT
class ArtDirectionTest(unittest.TestCase):
 def test_original_portrait_and_existing_content(self):
  text='<h1>由井 辰美</h1><img class="speaker-painting" src="/design-system/studio/images/soft-mentor.webp" alt="old"><p>元の紹介文</p>'
  result=decorate_art_direction(text)
  self.assertIn('src="'+PORTRAIT+'"',result)
  self.assertIn('<h1>由井 辰美</h1>',result);self.assertIn('<p>元の紹介文</p>',result)
  self.assertEqual(decorate_art_direction(result),result)
 def test_blog_instagram_and_venue_unchanged(self):
  text='<img src="/img/blog-cloudflare-ai-hero-20260918.png"><img src="/instagram/DcB0VodkgJ9.webp"><img src="/img/gubboru-cafe.webp">'
  self.assertEqual(decorate_art_direction(text),text)
 def test_material_cover_is_updated_without_changing_link(self):
  text='<a href="/lectures/2026-04-ai-kihon.html"><img src="/lectures/assets/covers/2026-04-ai-kihon.png" alt="old"></a>'
  result=decorate_art_direction(text)
  self.assertIn('lesson-agent.webp',result);self.assertIn('href="/lectures/2026-04-ai-kihon.html"',result)
if __name__=='__main__':unittest.main()
