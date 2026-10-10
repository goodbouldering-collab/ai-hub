# AI相談の現在地

最終更新: 2026-10-11

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。

## 最新の公開状態（2026-10-11）

- 10月11日版AIニュース5件を公開。直近48時間の公式5発表元・5URLを確認。Codex CLI 0.162.1と公式fingerprintは前回と同一のため、記事本文・10月10日の更新日を保持。
- ニュース入口はヒーロー直下の最新3見出しと「もっと見る」→ /ai-news/。ブログは画像付き最新3件、一覧は既存公開10記事のみ。独立ニュースをブログへ再掲載しない。
- 人物入りイラスト21点・講習6カードの最新デザイン、講習本文・料金・申込先、記事本文、既存Worker/APIを保持。公開差分4資産、573資産不変。
- PR #129、公開SHA `0057d83a4220fcfd5a9dd5144c52cf8ca127a1d4`。Cloudflare version `171fa478-0163-4d13-bf20-1c7993c111e3`、Wrangler 4.143.1、100%配信。
- 68テスト、assets、中央ForDeploy、統合SHAの確定入力53ファイルから577資産再生成に成功。本番33資産のSHA一致、旧3URL301、/health・/admin 200、保護API401、Worker etag・binding・runtime不変。
- 実在する `AI相談 - Chrome.lnk`（Profile 1）で本番を確認。PC1440px/iPhone390pxのトップと独立ページ、もっと見る遷移、横はみ出しなし。ブログ一覧10記事と除外も確認。
- 次回の公開基準は登録元 `.daily-news-release-20261011-final/public` とverification.json/production-summary.json。未公開のJPC・Worker差分を避け、統合Git blobから抽出したsource snapshotで再生成した。
- Web工程は文書更新前に `DELIVERY_VERIFIED`。[日次記録](docs/daily-news-20261011-run.md)、`outputs/daily-20261011/production-summary.json`を参照。デザインの制作履歴は[画像制作記録](docs/home-editorial-20261011/README.md)。

## 継続する作業と過去の記録

- 管理画面のmyblog/myreel制作とAPIキー保存はPR #117/#118で公開済み。本人ログイン後の実キー保存・再訪・生成は未検証のまま保持する。
- 日次処理はPCとCodexアプリの既存処理を継続する。別のGitHub定期ジョブは再開しない。
- 最新記事「その資料、毎回添付していませんか？」はPR #115で公開・検証済み。[記事公開記録](docs/blog/2026-10-09-codex-workers-ai/README.md)へ詳細を集約。記事制作worktreeはプレビュー親PID 47448（10月11日13:08:01 JST終了予定）と証拠のため保持中。
- 6記事のリール末尾移動はPR #111で公開・実画面確認済み。記録は `work/genspark-profile-edit/tmp/delivery/20261009-blog-reels-last.json`。`work/blog-reels-last-20261009` は証拠と別作業のAGENTS.md差分があるため整理保留。
- 今回のプレビューは http://127.0.0.1:4027/ 、親PID 49588、10月13日00:24:30 JST終了予定。旧4026は比較用に保持。ルートと登録公開元の別作業差分・ステージ済み変更は保全した。

<!-- browser-continuity-present:2026-10-09 -->
## 共通ブラウザ運用

- 適用版: `browser-continuity:2026-10-09`。HOME共通原本と [ブラウザ手順](C:/Project/docs/browser-account-policy.md) を参照する。
- 変更点: Chrome自体のログイン・同期は不要。確認済みの事業用デスクトップショートカットを優先し、Computer Useの一時障害でも許可済みの公開調査・制作・検証は続行する。myblogの制作中の案は、選択待ち指定がなければ推奨案を採用する。
- 検証・公開状況: HOMEとSkillのローカル反映・Skill構文検証済み。共通設定のGitHub配布は `C:/Project/codex-config/Present.md` を参照。今回のサイト変更の本番・画面確認は上記の公開状態と制作記録を参照。SNS投稿は実施していない。
- 残件・次の作業: サービスアカウント確認、未承認の最終投稿内容の公開承認は維持する。次回の依頼で既存ショートカット対応を使い、実際の操作結果と残件を記録する。
<!-- /browser-continuity-present:2026-10-09 -->
