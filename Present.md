# AI相談の現在地

最終更新: 2026-10-11

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。

## 今回の表示変更（2026-10-11・公開準備）

- トップのブログとCodex情報を画像左・本文右の3件リストへ統合。「もっと見る」から公開10記事とCodex情報の全11件へ進む。
- 人物入りの立体イラスト21点へ説明画像を刷新。講習6カードを短くし、本文・料金・詳細・申込先は保持。
- ローカル34テスト、内容保持、PC1440px・スマートフォン390/360pxの表示と操作を確認済み。commit・PR統合・本番反映はこの時点では未実施。
- [制作・検証記録](docs/home-editorial-20261011/README.md)。公開後にSHA・Cloudflare版・本番検証結果を更新する。

## 最新の公開状態（2026-10-10）

- トップのブログを9月30日の「日付＋記事名」の最新2件リストへ復元。10月9日・10月5日の記事を掲載し、記事本文・画像・講習欄は維持した。日次生成にも反映済み。
- PR #122を統合、公開SHA `458a3485aad3219dcb206626ba1e7523a77c3f80`。Cloudflare version `7dac22b6-8810-45ef-9f95-9756fac79763`、Wrangler 4.143.1、100%配信。
- 変更はトップ1ファイル、他555ファイルとWorkerは不変。18テスト・公開先ガード・本番16資産の照合が成功。PC 1440px／スマートフォン390pxで表示、メニュー、記事・一覧への遷移を確認した。
- 公開画面確認にはCodex内ブラウザを使用。実在する「AI相談 - Chrome.lnk」はProfile 1だが接続なし。ネイティブ起動が利用できず、同Profileでの確認は未実施。
- 次回の公開基準は登録公開元 `.home-blog-text-list-release-20261010/public` と `verification.json`。直前のdaily版は入力証拠として保持し、最新本番と混同しない。
- 詳細と検証証拠: [ブログ表示復元記録](docs/home-blog-list-restore-20261010.md)。工程は後続の文書更新前に `DELIVERY_VERIFIED`。

## 継続する作業と過去の記録

- 管理画面のmyblog/myreel制作とAPIキー保存はPR #117/#118で公開済み。本人ログイン後の実キー保存・再訪・生成は未検証のまま保持する。
- 10月10日版AIニュース5件・Codex CLI 0.162.1は公開済みで、今回も内容を維持。[日次記録](docs/daily-news-20261010-run.md)、`outputs/daily-20261010/production-summary.json` を参照。PCとCodexアプリの既存処理を継続し、別のGitHub定期ジョブは再開しない。
- 最新記事「その資料、毎回添付していませんか？」はPR #115で公開・検証済み。[記事公開記録](docs/blog/2026-10-09-codex-workers-ai/README.md)へ詳細を集約。記事制作worktreeはプレビュー親PID 47448（10月11日13:08:01 JST終了予定）と証拠のため保持中。
- 6記事のリール末尾移動はPR #111で公開・実画面確認済み。記録は `work/genspark-profile-edit/tmp/delivery/20261009-blog-reels-last.json`。`work/blog-reels-last-20261009` は証拠と別作業のAGENTS.md差分があるため整理保留。
- 今回のプレビューは http://127.0.0.1:4026/ 、親PID 21164、10月12日22:48:02 JST終了予定。ルートと登録公開元の別作業差分は保全した。

<!-- browser-continuity-present:2026-10-09 -->
## 共通ブラウザ運用

- 適用版: `browser-continuity:2026-10-09`。HOME共通原本と [ブラウザ手順](C:/Project/docs/browser-account-policy.md) を参照する。
- 変更点: Chrome自体のログイン・同期は不要。確認済みの事業用デスクトップショートカットを優先し、Computer Useの一時障害でも許可済みの公開調査・制作・検証は続行する。myblogの制作中の案は、選択待ち指定がなければ推奨案を採用する。
- 検証・公開状況: HOMEとSkillのローカル反映・Skill構文検証済み。共通設定のGitHub配布は `C:/Project/codex-config/Present.md` を参照。本事業のブラウザ実操作・投稿・本番デプロイは今回実施していない。
- 残件・次の作業: サービスアカウント確認、未承認の最終投稿内容の公開承認は維持する。次回の依頼で既存ショートカット対応を使い、実際の操作結果と残件を記録する。
<!-- /browser-continuity-present:2026-10-09 -->
