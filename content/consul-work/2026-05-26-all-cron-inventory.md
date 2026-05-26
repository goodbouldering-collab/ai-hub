# 全 cron 一覧表（正本）

最終更新: 2026-05-26
方針: **GitHub Actions 一元化**（親 `CLAUDE.md`「Cron ジョブの選定」セクション参照）。Vercel Cron は 3 条件 AND を満たす例外のみ。

ダッシュボードを跨がず 1 枚で全 cron を把握するための正本。新規追加・削除・スケジュール変更時はこの表を必ず更新する。

## 稼働中 cron（全 6 本・すべて GitHub Actions）

Vercel Cron は **現在 0 本**（`vercel.json` の `crons[]` を持つプロジェクトなし）。

| # | 事業 | ジョブ名 | ファイル | cron式(UTC) | JST | 内容 | 性質 |
|---|---|---|---|---|---|---|---|
| 1 | AIハブ | AIハブ daily digest（日次） | `ai-hub/.github/workflows/daily.yml` | `0 22 * * *` | 毎日 07:00 | 日次ダイジェスト生成 | Python・git push back |
| 2 | AIハブ | AIハブ daily digest（週次モード） | 同上（同ファイル内 2nd schedule） | `0 0 * * 1` | 毎週月 09:00 | 週次モード切替 | 同上 |
| 3 | AIハブ | Sync consul docs | `ai-hub/.github/workflows/sync-consul-docs.yml` | `0 21 * * *` | 毎日 06:00 | consul の work/ を ai-hub へ同期 | git clone/push（リポ間同期） |
| 4 | consul | SEO週次ダイジェスト | `consul/.github/workflows/seo-weekly.yml` | `0 23 * * 0` | 毎週日 08:00 | GSC/GA4 の SEO レポート生成 | Python・git push back |
| 5 | グッぼる | 本店シューズ自動スクレイピング | `グッぼる/クライミングシューズサーチ/.github/workflows/scrape-store.yml` | `30 15 28 * *` | 毎月28日 翌0:30 | 本店シューズ一覧を月次取得（EUC-JP変換） | Node・git commit/push |
| 6 | ビジネス21 | Supabase Weekly Backup (b21) | `ビジネス21/.github/workflows/supabase-backup.yml` | `0 18 * * 0` | 毎週月 03:00 | DB 全テーブルをバックアップ | pg_dump 相当・Artifact 保管 |

> #1・#2 は同一 `daily.yml` 内の 2 スケジュール（日次 + 週次切替）。実体ファイル数は 5。

## Vercel Cron で動かせない理由（移行可能率 0/6 = 0%）

6 本すべてが「Python」または「git push back」または「pg_dump/Artifact」に該当し、Vercel Functions（Node 専用・FS 読み取り専用・実行 300 秒上限）では物理的に動かない。これが GitHub Actions 一元化の数字根拠。

## 停止済み・残骸

- `.github/workflows/render-keepalive.yml`（親リポ）: Render 完全撤退に伴い **cron 停止済み**（`workflow_dispatch` のみ残存）。Render 上にサービスは 0 件。**ファイル自体は削除候補**（紛らわしいため・要 CEO 判断）。

## デプロイ系 workflow（cron ではない・参考）

`schedule:` を持たず push トリガーで動くもの（cron 一覧には含めない）:
- `N-デザイン/.github/workflows/ci.yml`、`Notエステ/web/.github/workflows/ci.yml`、`ビジネス21/.github/workflows/{deploy,kanri-ci}.yml`
- `Notエステ/line-crm/.../deploy-worker.yml`、`グッぼる/line-crm/.../deploy-worker.yml`（Cloudflare Workers デプロイ）
- `ai-hub/.github/workflows/pages.yml`

## 将来の追加候補

- **メディアキットのバナー自動生成**（7 本目候補）: `@napi-rs/canvas` ネイティブビルド + PNG 成果物 push → **GitHub Actions**（FS read-only で Vercel 不可）。ただし律速は「課題定義 JSON を誰が書くか」。入力が自動化できないと生成だけ自動化しても価値が薄い（未着手）。

## Vercel に寄せ直す再評価トリガー

T1: DB 同居・push 不要の Node cron が 3 本以上たまった（最も現実的）／ T2: GHA プライベート枠 2000 分/月を恒常超過 ／ T3: GHA ランナー起動の DB レイテンシが SLA を割った ／ T4: Vercel が永続 FS/git 連携を提供。いずれも未到達 → Vercel Cron は 0 本維持。
