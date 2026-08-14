# Cron ジョブ一覧（全プロジェクト横断・2026-05-13 時点）

このリポジトリ群で動いている全ての定期実行ジョブの一元台帳。
ダッシュボードを 2 つ（Vercel / GitHub）跨ぐ手間を、この 1 ファイルで埋める。

ジョブ追加/削除時は **必ずここを更新**する（PR 単位の更新は CEO 承認不要・Claude が反映する）。

---

## サマリ（2026-05-25 更新）

- **GitHub Actions cron**: 4 件
- **Vercel Cron**: 2 件
- **合計**: 6 件

---

## Vercel Cron

### 1. ビジネス21 / legal-crawl

| 項目 | 値 |
|---|---|
| **プロジェクト** | ビジネス21 |
| **定義場所** | [ビジネス21/vercel.json](ビジネス21/vercel.json) の `crons[0]` |
| **エンドポイント** | `/api/cron/legal-crawl` |
| **スケジュール (UTC)** | `0 21 * * *` |
| **JST 実行時刻** | 毎日 06:00 |
| **用途** | 法令情報のクロール（監理団体業務に必要な行政情報の更新確認） |
| **認証** | `CRON_SECRET` Bearer 必須 |
| **ダッシュボード** | https://vercel.com/goodboulderings-projects/business21/settings/cron-jobs |

### 2. みんなのWA / send-event-registration-mails

| 項目 | 値 |
|---|---|
| **プロジェクト** | みんなのWA |
| **定義場所** | [みんなのWA/vercel.json](みんなのWA/vercel.json) の `crons[0]` |
| **エンドポイント** | `/api/cron/send-event-registration-mails` |
| **スケジュール (UTC)** | `0 12 * * *` |
| **JST 実行時刻** | 毎日 21:00 |
| **用途** | 当日開催イベントのゲスト参加者に「本登録案内メール」を Resend で一斉送信 |
| **対象抽出** | `ev.date === today (JST)` の各イベント → `ev.registrations[*]` で `member.isGuest === true` かつ `regDetails[memberId].registrationMailSent !== true` のメンバー |
| **副作用** | `ev.regDetails[memberId].registrationMailSent = true` / `.registrationMailSentAt = ISO` を Supabase に書き戻して重複送信防止 |
| **認証** | `CRON_SECRET` Bearer 必須（Vercel CLI で登録済み・2026-05-13） |
| **ダッシュボード** | https://vercel.com/goodboulderings-projects/minanowa/settings/cron-jobs |

---

## GitHub Actions cron

### 3. ai-hub / AI トレンド記事収集 (daily.yml)

| 項目 | 値 |
|---|---|
| **プロジェクト** | ai-hub |
| **定義場所** | [ai-hub/.github/workflows/daily.yml](ai-hub/.github/workflows/daily.yml) |
| **スケジュール (UTC)** | `0 22 * * *`（毎日）+ `0 0 * * 1`（月曜・週次フル版） |
| **JST 実行時刻** | 毎日 07:00 + 月曜 09:00 |
| **言語** | Python (`run.py`) |
| **用途** | RSS / 各種 AI ニュースソースをクロール → NotebookLM 用 Markdown と outputs/ を生成 → main にコミット back |
| **手動実行** | `workflow_dispatch` 対応・mode 選択肢: `diff` / `full` |
| **必要 Secret** | `ANTHROPIC_API_KEY` |
| **ダッシュボード** | https://github.com/goodbouldering-collab/ai-hub/actions/workflows/daily.yml |
| **Vercel 移行可否** | ❌ Python ＋ git commit back のため Vercel Functions では実装不可 |

### 4. ai-hub / consul docs 同期 (sync-consul-docs.yml)

| 項目 | 値 |
|---|---|
| **プロジェクト** | ai-hub |
| **定義場所** | [ai-hub/.github/workflows/sync-consul-docs.yml](ai-hub/.github/workflows/sync-consul-docs.yml) |
| **スケジュール (UTC)** | `0 21 * * *` |
| **JST 実行時刻** | 毎日 06:00 |
| **用途** | プライベートリポ `consul` を fetch → `ai-hub/content/consul-work/*.md` に上書き → ai-hub に commit + push |
| **目的** | `https://aiclimb.vercel.app/admin/docs` から経営本部ドキュメントを Basic 認証下で閲覧可能にする |
| **手動実行** | `workflow_dispatch` 対応 |
| **必要 Secret** | `CONSUL_REPO_PAT`（consul プライベートリポへの read 権限を持つ PAT） |
| **ダッシュボード** | https://github.com/goodbouldering-collab/ai-hub/actions/workflows/sync-consul-docs.yml |
| **Vercel 移行可否** | ❌ Vercel Functions から `git push` できないため |

