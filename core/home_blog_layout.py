"""Keep the homepage reading list compact without changing the archive layout."""
import re

STYLE = '''<style id="home-blog-compact">
body.studio-theme.studio-editorial.studio-home #blog.editorial-feed--home .editorial-feed__row{grid-template-columns:112px minmax(0,1fr)!important;gap:16px!important;padding:12px 0!important;align-items:center!important}
#blog.editorial-feed--home .editorial-feed__media{width:112px!important;height:76px!important;border-radius:9px}
#blog.editorial-feed--home .editorial-feed__title{font-size:18px!important;line-height:1.5!important;margin-bottom:2px!important}
#blog.editorial-feed--home .editorial-feed__meta{margin-bottom:3px!important}
#blog.editorial-feed--home .editorial-feed__heading{margin-bottom:6px!important}
#blog.editorial-feed--home .editorial-feed__summary{font-size:13px!important;line-height:1.5!important}
#blog.editorial-feed--home .editorial-feed__actions{margin-top:14px!important}
@media(max-width:600px){body.studio-theme.studio-editorial.studio-home #blog.editorial-feed--home .editorial-feed__row{grid-template-columns:72px minmax(0,1fr)!important;gap:10px!important;padding:11px 0!important}#blog.editorial-feed--home .editorial-feed__media{width:72px!important;height:64px!important}#blog.editorial-feed--home .editorial-feed__title{font-size:15px!important}#blog.editorial-feed--home .editorial-feed__summary{font-size:12px!important}}
</style>'''


def compact_home_blog(document):
    if not re.search(r'id=[\x27"]blog[\x27"]', document): return document
    document = re.sub(r'<style id="home-blog-compact">.*?</style>', '', document, flags=re.S)
    return document.replace('</head>', STYLE + '</head>', 1)
