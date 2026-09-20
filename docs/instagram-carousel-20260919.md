# トップ上部のInstagram投稿欄

AI相談を初めて訪れた人が、由井辰美の日々の発信に触れられる入口。
メイン紹介の直後・AIニュースの前に、`@tatsumi.yui` の公開投稿6件を配置する。
Instagram公式のフレームを横に並べ、左右ボタン、キーボード、
フレーム外側での横スワイプで投稿を切り替える。動画は自動再生しない。

- アカウントと掲載投稿: `config/instagram.json`
- 共通描画: `core/instagram_feed.py`
- 表示と操作: `site/static/instagram-feed.css` / `instagram-feed.js`
- 通常再生成: `site/build_portal.py` から同じ共通描画を呼ぶ。
- 公開データ生成: `python scripts/build_instagram_release.py --output .editorial-release-instagram-20260919`

2026-09-19に認証不要の公式プロフィール埋め込み
`https://www.instagram.com/tatsumi.yui/embed/` から投稿と投稿者を確認。
共有用追跡パラメータを省いた正規URLを使う。
掲載投稿は設定ファイルで管理する。新規投稿の自動取得やアカウント認証は追加しない。
閲覧環境やInstagram側の制限でフレームが表示できない場合にも、投稿・プロフィールへのリンクは残る。

公開元は中央台帳の `work/genspark-profile-edit/cloudflare-runtime`。
直前の公開SHAとmanifestを `deployment/instagram/baseline.json` に固定し、
トップ1件と新規CSS/JS2件だけを変更。既存476資産とruntime15件はバイト単位で保持する。
コミット、PR、必須チェック、main統合後のSHAから再生成し、中央ガードの後に公開。
本番のSHA・URL・HTTP検証・画面確認はリリース出力内の `production-summary.json` に保存する。

## 検証

- 6件すべての公式埋め込みがHTTP 200、投稿者 `tatsumi.yui`、フレーム表示の拒否なし。
- 通常のポータル生成と本番スナップショット生成の両方で、投稿欄が重複せず上部に入る。
- 公開中の変更前ページ・APIなど18項目が保存済みリリースと一致。
- 既存の操作テスト11件、JavaScript構文検査、Git差分検査、Cloudflare公開経路ガードが成功。
- 登録設定を使い `runtime/worker/public-entry.mjs` を `--bundle` でdry-run検証。
  依存はコミット済み `deployment/profile/package-lock.json` に対応する既存node_modulesを使う。
- AI相談のChromeショートカットはProfile 1。今回の接続一覧に同プロフィールがないため、
  画面確認はユーザーへCodex内ブラウザの利用可否を照会中。HTTP・構造検証と目視を区別する。

## 2026-09-20 更新
公式iframeを廃止し、投稿画像のみの小型サムネイルに変更。現行手順は docs/design/cool-line-20260920.md と scripts/build_cool_line_release.py を参照。旧ビルドは当日の履歴用。
