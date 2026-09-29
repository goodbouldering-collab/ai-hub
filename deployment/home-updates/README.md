# Compact home updates

The hero-adjacent news entry now includes the latest two posts from the published
blog index. The former lower blog carousel is removed; `/#blog` targets the new
compact group. Desktop uses two columns, and widths up to 800px use one column.
Full titles remain in link text and title attributes; visual titles use two lines.

`core/home_updates.py` is shared by the daily news builder and this focused release.
It reads public blog cards, not Markdown drafts. When publishing later articles,
refresh the public blog index first and reapply `apply_home_updates` to the home
page. The old one-off blog release scripts require a carousel and cannot be used
unchanged with this layout. Rebase the news templates on each verified release.

`build_home_updates_release.py` checks the pinned baseline manifest, all 531 asset
hashes, and the Worker hash. Only `index.html` changes; unchanged assets are linked
to the immutable baseline. Never edit those linked assets in place.

Validation:

```text
python -m unittest tests.test_home_updates tests.test_ai_news_feature_build -v
python scripts/build_home_updates_release.py --baseline <verified-baseline> --output <fresh-release>
python scripts/verify_ai_news_feature.py --assets <fresh-release>/public
```

Deploy from the registered canonical source after merge and the central target
guard, using `deployment/ai-news/published-worker.mjs` at its original location.
Keep API/auth routes unchanged. Verify `/`, `/ai-news/`, `/blog/`, both linked
articles, `/health`, `/admin`, and `/api/admin/ping`. Browser checks at desktop and
iPhone widths are separate from the source, HTTP, and asset checks.
