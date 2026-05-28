# 2026-05-13 トラスト案件 認証基盤決定ログ

## CEO 指示（要約）

「LINE からもブラウザからも使える」「同じコンポーネントを使い回す」「合言葉登録は Web/LINE 共通」

## 確定方針

| 論点 | 確定 |
|---|---|
| 認証方式 | **LINE Login（Web OAuth）統一**。LIFF からも Web からも LINE `userId` で一意識別 |
| LINE チャネル | **2つ作成**: Messaging API + LINE Login（同一 Provider 配下） |
| セッション | **iron-session**（暗号化 Cookie 30日有効・KV 不要） |
| 初回登録 | `/enroll` で合言葉 + 氏名入力・Server Action で `STAFF_ENROLLMENT_CODE` 検証 |
| 保護対象 | `/home-shift/*` のみ middleware で Cookie 有無を判定。本権限チェックは page/Route Handler 側 |
| UI 統一 | LIFF/Web 同じコンポーネント。差分は `liff.isInClient()` で対応（カレンダー追加ボタン等） |

## 採用しなかった選択肢

| 案 | 却下理由 |
|---|---|
| Supabase Auth | LINE userId と独立した user_id を持つことになり、二重管理になる |
| メールマジックリンク | スタッフのメール収集コスト・到達率の不安 |
| スタッフコード+合言葉 | パスワード管理運用が発生・LINE 既保有なら LINE Login の方が摩擦少 |
| ワンタイムリンク（個人URL） | URL 漏洩でなりすまし可能・福祉事業者でリスク取れない |
| JWT 自前実装 | iron-session の方が依存最小で実績多 |
| Vercel KV | $0 範囲だがセッション程度に課金課題を持ち込みたくない |

## 出力物（このターンで作成）

### `C:\VSCode\Project\トラスト\`（新規10ファイル・既存3ファイル更新）

新規:
- `app/login/route.ts` — LINE Login 開始・state/nonce 発行・302
- `app/api/auth/line/callback/route.ts` — code 交換・id_token verify・セッション確立・/enroll または /home-shift へ
- `app/api/auth/logout/route.ts` — セッション破棄
- `app/enroll/page.tsx` — 合言葉フォーム（Server Action）
- `middleware.ts` — `/home-shift/*` Cookie 有無で gate
- `lib/session.ts` — iron-session ラッパー
- `lib/line-auth.ts` — OAuth URL 組立 / token 交換 / id_token verify
- `lib/home-shift/staffs.ts` — `findStaffByLineUserId` / `enrollStaff`（snake_case→camelCase mapper 込み）
- `components/SessionNav.tsx` — 共通ヘッダー

既存更新:
- `lib/supabase.ts` — module-load 時 throw を lazy 評価に変更（Supabase 未設定でも他ページが動く）
- `.env.example` — `LINE_LOGIN_CHANNEL_ID` / `LINE_LOGIN_CHANNEL_SECRET` / `SESSION_SECRET` 追加
- `app/page.tsx` / `app/home-shift/page.tsx` — SessionNav 組み込み
- [CLAUDE.md](CLAUDE.md) — 「認証フロー」セクション追加、ディレクトリ構成図更新
- `package.json` — `iron-session ^8.x` 追加

### 動作確認結果（dev サーバー実機）

| エンドポイント | 期待 | 実測 |
|---|---|---|
| `/` | 200 ポータル | ✅ 200 |
| `/login` (env 未設定) | 503 親切なエラー | ✅ 503 "Login is not configured yet" |
| `/home-shift` (未ログイン) | 307 → /login | ✅ 307 |
| `/enroll` (未ログイン) | 307 → /login?next=/enroll | ✅ 307 |
| `/api/line/webhook` | 200 | ✅ 200 |
| `/api/auth/logout` | 307 → / | ✅ 307 |
| `/api/auth/line/callback?error=...` | 307 → /login?error=... | ✅ 307 |

typecheck: exit 0 / エラーゼロ

## 実装中に踏んだバグと修正

| バグ | 原因 | 修正 |
|---|---|---|
| `/login` で Server Component から `cookies().set()` が拒否される | Next.js 15 の仕様（Server Component は読み取り専用） | `app/login/page.tsx` を削除し `app/login/route.ts`（Route Handler）に変更 |
| Supabase 未設定で `/enroll` が 500 | `lib/supabase.ts` がモジュール読み込み時に throw | 関数内部で読むよう lazy 評価に変更 |

## 重要な技術判断

### middleware で iron-session を読まない設計

Next.js Edge middleware は Node.js API（`crypto.subtle.decrypt` 等）が制限される。
iron-session の復号は Node Runtime で行いたい。

→ middleware では **Cookie 有無のみ判定**し、本物の認証チェックは page/Route Handler 側で
`getSession()` を呼んで行う。middleware は「明らかに未ログイン」を弾く役割だけ。
偽造 Cookie で middleware を通り抜けても、page 側の `getSession()` で復号失敗して
セッション空オブジェクトになるので、認可は破綻しない。

### LIFF と Web の userId 一致が前提

LIFF SDK で取れる `userId` と、LINE Login で取れる `id_token.sub` は**同一 Provider 内で一致**
する設計（LINE 公式仕様）。なので「両方とも staffs.line_user_id で識別」が成立する。

これを担保するため、**LIFF アプリは LINE Login チャネル側に紐付ける**運用にする
（Messaging API 側に紐付けると userId が違う Channel ID にぶら下がる可能性があるため）。

## CEO 未承認・次に必要なアクション

| アクション | 必要性 | 補足 |
|---|---|---|
| LINE Developers で Provider 作成 | 必須 | 既存 Provider 流用も可。トラスト専用が望ましい |
| Messaging API チャネル作成 | 必須 | Webhook URL: `https://trust.vercel.app/api/line/webhook` |
| LINE Login チャネル作成 | 必須 | Callback URL: `https://trust.vercel.app/api/auth/line/callback`・scope `profile openid` |
| LIFF アプリ作成（Login チャネル配下） | 必須 | endpoint URL: `https://trust.vercel.app/home-shift/liff/shift-request` 等 |
| Supabase プロジェクト作成 + migration 適用 | 必須（`/enroll` の DB 書き込みに必要） | `supabase/home-shift/migrations/0001_init_schema.sql` を流す |
| `STAFF_ENROLLMENT_CODE` の文言決定 | 必須（`/enroll` 起動に必要） | 例: `tousutoshift2026` のような覚えやすい・8文字以上 |
| Vercel プロジェクト `trust` 作成 + env 投入 | デプロイ時 | `NEXT_PUBLIC_SITE_URL` を Vercel URL に更新が必要 |
| GitHub `goodbouldering-collab/trust` 作成 | デプロイ時 | 初回 push |

## 残課題（仕様詰め）

1. **既存スタッフのインポート方法**: 17名分の `staffs` レコードを管理者が事前作成するか、自己登録のみで集めるか
2. **合言葉の管理**: グローバル1つでよいか、棟ごとに別か、有効期限を設けるか
3. **管理者 vs スタッフのロール分離**: `staffs` テーブルに `is_admin` カラム追加？それとも `ADMIN_LINE_USER_IDS` env で OK？
4. **退職者の扱い**: `is_active = false` で論理削除のみで OK か、LINE 連携も切るか
