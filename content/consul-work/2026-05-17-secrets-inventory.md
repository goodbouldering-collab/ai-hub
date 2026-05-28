# シークレット台帳（全プロジェクト横断・2026-05-17 時点）

このリポジトリ群で使われている全 API キー・トークン・シークレットの一元台帳。
保管庫が **4 箇所に分散**（Supabase consul-ops / Vercel / GitHub Secrets / ローカル .env）しており、
「どの鍵がどこにあり、いつ失効するか」を 1 ファイルで埋めるのが目的。
[cron 台帳](2026-05-13-cron-jobs-overview.md) と同じ運用方式。

> **絶対ルール**: このファイルに**実際のキー値は書かない**。鍵名・保管場所・発行元・期限・ローテ手順だけ。
> 値が要るときは下表の「保管場所」を直接見る。値をここに転記した時点で台帳が漏洩源になる。

---

## サマリ（2026-05-17 現在）

- **保管庫**: 4 系統（Supabase consul-ops Vault / Vercel Dashboard / GitHub Secrets / ローカル .env・credentials.json）
- **重複している鍵**: `SUPABASE_SERVICE_ROLE_KEY`（3+ 箇所）, `ANTHROPIC_API_KEY`（Vercel + GitHub Secrets）
- **有効期限のある鍵**: `THREADS_ACCESS_TOKEN`（60日）, X トークン群（要再生成）, `CONSUL_REPO_PAT`（classic PAT・期限要確認）
- **要注意**: `CONSUL_REPO_PAT` は 2026-05-13 以降 sync-consul-docs.yml が動いていない疑い（[ai-hub-ops-redesign](2026-05-16-ai-hub-ops-redesign.md) 参照）。期限切れの可能性大

---

## 保管庫の定義

| ID | 保管庫 | 実体 | 読み出し方 |
|---|---|---|---|
| **S** | Supabase `consul-ops` | `oauth_tokens` テーブル（service_role 専用・RLS 有効） | [google_ops/scripts/refresh.py](google_ops/scripts/refresh.py) の `get_credentials()` |
| **V** | Vercel Dashboard | 各プロジェクト Settings > Environment Variables | Vercel CLI / API（`VERCEL_TOKEN`）/ ダッシュボード手動 |
| **G** | GitHub Secrets | 各リポ Settings > Secrets and variables > Actions | Actions ワークフロー内 `${{ secrets.X }}` |
| **L** | ローカル | `consul/google_ops/.env` / `credentials.json` / `~/.codex/auth.json` | PC ローカルのみ・git 管理外 |

---

## シークレット一覧

### consul 本部 / Google API 連携

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| `SUPABASE_SERVICE_ROLE_KEY`（consul-ops） | **L** (`google_ops/.env`) | Supabase Dashboard > Settings > API | 無期限（手動失効まで） | Supabase で rotate → `.env` 更新 |
| Google OAuth トークン（`goodbouldering`） | **S** (`oauth_tokens`) | GCP OAuth 同意画面 | refresh_token 長期・access は自動 refresh | `python google_ops/scripts/authorize.py --account goodbouldering` |
| Google OAuth トークン（`lossismore`） | **S** (`oauth_tokens`) | 同上 | 同上 | `--account lossismore` で再認可 |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | **L** (`credentials.json`) | GCP OAuth クライアント | 無期限 | GCP コンソールで再発行 → credentials.json 差替 |
| `CONSUL_REPO_PAT` | **G** (ai-hub リポ) | GitHub Settings > Developer settings（classic PAT） | ⚠️ **要確認**（classic PAT・失効疑い） | GitHub で再発行 → ai-hub の GitHub Secret 更新（要 CEO） |

### ai-hub（AIハブ）

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| `ANTHROPIC_API_KEY` | **V** + **G** ⚠️重複 | Anthropic Console | 無期限 | Console で rotate → Vercel と GitHub Secret **両方**更新 |
| `OPENAI_API_KEY`（DALL-E 3） | **V** | OpenAI Platform | 無期限 | Platform で rotate → Vercel 更新 |
| `SUPABASE_SERVICE_ROLE_KEY`（ai-hub） | **V** | Supabase（ai-hub プロジェクト） | 無期限 | Supabase rotate → Vercel 更新 |
| `COLORME_ACCESS_TOKEN` | **V** | カラーミー API | 要確認 | カラーミー管理画面で再発行 |
| `ADMIN_USER` / `ADMIN_PASS` | **V** | 自前設定 | — | Vercel env 更新 |
| `X_API_KEY` / `X_API_SECRET` | **V** | X Developer Portal | 無期限（再生成可） | Portal > Keys and tokens で Regenerate |
| `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET` | **V** | X Developer Portal | 無期限（再生成可） | Portal で Regenerate → Vercel 更新 + Redeploy |
| `THREADS_USER_ID` | **V** | Threads `/me` API | 不変 | — |
| `THREADS_ACCESS_TOKEN` | **V** | Meta for Developers | ⚠️ **60日**（長期トークン） | `graph.threads.net/refresh_access_token` で延長 → Vercel 更新 |

