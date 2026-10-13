import unittest
from bs4 import BeautifulSoup
from core.diagnosis_copy import apply_diagnosis_copy

class DiagnosisButtonTests(unittest.TestCase):
    def setUp(self):
        self.document='<html><head></head><body><div class="diagnosis-guide-row"><section><div><a href="/ai-agent-readiness/">診断</a></div></section><section><a href="/seo-llmo-diagnosis/">サイト</a><p>説明</p></section></div><main id="preserved">Keep me</main></body></html>'

    def test_replaces_complete_group_and_preserves_destination_and_siblings(self):
        result=apply_diagnosis_copy(self.document)
        soup=BeautifulSoup(result,'html.parser')
        self.assertEqual([a['href'] for a in soup.select('.diagnosis-guide-row > a')],['/seo-llmo-diagnosis/', '/ai-agent-readiness/'])
        self.assertFalse(soup.select('.diagnosis-guide-row section'))
        self.assertFalse(soup.select('.diagnosis-intro'))
        self.assertEqual(len(soup.select('.diagnosis-guide-row .diagnose-open')),1)
        self.assertEqual(len(soup.select('.diagnosis-guide-row svg')),3)
        self.assertEqual(soup.select_one('#preserved').get_text(),'Keep me')
        self.assertEqual(apply_diagnosis_copy(result),result)
        self.assertEqual(len(soup.select('#diagnosis-copy-style')),1)

    def test_removed_hero_extras_and_trust_position_survive_daily_regeneration(self):
        from core.editorial_feed import apply_home_feed
        from tests.test_home_updates import news_feature
        posts=[dict(href=f'/blog/test-{i}.html',title=f'Article {i}',date=f'2026-10-0{i}') for i in (1,2,3)]
        group=str(BeautifulSoup(self.document,'html.parser').select_one('.diagnosis-guide-row'))
        hero=('<section id="top" class="focus-hero"><div class="focus-hero-copy">'
              '<p class="focus-lead">Hero introduction</p><div class="focus-actions">'
              '<div class="hero-diagnose-cta"><button>Flow</button></div>'
              '<a class="focus-btn secondary" href="/course">Course</a>'
              '<a class="hero-text-link" href="/lectures/">Materials</a></div>'
              '<ul class="focus-trust"><li>Beginner friendly</li></ul></div>'
              '<figure id="restored-hero-image"><img src="/hero.webp" alt="Consultation"></figure></section>')
        source='<html><head></head><body><main>'+hero+news_feature()+group+'<section id="preserved">Keep me</section></main></body></html>'
        rendered=apply_diagnosis_copy(apply_home_feed(source,posts,'css'))
        soup=BeautifulSoup(rendered,'html.parser')
        self.assertIsNotNone(soup.select_one('#top .focus-lead + .focus-trust + .focus-actions #diagnosis-start'))
        self.assertIsNotNone(soup.select_one('#top + #blog > .editorial-feed__list > #ai-news'))
        self.assertFalse(soup.select('.home-learning-links, #restored-hero-image, .focus-actions a.secondary, .focus-actions a.hero-text-link'))
        self.assertEqual(len(soup.select('#diagnosis-start')),1)
        self.assertEqual(soup.select_one('#preserved').get_text(),'Keep me')
        refreshed=apply_diagnosis_copy(apply_home_feed(rendered,posts,'css'))
        self.assertEqual(refreshed,rendered)

    def test_incomplete_input_fails_without_creating_new_destinations(self):
        for source in (self.document.replace('/ai-agent-readiness/','/missing/'),self.document+self.document,'<html></html>'):
            with self.assertRaises(ValueError): apply_diagnosis_copy(source)
