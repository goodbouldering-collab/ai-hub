# トップのブログ入れ替え・講習メニューの高さ調整

- ヒーロー直下の最新ブログ2件と、下段の画像付きブログ7件を入れ替える。
- 上段は小さな画像と日付・タイトルの横スクロールカード。本文抜粋は省き、タイトルと記事へのリンクを残す。
- 下段の最新2件は講師紹介の前に配置する。
- 講習6コースは画像をPC 88px、スマートフォン64pxに縮小し、カード・見出し・案内・会場の余白を詰める。説明、価格、詳細、受講者の声、申込先は保持する。
- 日次再生成にも同じ変換を適用し、入れ替え後の構成を維持する。

## 公開手順・検証

`python scripts/build_compact_blog_courses_release.py --baseline <.restore-home-blog-list-20261009> --output <fresh release directory>`

既存の検証済み550アセットからindex.htmlだけを変更する。記事と他549ファイル・Workerはハッシュ一致を検証する。講習メニューを含む他セクションのHTMLは一致を検証し、CSSのみで高さを変更する。

単体テスト5件、Cloudflare runtimeテスト7件、Cloudflare policy、生成済みHTML検査を実施する。公開は台帳のgenspark-profile-edit/cloudflare-runtimeでガードを通し、統合済みSHAの生成物を使う。

PC・iPhone実画面の確認は専用Chromeへのツール接続待ち。高さの実測とスクロール・メニュー操作は未確認で、コード/HTTP検証とは区別する。