### トラスト（LINE Bot シフト管理）

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | **V** | LINE Developers / Messaging API | 長期（再発行可） | LINE Developers コンソールで再発行 → Vercel 更新 |
| `LINE_CHANNEL_SECRET` | **V** | 同上 | 不変（チャネル固定） | チャネル再作成時のみ |
| `SUPABASE_SERVICE_ROLE_KEY`（トラスト） | **V** | Supabase（トラストプロジェクト） | 無期限 | Supabase rotate → Vercel 更新 |
| `ANTHROPIC_API_KEY`（トラスト） | **V** | Anthropic Console | 無期限 | Console rotate → Vercel 更新 |
| `STAFF_ENROLLMENT_CODE` | **V** | 自前設定 | — | Vercel env 更新 |

### ビジネス21（監理団体）

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| `SUPABASE_SERVICE_ROLE_KEY`（ビジネス21） | **V** + **G** ⚠️重複 | Supabase（ビジネス21プロジェクト） | 無期限 | Supabase rotate → Vercel と GitHub Secret **両方**更新 |
| `GEMINI_API_KEY` | **V** | Google AI Studio | 無期限 | AI Studio で rotate → Vercel 更新 |
| `AUTH_SECRET` | **V** | 自前設定 | — | Vercel env 更新 |
| `CRON_SECRET`（ビジネス21） | **V** | 自前設定 | — | Vercel CLI で再登録 |

### みんなのWA

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| `RESEND_API_KEY` | **V** | Resend Dashboard | 無期限 | Resend で rotate → Vercel 更新 |
| `SUPABASE_SERVICE_ROLE_KEY`（みんなのWA） | **V** | Supabase（みんなのWAプロジェクト） | 無期限 | Supabase rotate → Vercel 更新 |
| `CRON_SECRET`（みんなのWA） | **V** | 自前設定 | — | Vercel CLI で再登録（2026-05-13 登録済） |

### ClimbHero（Cloudflare 集約）

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| `JWT_SECRET` | Cloudflare（wrangler secret） | 自前設定 | — | `wrangler secret put JWT_SECRET` |
| `GEMINI_API_KEY` | Cloudflare | Google AI Studio | 無期限 | AI Studio rotate → wrangler 更新 |
| `YOUTUBE_API_KEY` / `VIMEO_ACCESS_TOKEN` | Cloudflare | 各 API コンソール | 要確認 | 各コンソールで再発行 |
| `X_CLIENT_ID` / `X_CLIENT_SECRET` | Cloudflare | X Developer Portal | 無期限 | Portal Regenerate |
| `STRIPE_*`（Phase 6） | Cloudflare | Stripe Dashboard | 無期限 | Stripe で rotate |
| `RESEND_API_KEY`（ClimbHero） | Cloudflare | Resend Dashboard | 無期限 | Resend rotate |

### 外部 AI バックエンド

| 鍵名 | 保管場所 | 発行元 | 有効期限 | ローテ手順 |
|---|---|---|---|---|
| Codex / ChatGPT 認証 | **L** (`~/.codex/auth.json`) | OpenAI（ChatGPT サインイン） | セッション（再ログイン） | `codex` 再サインイン |

---

## 運用ルール

1. **値はここに書かない**。鍵名・場所・期限・ローテ手順のみ。値が要れば「保管場所」列の実体を見る
2. **鍵を追加/失効/ローテしたら必ずこの表を更新**（PR 単位の更新は CEO 承認不要・Claude が反映）
3. **重複鍵（⚠️マーク）をローテする時は全保管庫を更新**。1 箇所漏れると本番が黙って壊れる
4. **期限つき鍵**（`THREADS_ACCESS_TOKEN` 60日 / X / `CONSUL_REPO_PAT`）の失効予定は Google Calendar にリマインダー登録を推奨（scheduler エージェント）
5. **新規プロジェクト追加時**: そのプロジェクトの必須環境変数をこの台帳に 1 セクション追加する

---

## 既知の問題・要対応

| 優先 | 内容 | 状態 |
|---|---|---|
| **高** | `CONSUL_REPO_PAT` が失効疑い。2026-05-13 以降 sync-consul-docs.yml 不動作。GitHub で再発行 → ai-hub Secret 更新が必要（要 CEO） | 未対応（[詳細](2026-05-16-ai-hub-ops-redesign.md)） |
| 中 | `SUPABASE_SERVICE_ROLE_KEY` / `ANTHROPIC_API_KEY` の保管庫重複。ローテ手順が二重管理 | 構造課題（保管庫集約は別途 advisor 案件） |
| 中 | `THREADS_ACCESS_TOKEN` 60日失効の棚卸し台帳・カレンダー登録が未整備 | 未対応（scheduler で登録可） |

---

## 過去の検討記録

- **2026-05-17**: Bitwarden Secrets Manager 導入相談 → 「保管庫を 5 つ目に増やすのは逆効果。問題の本質は台帳の不在」と判定し、本台帳を新規作成。保管庫の 4→2 集約（Supabase Vault 単一発行元化）は工数大のため将来 advisor 案件として保留
