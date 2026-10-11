import unittest
from bs4 import BeautifulSoup
from core.diagnosis_copy import apply_diagnosis_copy

class DiagnosisButtonTests(unittest.TestCase):
    def setUp(self):
        self.document='<html><head></head><body><div class="diagnosis-guide-row"><section><div><a href="/ai-agent-readiness/">診断</a></div></section><section><a href="/seo-llmo-diagnosis/">サイト</a><p>説明</p></section></div><main id="preserved">Keep me</main></body></html>'

    def test_replaces_complete_group_and_preserves_destination_and_siblings(self):
        result=apply_diagnosis_copy(self.document)
        soup=BeautifulSoup(result,'html.parser')
        self.assertEqual([a['href'] for a in soup.select('.diagnosis-guide-row > a')],['/ai-agent-readiness/','/seo-llmo-diagnosis/'])
        self.assertFalse(soup.select('.diagnosis-guide-row section, .diagnosis-guide-row p'))
        self.assertEqual(soup.select_one('#preserved').get_text(),'Keep me')
        self.assertEqual(apply_diagnosis_copy(result),result)
        self.assertEqual(len(soup.select('#diagnosis-copy-style')),1)

    def test_incomplete_input_fails_without_creating_new_destinations(self):
        for source in (self.document.replace('/seo-llmo-diagnosis/','/missing/'),self.document+self.document,'<html></html>'):
            with self.assertRaises(ValueError): apply_diagnosis_copy(source)
