# みんなのWA: イベント保存401修正 + ヒーロー押出一元化

**日時**: 2026-05-21
**事業**: みんなのWA
**対応**: Claude (このセッション)
**コミット**: `b82385f` (admin修正) / `75be788` (押出一元化)

---

## 1. イベント保存エラー「未認証 (x-member-id ヘッダが必要)」修正

### 症状
admin.html のイベント編集モーダルで保存を押すと、画面右上に
「保存失敗: 未認証 (x-member-id ヘッダが必要)」のトーストが表示され保存できない。

### 根本原因
- サーバ側 `lib/vercel-utils.js` の `requireAdmin` は `x-member-id` ヘッダ
  または `x-admin-token` ヘッダのどちらかを要求する仕様
- `admin.html` 側は `/api/admin/*` への fetch で **どちらのヘッダも一切送信していなかった**
- イベント保存だけでなく、メンバー編集・ブログ削除・掲示板更新・サイト設定保存・
  バックアップ操作・運営メンバー切替・有料イベントの支払状態切替まで合計15箇所が
  同じ問題を抱えていた（=これまで本当に動いていたとは思えない領域がある）

### 修正
- admin.html に `adminFetch(url, opts)` ヘルパを追加
  - `localStorage.wa_user` 経由で復元された `admin.id` を `x-member-id` ヘッダに自動付与
  - 既存 `opts.headers` はマージして保持
- 既存の admin API への素の `fetch(...)` を全 15 箇所 `adminFetch(...)` に置換
  - `/api/admin/events/*` (POST/PUT/DELETE)
  - `/api/admin/blogs/*` (PUT/DELETE)
  - `/api/admin/members/*` (PUT/DELETE) ※権限切替も含む
  - `/api/admin/boards/*` (PUT/DELETE)
  - `/api/admin/backup` / `/api/admin/backups*` (バックアップ作成・一覧・復元・削除・アップロード)
  - `/api/admin/reorder` / `/api/admin/operating-members` (PUT)
  - `/api/site-settings` (PUT) ※admin必須
  - `/api/events/:id/toggle-payment` (POST) ※admin必須

### CEO 側で必要なアクション
1. デプロイ完了を 1〜2 分待つ
2. `https://minanowa.com/admin.html` を **Ctrl+Shift+R で強制リロード**
   （ブラウザキャッシュに古い JS が残っていると治らないので必須）
3. もう一度イベント保存を試す

---

## 2. ヒーロー押出と「今日のWA」の重複を一元化

### 重複構造（修正前）
| 場所 | 内容 |
|---|---|
| Hero 内 `#heroNotifBar` | 「あなたの参加予定イベント」/ 直近イベント2件、「あなた宛のメッセージ」/ 掲示板最新3件 |
| Hero 直下 `#todayWaCard` | 次の交流会1件 / 最新ブログ1件 / 最新掲示板1件 |

「次のイベント」「最新掲示板」の情報が**2連続で出ていた**。ブログだけは todayWA 限定。

### CEO 判断
「Hero 内押出を残し、`#todayWaCard` を削除」（理由: ログイン中ユーザの
パーソナライズ表示が Hero 内押出にしかない / ブログは直下の
「お知らせ・レポート」セクションで自然に見えるため押出不要）

### 修正内容
削除:
- CSS: `today-wa-*` 関連 24 行
- HTML: `#todayWaCard` セクション 22 行
- JS: `renderTodayWA()` 関数 50 行
- JS呼び出し: 初期化フローの `;renderTodayWA();`

合計 -100 行 / +1 行。

### CEO 側で必要なアクション
1. デプロイ完了後、トップを Ctrl+Shift+R で強制リロード
2. Hero ファーストビューの押出（参加予定イベント・掲示板通知）が
   引き続き出ていることを確認
3. ファーストビュー直下のオレンジ系「今日のWA」カードが消えていることを確認

---

## 安全ゲートの結果

| ゲート | 結果 |
|---|---|
| ① ビルド (npm run build) | 対象外（package.json に build スクリプト無し・静的HTML + Vercel Functions） |
| ② 秘密情報の直書きチェック | OK（DOM 値の参照名のみ。実値の直書きなし） |
| ③ 意味ある単位での commit | OK（2 コミットに分離: 機能修正 / リファクタ） |

`git push origin main` 完了 → Vercel 本番自動デプロイ。

---

2026-05-22 codex:codex-rescue 発火（みんなのWA全体リファクタ棚卸し調査/Codex使用枠上限のため未実行・5/24 17:32 JSTリセット待ち→Claude本体に切替）

---

## 3. みんなのWA リファクタリング（2026-05-22）

### スコープ判断
CEO 指示「みんなのWA 全体」→ さらに絞って「明らかな重複の共通化まで一気に」を選択。
入口判定で「重い案件（5ファイル以上横断・全体スキャン）」と見積もり、Codex 主で
棚卸しに出そうとしたが **Codex 使用枠上限**（5/24 17:32 JST リセット）のため、
Claude 本体 + Explore サブエージェント（読み取り専用・別コンテキスト）で棚卸し実施。

### Explore 棚卸し結果（admin.html 1917行）
- **削除処理4関数が完全同型**（delEvent/delBlog/delMember/delBoard）= 最低リスクの共通化候補
- 保存ハンドラ6関数の部分重複（中リスク・フォーム値収集が関数ごとに違う）
- モーダル開閉6関数（中リスク）、テーブル描画5関数（低リスク・ドメイン固有性高い）
- `_spinnerCount` 多重制御が脆弱（将来課題）
- `animStat()` が未使用の可能性（要確認・今回は未対応）

### 実施（CEO 承認: 削除処理の統一だけ）
- `delResource(resource, id)` に4関数を集約、各 del* は後方互換ラッパ
- 呼び出し側（addEventListener 経由）は変更不要
- API 側 events/blogs/members/boards すべて `[id].js` に DELETE 登録済みを確認、挙動不変
- commit `7b525c9` → push 済

### 残り（次回 Codex 枠回復後の候補）
- index.html(6390行) の棚卸し未実施（Hero カード生成重複・render* 重複・fetch エラーハンドリングのバラつき）
- api/ 58本のボイラープレート揃え具合の確認
- admin.html の保存ハンドラ共通化（中リスク）
