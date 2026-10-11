# 2026-10-12 AIニュース・Codex監視

状態: ローカル検証済み、PR統合・公開前。

- 調査: 日本時間10月10日朝〜12日朝を優先。5件不足で10月5日朝からの7日間まで拡大し、公式5発表元の10月8〜9日発表を選定。正本JSONに全出典と発表日。本文・日付・HTTP200を確認。Microsoft本文は10月9日表示、公開メタデータは10月10日UTCで差異があり、publishedは本文表示を採用。
- Codex: 公式whats-newと最新安定版を検証済みfetchで照合。October 5–9, 2026／rust-v0.162.1、fingerprintは証拠 `outputs/daily-20261012/codex-check.json` と一致。差分なしで記事全バイト保持。
- 基準: `.glass-hero-release-20261012-final/public`。614manifest・本番7SHA一致。候補は3資産変更・611保持。トップはニュースと専用CSS以外のDOMが一致、ブログはバイト一致。管理Worker SHA256 `644f3ee74fc80f7bb4e59fd08816a51da64beb901b719f1c13b953e72f87cdd3` を維持。
- ソース: 最新登録元HEADから隔離sparse worktree。全checkoutは容量不足で失敗したため、新規失敗コピーのみ整理して必要ソースへ限定。不変の画像・動画をhardlink、テキストを独立コピーして再生成。既存dirty・stagedを保持。
- Vercel: committed policy disconnected、GitHub hooks空、公開経路検査PASS。Vercel・SNS・メール・課金・認証・DNS・別定期処理は変更しない。codex/codex-automationラベルは存在しない。
- Jev: 自動承認レビューが内部差分の外部送信を拒否。送信せずローカル検証・構造比較・ハッシュ照合で代替。
- 証拠: 登録元 `outputs/daily-20261012/` と `tmp/delivery/20261012-daily-ai-news.json`。実行helperは事業ルート `outputs/daily-20261012/`。