### 5. ビジネス21 / Supabase 週次バックアップ (supabase-backup.yml)

| 項目 | 値 |
|---|---|
| **プロジェクト** | ビジネス21 |
| **定義場所** | [ビジネス21/.github/workflows/supabase-backup.yml](ビジネス21/.github/workflows/supabase-backup.yml) |
| **スケジュール (UTC)** | `0 18 * * 0` |
| **JST 実行時刻** | 毎週月曜 03:00 |
| **言語** | Python（bash 引数解析事故を避けるためインライン Python） |
| **用途** | 監理団体本番 DB の全テーブルを Supabase REST API で SELECT * → JSON ダンプ |
| **保存先** | GitHub Artifact（90 日無料保持） |
| **失敗時** | リポに Issue 自動作成（`permissions.issues: write`） |
| **必要 Secret** | `SUPABASE_SERVICE_ROLE_KEY` |
| **ダッシュボード** | https://github.com/goodbouldering-collab/business21/actions/workflows/supabase-backup.yml |
| **Vercel 移行可否** | 🟡 技術的には可能だが、Artifact 90 日無料の利点を失うので非推奨 |

### 6. consul / SEO週次ダイジェスト (seo-weekly.yml)

| 項目 | 値 |
|---|---|
| **プロジェクト** | consul（google_ops 基盤） |
| **定義場所** | [consul/.github/workflows/seo-weekly.yml](consul/.github/workflows/seo-weekly.yml) → `weekly_seo_digest.py` |
| **スケジュール (UTC)** | `0 23 * * 0` |
| **JST 実行時刻** | 毎週月曜 08:00 |
| **言語** | Python |
| **用途** | 全GSCプロパティの直近28日 vs 前28日を比較→ダイジェストを `work/<日付>-seo-weekly-digest.md` に生成→[REPORTS-HUB.md](REPORTS-HUB.md) 更新→commit |
| **報告** | 生成MDは [REPORTS-HUB.md](REPORTS-HUB.md) に集約・ai-hub `/admin/docs` にも自動同期。🔴悪化があればClaudeが深掘り |
| **手動実行** | `workflow_dispatch` 対応 |
| **失敗時** | Issue 自動作成（トークン失効・Secret不正を検知） |
| **必要 Secret** | `GOOGLE_OAUTH_CREDENTIALS`（credentials.json中身）/ `GSC_TOKEN_GOODBOULDERING`（**本番公開後の無期限トークン**） |
| **ダッシュボード** | https://github.com/goodbouldering-collab/consul/actions/workflows/seo-weekly.yml |
| **Vercel 移行可否** | ❌ Python＋git commit back のため Vercel Functions 不可 |

> ⚠️ 前提: OAuth同意画面を「本番環境」に公開しないとトークンが7日で失効し失敗する。
> 当初ローカル(Windowsタスク)案だったが「Windows管理しにくい」によりGH Actionsへ切替（2026-05-25 CEO判断）。

---

## 運用ルール

1. **新規 cron 追加時のチェック**: 親 [CLAUDE.md](CLAUDE.md) の「Cron ジョブの選定」セクションのフローチャートで Vercel / GitHub Actions を決める
2. **追加・削除したらこのファイルを更新**: 表に行を追加・該当行を削除
3. **Secret 漏洩防止**: `CRON_SECRET` や PAT を commit に含めない。Vercel CLI / GitHub Settings 経由で登録
4. **失敗時通知**: GitHub Actions は Issue 自動作成、Vercel Cron は Vercel ダッシュボード手動確認（将来 Slack/Discord webhook を仕掛ける余地あり）
5. **本番実行確認**: 主要 cron は手動 Run Now で半年に 1 回は健全性確認

---

## 過去の検討記録

- **2026-05-13**: CEO「Vercel Cron に全部まとめたい」相談 → コスト・移行工数の試算で「現状維持」判定。詳細は親 [CLAUDE.md](CLAUDE.md) 「すべて統一の罠」セクション参照
