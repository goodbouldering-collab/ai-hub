# AI相談の現在地

最終更新: 2026-10-11

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。


## ニュースをブログ直下へ（2026-10-11、ローカル検証済み）

- 「今日のAIニュース5とCodex」をブログ直下へ移動。見出し、一覧の文字、区切り線、緑の「もっと見る」をブログと統一。本文・更新日・リンク・日次生成を保持。
- Python34件・Cloudflare7件と既存公開検査が成功。候補600資産中、変更はindex.htmlのみ。599資産・Workerと、ニュース・ブログのHTML内容を保持。
- アプリ内ブラウザでPC1440px/スマートフォン390px、横はみ出しなし、ニュース5件とCodexへの遷移を確認。既存事業Chromeは再接続が応答しないため代替を使用。
- 公開前。次はPR統合、登録元から確定SHAで再生成、公開先ガード、Cloudflare公開、本番確認。記録: [配置変更](docs/news-below-blog-20261011.md)。

## SEO・MEO整備（2026-10-11、独立事業へ修正・公開前）

- 本人回答でAI相談はクライミングコンサルとは独立した別事業と確定。前回の同一事業判断は失効した。JSON-LDの親組織関係と運営組織を除去し、llmsの運営元をAI相談、ホームの運営表記を「AI相談（彦根）」へ修正。住所・講師・連絡先・既存料金・画像・管理機能は保持する。
- 承認済みアカウントへのSearch Console所有権追加と確認タグ公開は本人承認済み。確認タグを実装・ローカル検証済みだが、本番公開・Googleの所有権確認・サイトマップ送信は未完了。確認済みと混同しない。
- ローカル候補は600資産。現行公開r2との差分48件は公開47 HTMLの独立事業情報と確認タグ、llms.txtに限定。本文変更はホームの運営表記1箇所だけ。その他552資産、robots/sitemap/llms-full、Workerは同一。Python55件・Cloudflare7件・管理Worker4件・構成チェック成功。
- 既存Googleビジネス「クライミングコンサル」へ前回追加したAI相談情報の復元は本人承認済みで、UI作業中。新規AI相談GBPは、実住所・看板・来店対応または訪問の実態の本人回答待ち。重複プロフィールや架空情報を作らない。
- 現行公開はPR #133〜#135のSHA `364d7d0ee00d5aa64e8be191e471b807bb653812`、Cloudflare version `1561c92a-22d9-4e35-8cff-4331b94f64d5`、登録元 `.search-presence-release-20261011-r2-final`。旧受講資料URLの503修正と不完全なReview指定の除去は保持する。前回の有効5件・重大エラー0件というGoogle検査は独立事業修正前の結果で、今回版は公開後に確認する。
- 次は今回の変更を統合SHAから登録公開元へ生成・公開し、47正規URLとGSCタグを確認後、所有権確認・サイトマップ送信を実行する。Wikidataは一致する項目と独立した出典が未確認のため新設やsameAs追加を行わない。詳細: [独立事業の修正記録](docs/independent-ai-search-20261011/README.md)、[前回の公開記録](docs/seo-meo-20261011/README.md)。工程記録は `tmp/delivery/20261011-independent-ai-search.json`。

## 最新の公開状態（2026-10-11）

