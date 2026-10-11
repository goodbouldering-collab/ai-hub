# トップの不要要素を削除 — 2026-10-12

## 変更

ユーザーが指定した「調べる →」に該当するサイト診断ボタン、相談風景のヒーロー画像、その直下の講習・受講資料リンク行を削除。ヒーローは最大900pxの1列に整理し、残るAI実力診断の説明を合わせる。3行見出し、メニュー選択フロー、ブログ、コース、受講資料本体は保持する。

`core/diagnosis_copy.py` を更新し、日次生成からも同じ削除を適用。公開は `scripts/build_hero_cleanup_release.py` と `deployment/hero-cleanup/baseline.json` を使い、検証済みの `.hero-agent-release-20261012-final` の612資産からindex.htmlだけを変更する。管理Workerは統合済みの最新ソースを使う。画像ファイルと診断ページ自体は既存資産として保持。

## ローカル検証

- Python: diagnosis_buttons / focused_ux / editorial_home / home_updates、19件成功。
- Cloudflare runtime: 7件成功。公開経路検査成功（既存のpartial migration注記あり）。
- 削除3要素、残るリンク・画像・フォーム・スクリプト・コース内容、ヒーロー外HTML、再適用時の一致を検証。
- 既存のeditorial_homeテストがfriendly-glassスタイル追加前の期待値だったため、両テーマのstyleだけを除いて未変更内容を照合するよう更新。Windows一時領域の権限問題はプロジェクト内の一時領域で再検証して解消。
- 既存の事業Chromeを使用。既存タブは他セッションが使用中のため、同じChromeの作業タブでPC1440×1000、スマートフォン390×844を確認。横はみ出しなし、削除要素0件。
- Node24.15.0、Python3.12、Wrangler4.90.0。
- プレビュー: http://127.0.0.1:4096/ 。親PID59512、2026-10-14 01:41:25 JST終了予定。このサーバーが参照する既存worktreeは保持。

## 本番確認

- 実装PR: https://github.com/goodbouldering-collab/ai-hub/pull/155 。チェック2件成功、必須チェック設定なし。実装head `3b7abb62c6a8ccd798e8601e116162e435f96eeb`、初回公開の統合SHA `8d2391e87024a42261c3c35dd3bc4dc6e0e6933c`。
- 登録元で既存差分とステージを保全し、7入力を統合SHAのGit blobから改行変換なしで再生成。中央ForDeployガードとWrangler dry-runに成功。
- 初回公開Cloudflare version `e106b3d8-5f85-4d9e-b4b7-3108bcd7739a`。公開URL: https://aiclimb.aiclimb.workers.dev/ 。公開資産 `.hero-cleanup-release-20261012-first`。
- トップSHA-256 `bcede21b91d6c672563de1cd650c7f1aa6ec2adf4c5f976c74755999d2d29767`。611資産を保持、Worker SHA-256 `5e880e7aeebe0fbb64756d8ff240f7b4a9f98c93d0cd2c05c6c160ec1bf78fc2` は従来版と一致。
- 本番トップ・ブログ一覧・既存ブログ記事・AIニュースのSHAが生成物と一致。health200、未認証管理入口303、管理API401を確認。
- ChromeでPC1440px・スマートフォン390pxの削除結果と横はみ出しなしを確認。メニュー選択フローの開閉、AI実力診断の質問画面への遷移、スマホメニュー開閉が成功。最後に画面サイズを通常へ戻した。
- 今回の残件なし。登録元の別作業とステージを保全。資料本体や画像ファイル、サイト診断ページは削除せず、指定されたトップ表示だけを除去。

公開済み結果をこの文書とPresent.mdへ反映。最終統合・配備SHA、version、工程検査の最新値は登録元と事業ルートの `tmp/delivery/20261012-remove-hero-extras.json` を参照。証拠は同名フォルダ。プレビュー継続中のため、使用中worktreeの削除は行わない。
