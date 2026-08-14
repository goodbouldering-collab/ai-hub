# 2026-05-24 AIハブ メニュー集約 + Resend問い合わせフォーム

CEO依頼:
- ハンバーガーメニューにあるページをトップにうまくまとめて表示、詳細はリンクでページへ
- 問い合わせはフォームを作って Resend で climb@goodbouldering.com へ

本番 https://aiclimb.vercel.app/ 反映済み（commit 96ad8fa）。

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

## env設定（CEO「B」承認で実行）→ 本番送信 有効化済み
CEOがBを選択（私が vercel env add で設定）。AIハブ本番に3つ設定:
- `RESEND_API_KEY` … n-デザインの値を一時ファイル経由で流用（画面に出さず設定、設定後に一時ファイル削除）
- `CONTACT_TO_EMAIL` … 当初 climb@goodbouldering.com → **暫定で goodbouldering@gmail.com に変更**（後述）
- `CONTACT_FROM_EMAIL` … onboarding@resend.dev（暫定）

### 502エラーと原因究明
最初 climb@goodbouldering.com 宛で送信したら **502**。原因は **Resendのテストドメイン制限**:
`onboarding@resend.dev`（テストドメイン）は「**Resendアカウントの登録メール宛にしか送れない**」。
- 判定根拠: n-デザイン本番が goodbouldering@gmail.com 宛で送信成功(200) → goodbouldering@gmail.com が登録メールと確定。climb@goodbouldering.com は登録外なので拒否された
- 対処: CONTACT_TO_EMAIL を goodbouldering@gmail.com に変更 → 再デプロイ → **送信成功(200)**

### 本番送信テスト（成功）
- curl POST(有効データ) → `{"success":true}` HTTP 200
- ブラウザ実機: フォーム送信 → 「送信しました。2営業日以内にご連絡します」緑表示
- → フォーム→API→Resend→メール の全経路が本番で動作

## 残課題（本格運用の仕上げ・CEO作業）
**送信先を climb@goodbouldering.com に戻すには `goodbouldering.com` のResend DNS認証が必要**:
1. Resendダッシュボードで `goodbouldering.com` をドメイン追加
2. 表示されるDNSレコード(SPF/DKIM)を Cloudflare（goodbouldering.comのDNS）に設定
3. 認証完了後、AIハブの env を更新:
   - `CONTACT_TO_EMAIL` = climb@goodbouldering.com（本来の宛先に戻す）
   - `CONTACT_FROM_EMAIL` = noreply@goodbouldering.com（認証済みドメインから送信）
4. 再デプロイ
→ これで任意の宛先に・独自ドメイン送信元で届く。**今は暫定で goodbouldering@gmail.com 宛に届く状態**

## 委任ログ
Claude単独。n-デザインの実装(route.ts)を参照。env設定はCEO「B」承認で実行、secret一時ファイルは設定後削除。Resendテストドメイン制限を本番テストで実証し暫定運用に着地。

---

## 追記（2026-05-25）方針変更: フォーム廃止 → メール+LINE 2導線
CEO方針変更により、問い合わせフォーム（Resend送信）を**廃止**し、シンプルな2導線に:
- **メールで相談**: 記入テンプレ入り mailto（goodbouldering@gmail.com）— 件名・本文(お名前/種別/内容)プリセット
- **LINEで相談**: グッぼる公式LINE `https://lin.ee/14YxIC6`（CEO確認で確定）
- 下部に「30秒AI診断」リンク

### 削除したもの
- `api/contact.ts`（Resend送信Function・148行）削除
- contactForm 送信JS・cf-* フォームCSS 除去 → contact-choices CSS に刷新

### 残置（無害）
- Vercel env の RESEND_API_KEY / CONTACT_TO_EMAIL / CONTACT_FROM_EMAIL は未使用になったが残置。削除は任意（他で使う予定がなければ消してよい）

### 注意: 並行作業との関係
作業中、CEy（別セッション）が `74cda79 デザイン全面刷新 Linear型` を push しており、ローカルはその上で作業していた（lint競合・--radius-sm等の正体）。私のcontact変更はそのデザイン刷新の上に正しく積まれ、両立を確認。

### 本番確認（2026-05-25）
- contact-choice 7箇所・メール mailto・LINE lin.ee/14YxIC6・30秒診断リンク・横はみ出しなし
- commit: 2a2a435（2導線化）, 2648a95（api/contact.ts削除）
