# ヒーローの3ボタン（2026-10-12）

状態: PR統合・本番公開・実画面と遷移確認済み。今回の残件なし。

「何からはじめれば？ メニュー選択フロー」「AIに表示されてる？ サイト診断」「ほんとにAI使えてる？ AI実力診断」を、SVGアイコンと2行の短い文言に集約。各ボタン約50px、間隔6px。既存サイト診断ページへの入口を復旧し、選択フローのボタン属性と既存JSを保持する。

生成元は `core/diagnosis_copy.py`。繰り返し生成の重複と復旧リンクの再消失を既存テストで確認する。旧heroの説明と重複見出しだけを除き、画像、3行見出し、本文、7講座、最新ニュース、管理Worker、615公開資産を保全する。候補生成は `scripts/build_hero_actions_release.py`、固定比較元は `deployment/hero-actions/baseline.json`。

Python19件、Cloudflare7件、公開経路検査が成功。検証ブラウザで表示・390px幅・横はみ出しなし・メニューダイアログ起動・2診断ページへの遷移を確認。既存Chromeは一覧取得後に再接続が失敗し、Chrome DevToolsの検証ブラウザを利用。公開データのみを検証し、診断送信・認証変更・顧客データ操作は行わない。

プレビュー: http://127.0.0.1:4103/ 、親PID12044、2026-10-14 19:25:16 JSTまで。作業環境再起動時は終了する場合がある。

## 公開結果

- PR #168、統合・初回公開SHA `6d6ab7ce23b8ceb6a7942910799bd31bddfbd481`、version `8c015433-67d8-4056-9786-d3de2786d973`。ForDeployガード・dry-run成功、index.htmlだけアップロード。
- 本番PC1440px・390pxで3文言・アイコン・各49.65px・横はみ出しなしを確認。選択フローの既存ダイアログ起動、サイト診断とAI実力診断へのクリック遷移成功。7講座とヒーロー画像を保持。
- 7公開資産のSHA一致、health200・管理入口303・login200・未認証管理API401。初回HTTP検査の反映待ちを検出し、再取得後は全件一致。
- 登録元の別作業13ファイルとステージを保全。Present.mdの未公開JPC記録も3方向統合で保持。事業ルートの旧HEADやステージは変更しない。
- Node24.15.0・Python3.12・Wrangler4.90.0。既存Chrome接続が不安定なため、Chrome DevTools検証ブラウザで本番確認した。
- 公開結果記録の統合後も全616資産とWorkerが初回公開と一致することを照合する。最終SHA・version・工程検査は登録元 `tmp/delivery/20261012-hero-three-actions.json`。次回の正常版は登録元 `.hero-three-actions-release-final/public`。

確認URL: https://aiclimb.aiclimb.workers.dev/

