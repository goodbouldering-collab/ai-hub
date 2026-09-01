# 📊 報告ハブ（全自動ジョブ・定期診断の一元窓口）

**これが報告の一本化された窓口。** 各ジョブの「最終実行・結果・要点」をここだけ見れば把握できる。
consul/work/ に置いているので、毎日 `sync-consul-docs.yml` で **ai-hub の `/admin/docs` に自動同期** され、ブラウザでも閲覧可能。

- 各ジョブの詳細仕様・スケジュールは [2026-05-13-cron-jobs-overview.md](2026-05-13-cron-jobs-overview.md)（台帳）
- ジョブは**全部稼働継続**（このハブは報告を集約するだけ・ジョブは止めない）
- 更新ルール: ジョブが走って結果が出たら、該当行の「最終実行」「結果」を Claude が更新する

最終更新: 2026-08-31

---

## 定期ジョブの稼働状況

| # | ジョブ | 種別 | 頻度 | 最終実行 | 結果 | 詳細リンク |
|---|---|---|---|---|---|---|
| 1 | ビジネス21 法令クロール | Vercel | 毎日06:00 | （未記録） | — | 台帳#1 |
| 2 | みんなのWA 本登録メール | Vercel | 毎日21:00 | （未記録） | — | 台帳#2 |
| 3 | ai-hub AIトレンド記事収集 | GH Actions | 毎日07:00+月曜 | （未記録） | — | 台帳#3 |
| 4 | ai-hub consul docs同期 | GH Actions | 毎日06:00 | （未記録） | — | 台帳#4 |
| 5 | ビジネス21 Supabaseバックアップ | GH Actions | 毎週月03:00 | （未記録） | — | 台帳#5 |
| 6 | **consul SEO週次ダイジェスト** | GH Actions | 週1（月曜08:00） | 2026-08-31 | 🔴 goodbouldering +1.1悪化 | 下記 |

> 「最終実行」が（未記録）のものは、次にそのジョブの結果を確認したタイミングで Claude が埋める。
> Vercel/GH Actions のジョブは各ダッシュボードが一次情報。ここはその要約を集める二次台帳。

---

## 🔍 SEO週次ダイジェスト（最新）

最新の生データ: [2026-08-31-seo-weekly-digest.md](2026-08-31-seo-weekly-digest.md)

| プロパティ | 平均順位(前→今) | 判定 |
|---|---|---|
| goodbouldering.com（グッぼる） | 5.24 → 6.35 | 🔴悪化 +1.1 |
| plogging.jp（プロギング） | 4.64 → 5.36 | 🔴悪化 +0.72 |
| blog.goodbouldering.com | 44.3 → 28.5 | 🟢改善 -15.8 |
| mokshajapan.jp | 3.94 → 4.24 | ➡️微悪化 +0.3 |
| notesthe.com（Notエステ） | 5.54 → 5.27 | ➡️横ばい |

**現在の最重要トピック**: グッぼる&プロギングが **Googleコアアップデート(3月+5月)で被弾**。
- 確定診断: [2026-05-25-gubble-seo-api-diagnosis-confirmed.md](2026-05-25-gubble-seo-api-diagnosis-confirmed.md)
- 回復対策①②: [2026-05-25-gubble-seo-recovery-actions.md](2026-05-25-gubble-seo-recovery-actions.md)
- 次の観測ポイント: 5/21〜の5月コアアップデート完了後、および対策実施後の回復

---

## ⚠️ 運用上の未完事項

- [ ] **OAuth本番公開**: SEO週次ジョブはテストモードだとトークンが7日で失効。CEOがGCPで「アプリを公開」を1回実施（→公開後にClaudeが無期限トークン再取得）
- [ ] **GitHub Secrets登録**: 公開後の無期限トークンを `GSC_TOKEN_GOODBOULDERING`、`credentials.json`中身を `GOOGLE_OAUTH_CREDENTIALS` として consul リポに登録 → seo-weekly.yml が稼働開始
- [ ] lossismore アカウントの認可（任意・CEO個人プロパティを見る場合）
