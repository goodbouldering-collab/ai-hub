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
- Node24.15.0、Python3.12、公開に使用するWranglerは配備時のログで記録。
- プレビュー: http://127.0.0.1:4096/ 。親PID59512、2026-10-14 01:41:25 JST終了予定。このサーバーが参照する既存worktreeは保持。

## 公開状態

ローカル検証済み。commit・PR・統合・本番配備と画面確認はこれから。今回の工程記録は `tmp/delivery/20261012-remove-hero-extras.json`。公開結果を同記録とこの文書へ更新する。別作業の未コミット変更・ステージは保全する。
