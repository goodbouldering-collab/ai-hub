# CodexとWorkers AIで減らせる手間 — 公開記録
最終更新: 2026-10-09

対象: 既存AI相談ブログ。ユーザーが最終タイトル・本文を承認し、投稿・デプロイを指示。本文は承認稿を保持し、具体的な相談案件や個人名は掲載しない。イメージ画像5点（built-in image_gen、WebP計350KB）を追加し、実画面ではないと明示した。プロンプトは image-prompts.json。

- 記事: content/blog/2026-10-09-codex-workers-ai-workflow.md
- 公開予定: https://aiclimb.aiclimb.workers.dev/blog/2026-10-09-codex-workers-ai-workflow
- 公開元: 中央台帳の work/genspark-profile-edit/cloudflare-runtime、Target default / aiclimb。
- ビルド: scripts/build_codex_workers_ai_release.py。直前公開版 .daily-news-release-20261009/public を550資産のmanifestと本番7資産のSHA256で照合。
- 変更範囲: 記事HTML・画像5点を追加、トップ・ブログ一覧・サイトマップのみ変更。547資産とWorkerを保持。
- ローカル検証: 記事・ホーム21テスト、Worker7テスト、ニュース構造検証、Cloudflare公開経路policy成功。画像のGit追跡検査はstage後に成功。
- 画面: AI相談 - Chrome.lnkはProfile 1。対応Chrome接続が利用できずnative起動APIもないためCodex内ブラウザでローカル1440px/390px表示、タイトル・画像・横幅・検索メニュー確認。
- プレビュー: http://127.0.0.1:4075/blog/2026-10-09-codex-workers-ai-workflow.html 。Start-LocalPreview.ps1、親PID 47448、2026-10-11の同時刻まで48時間。初回sandbox起動は接続不可、通常環境の起動で復旧。
- 公式根拠: https://learn.chatgpt.com/docs/projects 、https://learn.chatgpt.com/docs/agent-configuration/agents-md 、https://learn.chatgpt.com/docs/app-server 、https://developers.cloudflare.com/workers-ai/get-started/workers-wrangler/ 。本文作成時に公式本文を確認。App Server全体を実験的とは断定せず安定版/実験的APIを区別。
- 計測: 共通準備票02-AI相談を確認。既存タグ維持、新規Google設定なし。canonical・サイトマップを検証。
- GBP: 既存記録で当事業のプロフィールID・管理接続は未確認。今回の依頼は本記事のサイト公開。別媒体への投稿なし。
- このコミット時点では公開前。PR・統合・デプロイ・HTTP/実画面結果は公開元 tmp/delivery/20261009-codex-workers-ai-blog と本記録へ追記する。

