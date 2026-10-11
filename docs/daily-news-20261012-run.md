# 2026-10-12 AIニュース・Codex監視

状態: PR統合・Cloudflare公開・本番画面確認済み。今回の公開残件なし。

- 調査: 日本時間10月10日朝〜12日朝を優先。5件不足で10月5日朝からの7日間まで拡大し、公式5発表元の10月8〜9日発表を選定。正本JSONに全出典と発表日。本文・日付・HTTP200を確認。Microsoft本文は10月9日表示、公開メタデータは10月10日UTCで差異があり、publishedは本文表示を採用。
- Codex: 公式whats-newと最新安定版を検証済みfetchで照合。October 5–9, 2026／rust-v0.162.1、fingerprintは証拠 `outputs/daily-20261012/codex-check.json` と一致。差分なしで記事全バイト保持。
- 基準: `.glass-hero-release-20261012-final/public`。614manifest・本番7SHA一致。候補は3資産変更・611保持。トップはニュースと専用CSS以外のDOMが一致、ブログはバイト一致。管理Worker SHA256 `644f3ee74fc80f7bb4e59fd08816a51da64beb901b719f1c13b953e72f87cdd3` を維持。
- ソース: 最新登録元HEADから隔離sparse worktree。全checkoutは容量不足で失敗したため、新規失敗コピーのみ整理して必要ソースへ限定。不変の画像・動画をhardlink、テキストを独立コピーして再生成。既存dirty・stagedを保持。
- Vercel: committed policy disconnected、GitHub hooks空、公開経路検査PASS。Vercel・SNS・メール・課金・認証・DNS・別定期処理は変更しない。codex/codex-automationラベルは存在しない。
- Jev: 自動承認レビューが内部差分の外部送信を拒否。送信せずローカル検証・構造比較・ハッシュ照合で代替。
- 証拠: 登録元 `outputs/daily-20261012/` と `tmp/delivery/20261012-daily-ai-news.json`。実行helperは事業ルート `outputs/daily-20261012/`。

## 公開結果

- ソースcommit `206cbe79132d2aa6301bf77ab95013a9c4264c22`、[PR #164](https://github.com/goodbouldering-collab/ai-hub/pull/164)、統合・公開SHA `aabd608d0bddc2f7579b06c975b9c9df12521736`。2件の公開先チェック成功後に統合。
- 確定Git blob67入力から `.daily-news-release-20261012-verified/` に再生成。614資産が検証候補と一致。中央ガード・dry-run・直前version確認後、登録runtimeから公開。version `7b1ae6b0-90d6-4ada-a16c-122fe0acf5d8`、配信100%。Worker resources（etag・binding・runtime）完全一致。
- 日次・Codex・画像・配置の53テスト、assets/live検証、主要8資産の本番SHA一致。旧Codex URL3形式は301、healthと旧ブログ200、管理入口200（ログインへ遷移後）、未認証管理API401。
- 既存AI相談Chrome（browser 3）を使用。古いタブ参照の接続不良後、同じ事業ブラウザの確認用タブでPC1440px・スマホ390pxを検証。ヒーロー直下3件、もっと見るから独立ページ5件、同じ大見出し書式、目次なし、7講座、横はみ出しなし。4スクリーンショットを保存。
- `delivery-status.mjs check` はDELIVERY_VERIFIED。公開直後に一度走ったlive検査はアップロード完了前の旧版を取得したため不一致、デプロイ完了後の再検査で成功。最初のCRLF候補比較に失敗した `.daily-news-release-20261012-final` は採用しない。
- 次回正常版は `.daily-news-release-20261012-verified/public`。同ディレクトリのverification.jsonとproduction-summary.json、最新本番を照合する。今回の記録更新だけではサイトを再デプロイしない。
- Python3.12／Node24.15.0／Wrangler4.90.0。既存のdirty・staged差分を保持し、事業ルートの旧HEADを変更していない。

確認URL: https://aiclimb.aiclimb.workers.dev/ai-news/ 、 https://aiclimb.aiclimb.workers.dev/
