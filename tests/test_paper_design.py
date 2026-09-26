"""Protect the published user journeys while adding the shared paper design."""
import os,unittest,json
from pathlib import Path
from bs4 import BeautifulSoup
from core.art_direction import decorate_art_direction
BASE=Path(os.environ.get('DESIGN_BASE','C:/Project/AI相談/work/genspark-profile-edit/.contextual-release-20260926'))
STYLE='/design-system/studio/paper-design.css'
def signature(html):
 d=BeautifulSoup(html,'html.parser')
 return {'text':list(d.stripped_strings),'sections':[x.get('id') for x in d.select('main section')], 'links':[x.get('href') for x in d.select('a')], 'forms':[str(x) for x in d.select('form')], 'scripts':[str(x) for x in d.select('script')], 'images':[x.get('src','').split('?')[0] for x in d.select('img')]}
class PaperDesignTest(unittest.TestCase):
 def test_shared_design_reaches_home_material_admin_and_login_without_losing_journeys(self):
  raw=(BASE/'runtime/worker/admin-assets.generated.mjs').read_text(encoding='utf-8');admin=json.loads(raw[raw.index('{'):raw.rfind('}')+1])['/admin']['body']
  examples=[(BASE/'public/index.html').read_text(encoding='utf-8'),(BASE/'public/lectures/2026-06-ai-agent-rag-design.html').read_text(encoding='utf-8'),admin,'<!doctype html><html><head><link rel="stylesheet" href="/old.css"></head><body class="studio-theme studio-login"><main><form action="/api/admin/login" method="post"><input name="password" type="password"><button>ログイン</button></form></main></body></html>']
  for before in examples:
   with self.subTest(page=before[:80]):
    after=decorate_art_direction(before);d=BeautifulSoup(after,'html.parser')
    self.assertTrue(any(x.get('href','').split('?')[0]==STYLE for x in d.select('link[rel="stylesheet"]')),'Shared paper design is missing')
    self.assertIn('studio-paper',d.body.get('class',[]))
    self.assertEqual(signature(before),signature(after),'Visual redesign changed user content or behavior')
    self.assertEqual(decorate_art_direction(after),after,'Repeated builds duplicated the design layer')
 def test_existing_images_and_accessible_form_labels_remain_intact(self):
  before='<html><head></head><body><section id="diagnosis"><a href="/ai-agent-readiness/">診断を始める</a><form action="/send" method="post"><label for="mail">メール</label><input id="mail" name="mail" type="email" required><button>送信</button></form><img src="/instagram/photo.webp" alt="活動の写真"></section></body></html>'
  after=decorate_art_direction(before);d=BeautifulSoup(after,'html.parser')
  self.assertEqual(signature(before),signature(after))
  self.assertEqual(d.select_one('label')['for'],d.select_one('input')['id'])
if __name__=='__main__':unittest.main()
