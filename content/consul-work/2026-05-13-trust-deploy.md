# 2026-05-13 トラスト案件 初回 Vercel デプロイ完了ログ

## CEO 指示

「ノンストップ」で GitHub + Vercel 連携・本番デプロイまで一気通貫。

## 成果

### 本番 URL（公開済み・LINE 未接続のプレビュー）

🌐 **https://trust-nine-tau.vercel.app**

| ルート | 状態 |
|---|---|
| `/` | ✅ 200 ポータル（trust + シフト管理カード） |
| `/home-shift` | ✅ 200 シフトアプリトップ |
| `/home-shift/liff/shift-request` | ✅ 200 希望提出（プレースホルダ） |
| `/home-shift/liff/shift-view` | ✅ 200 シフト確認（プレースホルダ） |
| `/enroll` | ✅ 200 合言葉フォーム（「LINE 未接続中」バナー付き） |
| `/api/line/webhook` | ✅ 200 `{ok:true}` |
| `/login` | LINE 未接続のため 503 想定 |

### 重要な発見

**`trust.vercel.app` は取得不可能だった**:
- 第三者の Altos 社が **`trust.vercel.app` を先に取得**している（title: "Altos - Building Trust on the Web"）
- Vercel のサブドメインは世界中で先勝ち
- Vercel が割り当てたサフィックス付き: **`trust-nine-tau.vercel.app`**

→ 独自ドメイン取るときは `trust.com / trust.jp` も世間で取り合いが激しいので、別の名前
（例: `trust-care.com`, `trust-shift.app`）が現実的。

### 作成・設定したリソース

| リソース | 値 |
|---|---|
| GitHub リポ | `goodbouldering-collab/trust`（private） |
| Vercel Project ID | `prj_WgcnPJcTCdjo7iwneQjkZ30p7tPi` |
| Vercel Project 名 | `trust` |
| 本番デプロイ ID | `dpl_E4Jiz6WpBqxhab8qBKTQ7uwt3Nkn` |
| Production Branch | `main`（push で自動デプロイ） |

### Vercel 環境変数（投入済み）

| キー | 用途 | スコープ |
|---|---|---|
| `SESSION_SECRET` | iron-session 暗号化キー（32バイト乱数・自動生成） | prod/preview/dev |
| `NEXT_PUBLIC_SITE_URL` | `https://trust-nine-tau.vercel.app`（最初 `trust.vercel.app` で投入し、判明後即修正） | prod |
| `CLAUDE_MODEL` | `claude-opus-4-7` | prod/preview/dev |

### 未投入の Vercel 環境変数（手動で揃える必要あり）

| キー | 取得元 | 投入タイミング |
|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Developers / Messaging API | LINE チャネル作成後 |
| `LINE_CHANNEL_SECRET` | 同上 | 同上 |
| `LINE_LOGIN_CHANNEL_ID` | LINE Developers / LINE Login | LINE Login チャネル作成後 |
| `LINE_LOGIN_CHANNEL_SECRET` | 同上 | 同上 |
| `ADMIN_LINE_USER_IDS` | CEO + 運営担当者の LINE userId | LINE 接続後 |
| `NEXT_PUBLIC_LIFF_ID_SHIFT_REQUEST` | LIFF アプリ作成時 | 同上 |
| `NEXT_PUBLIC_LIFF_ID_SHIFT_VIEW` | 同上 | 同上 |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase プロジェクト Settings → API | Supabase 作成後 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 同上 | 同上 |
| `SUPABASE_SERVICE_ROLE_KEY` | 同上 | 同上 |
| `ANTHROPIC_API_KEY` | Anthropic Console | Phase 2 着手前 |
| `STAFF_ENROLLMENT_CODE` | CEO が文言決定 | LINE 接続後 |

## 実装した「LINE 未接続中でも見られる」対応

### `middleware.ts`

`LINE_LOGIN_CHANNEL_ID` が未設定なら、middleware は全リクエストをスルー。
これで `/home-shift/*` も保護なしで見られる。

```ts
const AUTH_ENABLED = Boolean(process.env.LINE_LOGIN_CHANNEL_ID);
if (!AUTH_ENABLED) return NextResponse.next();
```

### `app/enroll/page.tsx`

LINE 未接続中は `/login` リダイレクトせず、フォームを表示。
ただし「プレビューモード」バナーを出して送信しても処理されないことを明示。

### `lib/supabase.ts`

モジュール読込時の throw をやめ、関数内 lazy 評価に変更。Supabase 未設定でも
他ページが死なない。

これらは **LINE/Supabase 接続後は自動的に通常モードに戻る**設計。環境変数を入れるだけ。

## CEO 手動アクションの残り

| 順 | アクション | 担当 | 目的 |
|---|---|---|---|
| ① | Supabase プロジェクト `trust` 作成 | CEO | DB 接続情報取得 |
| ② | 上記接続情報を Vercel env に投入 | Claude (API) または CEO | DB 接続 |
| ③ | migration `0001_init_schema.sql` を Supabase で実行 | Claude (Supabase CLI) または CEO | テーブル作成 |
| ④ | LINE Developers で Provider + Messaging API + LINE Login + LIFF 作成 | CEO | LINE 連携 |
| ⑤ | LINE 関連 env を Vercel に投入 | Claude (API) | LINE 認証稼働 |
| ⑥ | `STAFF_ENROLLMENT_CODE` 文言決定 | CEO | スタッフ登録ゲート |
| ⑦ | Redeploy | Claude (API) | 全機能稼働 |

## 検証コマンド

```bash
# 本番動作確認
curl -I https://trust-nine-tau.vercel.app/
curl -I https://trust-nine-tau.vercel.app/home-shift
curl https://trust-nine-tau.vercel.app/api/line/webhook   # {"ok":true,"service":"trust line webhook"}

# Vercel デプロイ状況
gh repo view goodbouldering-collab/trust --web
```
