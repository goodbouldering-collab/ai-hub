# トップの見出し変更

2026-10-12。本人指定の文言をそのまま使用する。

彦根で使えるAIを学ぶ  
AIエージェント導入たった6%  
30年振りのビッグチャンス

`core/hero_copy.py` とホームテンプレートを更新。既存の見た目・導線を保持する。`scripts/build_hero_copy_release.py` は最新公開版 `.home-refresh-release-first`（SHA `cbe32351f255edc91872f9c8f2a6c0c7dff387dd`）のmanifestと全資産を照合し、h1だけを置換する。612資産中index.htmlのみ変更、611資産と管理Workerは不変。文言は本人指定であり、この変更で統計の追加調査は行っていない。

ChromeのPC1440pxとスマートフォン390pxで3行表示・横はみ出しなしを確認。Focused UXの既存4件成功。公開先は台帳のdefault/aiclimb。本番統合・公開・最終確認はこれから実施する。

工程記録: 事業ルート `tmp/delivery/20261012-hero-agent-copy.json`、証拠 `tmp/delivery/20261012-hero-agent-copy/`。既存差分を含む登録公開元と事業ルートは保全し、今回分だけを分離して共有する。

プレビュー: http://127.0.0.1:4094/ 。親PID50636、2026-10-14 01:07:24 JST終了予定。
