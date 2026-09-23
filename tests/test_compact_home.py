import unittest
from core.compact_home import compact_home
from core.soft_studio import decorate_soft_playground

class CompactHomeTest(unittest.TestCase):
    def test_removes_only_teasers_and_preserves_actions_prices_and_details(self):
        html='''<p class='readiness-guide__summary'>説明</p><p class="focus-section-lead">説明</p><a href="/site"><div class='pf-sum'>実績の説明</div><strong>サイト名</strong></a><div class="compact-course-meta">5,500円</div><details><summary>内容を見る</summary><p>必要な受講条件</p></details>'''
        result=compact_home(html)
        self.assertNotIn('説明',result)
        self.assertIn('<a href="/site"><strong>サイト名</strong></a>',result)
        self.assertIn('5,500円',result)
        self.assertIn('<p>必要な受講条件</p>',result)
        self.assertEqual(compact_home(result),result)

    def test_moves_existing_playground_after_nested_diagnosis_pair(self):
        source='<html><head></head><body><section id="studio-playground">旧表示</section><section id="ai-news">新しい記事</section><div class="diagnosis-guide-row"><section><div>診断1</div></section><section><div>診断2</div></section></div><section id="packages">料金</section></body></html>'
        result=decorate_soft_playground(source)
        self.assertLess(result.index('診断2'),result.index('<section id="studio-playground"'))
        self.assertLess(result.index('<section id="studio-playground"'),result.index('<section id="packages"'))
        self.assertNotIn('旧表示',result)
        self.assertEqual(decorate_soft_playground(result),result)
        self.assertNotIn('soft-playground__output',result)
        self.assertEqual(result.count('data-sp-mode='),6)

if __name__=='__main__':unittest.main()
