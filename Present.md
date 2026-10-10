# AI相談の現在地

最終更新: 2026-10-11

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。

## 10月11日の日次更新（検証済み・公開前）

- 公式発表5件（10月9日発表）を直近48時間から選定。Codex 0.162.1と公式fingerprintは同一のため記事本文・更新日を保持。
- ニュースはヒーロー直下の最新3見出しと「もっと見る」から独立ページへ。ブログ一覧は公開10記事のみ。最新の人物イラストと講習カードは保持。
- 68テスト、assets、577資産比較、同一Worker dry-run成功。4資産変更・573資産不変。Chrome Profile 1のPC1440/iPhone390幅で候補確認。
- 次の作業はPR統合、統合SHA再生成、中央ガード、Cloudflare公開、本番検証。詳細は [日次記録](docs/daily-news-20261011-run.md)。

## 最新の公開状態（2026-10-11）

- トップのブログとCodex情報を画像左・本文右の3件リストへ統合。「もっと見る」から公開10記事とCodex情報の全11件へ進む。
- 人物入りの立体イラスト21点へ説明画像を刷新。ホーム17箇所に10点、一覧に11点を使用。講習6カードを短くし、本文・料金・詳細・申込先は保持。
- PR #124を統合し、公開SHA `40ce7c95f97e9cfec199543615f59cf958d9f186`。Cloudflare version `3121c0bc-72a6-446f-84bc-28ddb1c2a3a6`、Wrangler 4.143.1、100%配信。
- Python 25件・Worker 9件、公開先ガード、本番35資産のハッシュ照合に成功。変更はトップとブログ一覧、追加21画像。他554資産とWorkerは保持。記事10本も本番で一致を確認。
- Codex内ブラウザでPC1440px・スマートフォン390/360pxを確認。画像と本文の重なり・横はみ出しなし。3件表示、もっと見る→11件、メニュー開閉、講習詳細の全幅展開を確認した。AI相談用Chrome Profile 1は未接続のため共通手順の代替ブラウザを使用。
- 次回の公開基準は登録公開元 `.editorial-release-20261011-final/public` と `verification.json`。直前版 `.home-blog-text-list-release-20261010` は再生成用の固定入力として保持する。
- [制作・公開記録](docs/home-editorial-20261011/README.md)。工程は後続の文書更新前に `DELIVERY_VERIFIED`。前回の文字リスト復元は [10月10日の記録](docs/home-blog-list-restore-20261010.md) を参照。

## 継続する作業と過去の記録

- 管理画面のmyblog/myreel制作とAPIキー保存はPR #117/#118で公開済み。本人ログイン後の実キー保存・再訪・生成は未検証のまま保持する。
- 10月10日版AIニュース5件・Codex CLI 0.162.1は公開済みで、今回も内容を維持。[日次記録](docs/daily-news-20261010-run.md)、`outputs/daily-20261010/production-summary.json` を参照。PCとCodexアプリの既存処理を継続し、別のGitHub定期ジョブは再開しない。
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
