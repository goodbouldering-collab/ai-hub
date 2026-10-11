import json
from pathlib import Path
import unittest
from bs4 import BeautifulSoup
from core.news_images import apply_news_images, strip_news_images, image_for
from scripts.build_ai_news_feature import render_feature

ROOT=Path(__file__).resolve().parents[1]

class NewsImageTests(unittest.TestCase):
    def test_all_home_entries_get_their_source_image_without_content_changes(self):
        news=json.loads((ROOT/'content/daily-ai-news.json').read_text(encoding='utf-8'))
        source='<html><head></head><body>'+render_feature(news,'10月11日更新')+'</body></html>'
        result=apply_news_images(source,news)
        soup=BeautifulSoup(result,'html.parser')
        for item,img in zip(news['items'],soup.select('.news-thumbnail img')):
            self.assertEqual(image_for(item['url'])['image'],img['src'])
        self.assertEqual(3,len(soup.select('.news-thumbnail')))
        self.assertEqual(source,strip_news_images(result))
        self.assertEqual(result,apply_news_images(result,news))

    def test_wrong_snapshot_is_rejected_and_unknown_source_does_not_reuse_rank_image(self):
        news=json.loads((ROOT/'content/daily-ai-news.json').read_text(encoding='utf-8'))
        source='<head></head>'+render_feature(news,'today')
        news['items'][0]['title']='Different story'
        with self.assertRaisesRegex(ValueError,'do not match'):
            apply_news_images(source,news)
        self.assertIn('イメージ',image_for('https://unknown.example/article')['alt'])

    def test_news_and_codex_detail_text_and_links_are_unchanged(self):
        source='<head></head><li class="daily-ai-news__item"><header><h3><a href="https://unknown.example/story">News</a></h3></header><p>Keep this.</p></li><section class="codex-feature-card"><header>Codex</header><p class="update-card__source"><a href="https://github.com/openai/codex/releases">公式情報</a></p></section>'
        result=apply_news_images(source)
        self.assertEqual(2,len(BeautifulSoup(result,'html.parser').select('.news-thumbnail img')))
        self.assertEqual(source,strip_news_images(result))
        self.assertEqual(result,apply_news_images(result))

if __name__=='__main__':unittest.main()
