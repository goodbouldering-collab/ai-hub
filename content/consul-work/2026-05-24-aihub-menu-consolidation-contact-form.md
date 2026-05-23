# 2026-05-24 AIハブ メニュー集約 + Resend問い合わせフォーム

CEO依頼:
- ハンバーガーメニューにあるページをトップにうまくまとめて表示、詳細はリンクでページへ
- 問い合わせはフォームを作って Resend で climb@goodbouldering.com へ

本番 https://ai-hub-jp.vercel.app/ 反映済み（commit 96ad8fa）。

## 実装内容

### ① メニュー集約「EXPLORE / もっと知る」セクション
ヘッダーの「その他」ドロップ・mobile-nav にあった項目をトップに3カードで集約（詳細は各ページへリンク）:
- 制作実績・事業ポートフォリオ → /portfolio.html
- 講習資料 → /lectures/index.html
- 自分ポータル（AI Watch） → /watch/index.html

旧 watch-link-bar（地味なリンク行）を `_render_explore()` のカードグリッドに格上げ。

### ② Resend 問い合わせフォーム
- `api/contact.ts` 新設（Vercel Function）: n-デザインの `app/api/contact/route.ts` パターンを Vercel Functions 形式へ移植
  - 管理者宛(問い合わせ内容) + 送信者宛(自動返信) の2通を Resend API で送信
  - メールHTMLはAIハブのダーク基調(#0A0F1C/シアン)に合わせて調整
  - バリデーション: 必須(名前/メール/内容)・メール形式・4000字上限
  - env 未設定時は送信スキップして success（フォーム動作は壊れない設計）
- `_render_contact_form()`: フォームUI(名前/メール/相談種別/内容) + サイド(メール相談/30秒AI診断導線)
- 送信JS: `/api/contact` へ非同期POST、ステータス表示(送信中/成功/失敗)

### 必要env（本番送信の有効化に必要）
| key | 値 | 状態 |
|---|---|---|
| RESEND_API_KEY | n-デザイン/みんなのWAの既存キー流用予定 | **未設定** |
| CONTACT_TO_EMAIL | climb@goodbouldering.com | 未設定(コード既定値あり) |
| CONTACT_FROM_EMAIL | onboarding@resend.dev(暫定) | 未設定(コード既定値あり) |

## トラブルと修正
- 初回デプロイが **Error**（`api/contact.ts: config.runtime: "nodejs" semantics will evolve` で失敗）。`export const config = { runtime: "nodejs" }` がVercel新仕様で非推奨エラー。他のapi/*.tsに倣い runtime キー削除で解消（commit 96ad8fa）

## 本番疎通確認
- `/api/contact` GET → 405（method guard）
- `/api/contact` POST 空 → 400「必須項目不足」（バリデーション動作）
- TOPに「もっと知る」3カード・問い合わせフォーム反映

## 残課題（env設定でメール送信が有効化）
env設定は本番secret操作のため、Auto Modeのセキュリティ判定で複数回ブロックされた（クロスプロジェクトのRESEND_API_KEY流用 + secret設定は明示承認でも判定を通せず）。

**RESEND_API_KEY の設定方法（2案）**:
- A. CEOがVercelダッシュボードで n-デザインの値をコピーしてAIハブに貼る（私がsecretに触れず安全）
- B. Bashのpermission許可を明示的に出してもらい、私が `vercel env add` で設定

**送信元(From)の注意**: Resendは認証済みドメインからしか送れない。暫定 `onboarding@resend.dev` は「自分のResendアカウントのメールにしか届かない」制限あり。理想は `goodbouldering.com` を Resend で DNS認証して `noreply@goodbouldering.com` を From にする（CEOのResendダッシュボード作業）。

## 委任ログ
Claude単独。n-デザインの実装を参照（route.ts読込のみ）。env操作はセキュリティ判定で保留、CEO判断待ち。
