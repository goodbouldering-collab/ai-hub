"""Undo the mistaken article rollback and restore the original home blog list."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import build_ssd_annotations_release as article
from core.home_updates import apply_home_updates, published_posts
from bs4 import BeautifulSoup
from verify_ai_news_feature import verify

CONTRACT = ROOT / 'deployment/cloudflare-blog/restore-home-blog-list-20261009.json'


def build(baseline, output):
    baseline, output = baseline.resolve(), output.resolve()
    article.CONTRACT = CONTRACT
    article.build(baseline, output)
    public = output / 'public'
    home = (public / 'index.html').read_text(encoding='utf-8')
    blog = (public / 'blog/index.html').read_text(encoding='utf-8')
    css_path = ROOT / 'site/templates/ai-news/home-updates.css'
    restored = apply_home_updates(home, blog, css_path.read_text(encoding='utf-8'))
    assert apply_home_updates(restored, blog, css_path.read_text(encoding='utf-8')) == restored
    (public / 'index.html').write_text(restored, encoding='utf-8', newline='\n')
    soup = BeautifulSoup(restored, 'html.parser')
    cards = soup.select('#blog-carousel .blog-card')
    posts = published_posts(blog)[:7]
    assert len(cards) == 7 and len(soup.select('#blog')) == 1
    assert soup.select_one('#blog').find_next_sibling()['id'] == 'speaker'
    assert len(soup.select('#latest-blog li')) == 2
    assert [c['href'] for c in cards] == [p['href'] for p in posts]
    for c, p in zip(cards, posts):
        assert c.h3.get_text() == p['title']
        assert (public / p['href'].lstrip('/')).is_file()
        assert c.img and (public / c.img['src'].lstrip('/')).is_file()
    # Compare outside the intended new list / compact anchor change byte for byte.
    strip_list = lambda s: re.sub(r"<section\b[^>]*id=['\"]blog['\"][^>]*>.*?</section>", '', s, flags=re.S)
    assert strip_list(restored).replace('id="latest-blog"', 'id="blog"') == home
    checks = verify(lambda name: (public / name).read_text(encoding='utf-8'))
    result = json.loads((output / 'verification.json').read_text(encoding='utf-8'))
    additional = [Path(__file__), ROOT/'scripts/build_ssd_annotations_release.py', ROOT/'scripts/verify_ai_news_feature.py', css_path]
    additional += [ROOT/'config/home-blog-images.json']
    additional += [ROOT/'content/blog'/(Path(p['href']).stem+'.md') for p in posts if (ROOT/'content/blog'/(Path(p['href']).stem+'.md')).is_file()]
    for p in additional:
        result['source_inputs'][p.relative_to(ROOT).as_posix()] = article.digest(p)
    result['inputs'] = sorted(result['source_inputs'])
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--', *result['inputs']], cwd=ROOT, text=True)
    result.update(assets=article.hashes(public), source_inputs_clean=not dirty.strip(), source_input_status=dirty.splitlines(), home_blog_checks=checks, home_blog_posts=posts)
    before = json.loads(CONTRACT.read_text(encoding='utf-8'))['assets']
    assert sorted(p for p in before if before[p] != result['assets'][p]) == result['changed_assets']
    previous = json.loads((ROOT/'deployment/cloudflare-blog/restore-blog-display-20261009.json').read_text(encoding='utf-8'))['assets']
    for p in result['changed_assets']:
        if p != 'index.html':
            assert result['assets'][p] == previous[p], 'Article rollback was not fully undone: '+p
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'home_blog_cards':len(cards),'latest_article':posts[0]['title'],'other_assets_preserved':result['preserved_assets'],'article_rollback_undone':True,'source_inputs_clean':result['source_inputs_clean']},ensure_ascii=False))

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    build(args.baseline,args.output)
