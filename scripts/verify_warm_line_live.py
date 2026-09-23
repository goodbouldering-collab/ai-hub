"""Read-only production checks for the warm artwork and original portrait release."""
from pathlib import Path
import argparse,json,sys
import requests
from bs4 import BeautifulSoup
from verify_editorial_live import fetch,digest,route_identity,response_summary,PRODUCTION_URL,PUBLIC_ROUTES
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.art_direction import LESSONS,PORTRAIT,EDITORIAL_VERSION
from build_warm_line_release import NAMES

def verify(release):
    m=json.loads((release/'verification.json').read_text(encoding='utf-8'))
    assert m['source_inputs_clean']
    routes=[x for x in PUBLIC_ROUTES if '/images/soft-' not in x[0]]
    names=[f'design-system/studio/images/soft-{n}.webp' for n in NAMES]+[f'design-system/studio/images/{n}.webp' for n,_ in LESSONS.values()]+[PORTRAIT.lstrip('/')]
    routes += [('/'+n,n) for n in names]
    routes += [('/design-system/studio/soft-playground.css','design-system/studio/soft-playground.css')]
    s=requests.Session();s.trust_env=False;s.headers['User-Agent']='Mozilla/5.0 (compatible; AIConsultReleaseVerifier/1.0)'
    results=[]
    for url,name in routes:
        r,redirects=fetch(s,PRODUCTION_URL,url)
        assert r.status_code==200 and digest(r.content)==m['assets'][name],url
        if name.endswith('.html'):
            soup=BeautifulSoup(r.content,'html.parser')
            assert soup.select_one('#studio-editorial')['href'].endswith('?v='+EDITORIAL_VERSION),url
            canonical=soup.select_one('link[rel="canonical"]')['href']
            assert canonical.startswith(PRODUCTION_URL) and route_identity(canonical[len(PRODUCTION_URL):])==route_identity(url),url
            if name in ['index.html','speaker.html']:
                assert len(soup.select('img[src="'+PORTRAIT+'"]'))==1
            if name=='index.html':
                assert len(soup.select('#lecture-carousel img[src^="/design-system/studio/images/lesson-"]'))==7
                assert len(soup.select('#instagram img'))==6 and soup.select_one('#instagram').get_text(strip=True)=='Instagram'
                if EDITORIAL_VERSION=='20260923-cyber':
                    assert not soup.select('.readiness-guide__summary,.focus-section-lead,.pf-sum')
                    assert soup.select_one('.diagnosis-guide-row').find_next_sibling()['id']=='studio-playground'
                    assert not soup.select('.soft-playground__output')
                    assert len(soup.select('[data-sp-tab]'))==3
                    assert all('?v='+EDITORIAL_VERSION in img['src'] for img in soup.select('img[src^="/design-system/studio/images/"]'))
        results.append(response_summary(r,url,redirects)|{'matches_release':True,'passed':True})
    for url,status in [('/health',200),('/admin',303),('/admin/login',200),('/api/admin/ping',401)]:
        r,redirects=fetch(s,PRODUCTION_URL,url,follow=False)
        assert r.status_code==status,url
        if url=='/admin':assert r.headers['Location'].split('?')[0]=='/admin/login'
        if url=='/admin/login':assert '?v='+EDITORIAL_VERSION in r.text
        results.append(response_summary(r,url,redirects)|{'passed':True})
    return {'source_sha':m['source_sha'],'passed':True,'checked':len(results),'results':results}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();proof=verify(a.release);a.output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:proof[k] for k in ['source_sha','passed','checked']}))
