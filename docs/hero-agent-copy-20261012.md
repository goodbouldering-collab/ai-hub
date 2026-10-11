# トップの見出し変更

2026-10-12。本人指定の文言をそのまま使用する。

彦根で使えるAIを学ぶ  
AIエージェント導入たった6%  
30年振りのビッグチャンス

`core/hero_copy.py` とホームテンプレートを更新。既存の見た目・導線を保持する。`scripts/build_hero_copy_release.py` は最新公開版 `.home-refresh-release-first`（SHA `cbe32351f255edc91872f9c8f2a6c0c7dff387dd`）のmanifestと全資産を照合し、h1だけを置換する。612資産中index.htmlのみ変更、611資産と管理Workerは不変。文言は本人指定であり、この変更で統計の追加調査は行っていない。

ChromeのPC1440pxとスマートフォン390pxで3行表示・横はみ出しなしを確認。Focused UXの既存4件、Cloudflare7件、公開経路検査とdry-runが成功。公開先は台帳のdefault/aiclimb。

PR #152を統合し、並行作業を含む最新main `d0058f9cec0c5d223218cb5236c8bb8c2cb45ee5` のGit blob6入力から再生成して公開。初回Cloudflare version `993e51d1-c5cd-414a-88b5-b1f38f113e0f`。Wrangler4.90.0・Node24.15.0・Python3.12。中央ForDeployガード成功。本番ChromeでPC1440px/スマートフォン390pxの3行を確認。トップ・ブログ一覧・既存記事・ニュースの4資産はSHA一致、health200・未ログイン管理入口303・管理API401を確認。旧記事.htmlは既存の307転送後に200となる。

今回の残件なし。記録更新後の最終SHA・Cloudflare version・完了検査は下記工程記録を参照。公開面は `.hero-agent-release-20261012/public`。手動worktreeは48時間プレビューと作業証拠を保持するため残し、プレビュー終了後にクリーン状態と統合済みを再確認して整理する。

工程記録: 事業ルート `tmp/delivery/20261012-hero-agent-copy.json`、証拠 `tmp/delivery/20261012-hero-agent-copy/`。既存差分を含む登録公開元と事業ルートは保全し、今回分だけを分離して共有する。並行統合されたPR #150の管理機能を保持するため、配備Workerは最新の統合済みソース `deployment/admin-workspace/published-worker.mjs` を使う。旧baselineのWorkerへ戻さない。

プレビュー: http://127.0.0.1:4094/ 。親PID50636、2026-10-14 01:07:24 JST終了予定。