- 案内画像21点を落ち着いた写実表現へ刷新。トップの診断を「あなたのAI実力を試す」「サイトのAI対応を調べる」の2ボタンへ集約し、ブログ最新3件の引用を除去。ブログ一覧10記事の要約は保持。
- 管理を「ホーム／制作・発信／内部資料／運営・分析」の4区分へ整理。内部手順書3件の検索・閲覧・Markdown保存を追加。既存認証・API・キー保存・編集画面は継続。
- PR #131、公開SHA `c76e9014a2a1f5069398218c13ac495c02fe0d94`。Cloudflare version `b315aad6-7bf5-4345-9baf-68d767a77045`、100%配信。Node24.15.0／esbuild0.25.12／Wrangler4.143.1。
- Python44件・管理Worker4件・Cloudflare7件成功。確定Git blob38入力から再生成し、bundleの再ビルド一致、中央ForDeployガード成功。公開HTML2件変更・画像21件追加・575資産不変。別作業16ファイルと既存ステージ差分を保全。
- 本番29資産のSHA一致、認証必須7経路、health200・login200を確認。既存AI相談ChromeでPC1440px/iPhone390pxの画像・ブログ・2診断のクリック遷移・モバイルメニューを確認。横はみ出しなし。
- 管理ホーム・制作・資料検索と本文はローカル仮認証で表示確認。本番の保存済みログイン候補がないため、本人ログイン後の画面確認だけ未完了。工程記録は `DELIVERY_INCOMPLETE`。次は本番 `/admin/login` でログインし、4メニューと資料検索/保存を確認する。認証変更・実キー保存・外部生成・投稿はしていない。
- 画像刷新時の保存基準は登録元 `.cool-editorial-release-20261011-final/public` と `verification.json`。現行のSEO反映済み基準は上記SEO記録を参照。公開Workerは `deployment/admin-workspace/published-worker.mjs`。日次生成は今回の新baselineを確認して使い、旧Workerや未公開JPC差分を混ぜない。
- 詳細: [制作・検証・公開記録](docs/cool-editorial-20261011/README.md)。証拠は登録元 `tmp/delivery/20261011-cool-editorial-images/`。プレビュー http://127.0.0.1:4034/、親PID26088、10月13日12:34:17 JST終了予定。管理はローカル仮認証。
- 10月11日のAIニュース5件・Codex0.162.1記事・講習料金/申込先・実績/本人写真を保持。日次記事の根拠は[日次記録](docs/daily-news-20261011-run.md)、旧画像制作は[履歴](docs/home-editorial-20261011/README.md)。

## 継続する作業と過去の記録

- 管理画面のmyblog/myreel制作とAPIキー保存はPR #117/#118で公開済み。本人ログイン後の実キー保存・再訪・生成は未検証のまま保持する。
- 日次処理はPCとCodexアプリの既存処理を継続する。別のGitHub定期ジョブは再開しない。
- 最新記事「その資料、毎回添付していませんか？」はPR #115で公開・検証済み。[記事公開記録](docs/blog/2026-10-09-codex-workers-ai/README.md)へ詳細を集約。記事制作worktreeはプレビュー親PID 47448（10月11日13:08:01 JST終了予定）と証拠のため保持中。
- 6記事のリール末尾移動はPR #111で公開・実画面確認済み。記録は `work/genspark-profile-edit/tmp/delivery/20261009-blog-reels-last.json`。`work/blog-reels-last-20261009` は証拠と別作業のAGENTS.md差分があるため整理保留。
- 前回の日次プレビューは http://127.0.0.1:4027/ 、親PID 49588、10月13日00:24:30 JST終了予定。旧4026は比較用に保持。ルートと登録公開元の別作業差分・ステージ済み変更は保全した。

<!-- browser-continuity-present:2026-10-09 -->
## 共通ブラウザ運用

- 適用版: `browser-continuity:2026-10-09`。HOME共通原本と [ブラウザ手順](C:/Project/docs/browser-account-policy.md) を参照する。
- 変更点: Chrome自体のログイン・同期は不要。確認済みの事業用デスクトップショートカットを優先し、Computer Useの一時障害でも許可済みの公開調査・制作・検証は続行する。myblogの制作中の案は、選択待ち指定がなければ推奨案を採用する。
- 検証・公開状況: HOMEとSkillのローカル反映・Skill構文検証済み。共通設定のGitHub配布は `C:/Project/codex-config/Present.md` を参照。今回のサイト変更の本番・画面確認は上記の公開状態と制作記録を参照。SNS投稿は実施していない。
- 残件・次の作業: サービスアカウント確認、未承認の最終投稿内容の公開承認は維持する。次回の依頼で既存ショートカット対応を使い、実際の操作結果と残件を記録する。
<!-- /browser-continuity-present:2026-10-09 -->
