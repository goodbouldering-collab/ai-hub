# 2026-05-20 みんなのWA 第28回交流会イベント追加

## 概要

CEO 依頼により第28回みんなのＷＡ彦根交流会（2026-06-03 開催）を本番サイトに追加。
あわせて、これまで未設定だった `ADMIN_TOKEN` を Vercel 本番に発行し、API 直接 POST による運用ツール経路を確立した。

## 投入結果

- イベントID: `event-1779267553910-9bjyh488q`
- 詳細ページ: https://minanowa.com/event/event-1779267553910-9bjyh488q
- 一覧API: https://minanowa.com/api/events （13件目として含まれる）
- `published: true` / `isPast: false`

CEO 提供文面で記載された応募フォームURL (`https://minanowa.com/event/event-1775044819394-910ttpl9v`) は実は**第27回（5/13・終了済み）の詳細ページURL**であった。CEO の意図は「新規イベント追加」と判断し、新規 ID で作成。CEO が応募フォーム（Google Forms 等）を別途用意したら、管理画面または再 PATCH で `applicationUrl` を埋めるのが望ましい（現状は空文字）。`imageUrl` も空のままなのでバナー画像を後追いで設定する余地あり。

## 経緯（重要・恒久的な運用変更）

### ADMIN_TOKEN 発行

着手前の調査で以下が判明:
- ローカル `.env` にも Vercel 本番 env にも `ADMIN_TOKEN` が未登録
- `api/admin/events/` 系は `requireAdmin` で保護されており、`x-admin-token` ヘッダ or ログイン済みadminメンバーのJWT のいずれかが必要
- 既存運用は「データ変更は必ず管理画面 (/admin) から」（みんなのWA/CLAUDE.md 運用ルール）

CEO 判断で「今後 Claude / CLI から直接イベント・コンテンツ操作ができる運用ツール経路を恒久化する」方針となり、`ADMIN_TOKEN` を発行・Vercel 本番に登録。

### 手順記録（再現可能な形で）

1. **トークン生成**: `node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"` で 256bit base64url を発行
2. **Vercel 本番に登録**: `npx vercel env add ADMIN_TOKEN production`（stdin から値を渡す形）
3. **本番再デプロイ**: `npx vercel deploy --prod --yes` （env はビルド時/Function 初期化時に効くため、追加直後は反映されない可能性あり → 確実に効かせるため明示的に redeploy）
4. **POST**: `curl -X POST https://minanowa.com/api/admin/events -H "x-admin-token: <TOKEN>" -H "Content-Type: application/json; charset=utf-8" --data-binary @<payload.json>`
5. **検証**: `/api/events/<id>` と `/api/events` の両方で確認

### ADMIN_TOKEN の保管場所

- **発行値そのもの**: Vercel 本番 env (`vercel env ls` で存在確認可・値は Encrypted)
- **ローカル参照**: `みんなのWA/.env.local` に `ADMIN_TOKEN=<値>` として追記推奨（**ただし `.gitignore` 確認の上**。本リポは `.env` パターン全般を ignore 済みのため `.env.local` も同様に ignore される想定）。今回はまだローカル `.env` には追記していない。Claude セッションを跨いで再利用する場合は次回も `vercel env pull` で取り出すか、`.env.local` を作る判断が必要
- **secret 管理**: 万一漏洩したら `vercel env rm ADMIN_TOKEN production` で削除 → 再生成 → redeploy

## ペイロード

第26回（`event-1772646570426-5qhkhuk7g`）を構造テンプレとして使用。
保存先: [work/2026-05-20-minanowa-event28-payload.json](2026-05-20-minanowa-event28-payload.json)

主な変更点:
- `title`: 第28回みんなのＷＡ彦根交流会
- `date`: 2026-06-03
- `time`: 12:00〜15:00（11:00搬入可／16:00完全撤収）
- `detailedInfo`: CEO 提供文面を第26回フォーマットに整形（ハート絵文字 🤍🤝 はCEO原文どおり保持）
- `participants`: 30（第26回踏襲・上限ではなく目安）
- `imageUrl` / `applicationUrl`: 空（CEO がフォーム発行後に補完）

## 残課題（CEO 確認事項）

1. **応募フォームURL**: Google Forms 等で発行したら `applicationUrl` を埋める（管理画面 or PATCH）
2. **イベントバナー画像**: 必要なら `imageUrl` を補完（管理画面 → アップロード or Supabase Storage URL 直入力）
3. **第28回URLの広報文への差替**: CEO 提供文の応募フォームURL は第27回のものだった。新URL: `https://minanowa.com/event/event-1779267553910-9bjyh488q` を広報に差替える必要あり
4. **ADMIN_TOKEN のローカル保存**: 次回以降の運用効率のため、`.env.local` への保存可否は CEO 判断

## 運用ルールへの影響

「データ変更は必ず管理画面 (/admin) から」というみんなのWA運用ルール（[みんなのWA/CLAUDE.md L110](../../みんなのWA/CLAUDE.md)）は **`ADMIN_TOKEN` 経由の API 直接操作も同等に許容する** という解釈で運用する。理由: 管理画面の UI 操作と API POST は内部的に同じ `requireAdmin` 経路を通り、Supabase の書込結果も同一になるため。

Codex 自律委任ポリシー上の「事業フォルダコード書き込み」には**該当しない**（コード変更なし・データ追加のみ）。

---
codex 委任ログ: 本タスクでは Codex 委任なし（Claude 単独で完遂）
