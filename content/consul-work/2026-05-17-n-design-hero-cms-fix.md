# N-デザイン トップ ヒーローセクション 管理ページ編集化 — 完了報告

**作成日**: 2026-05-17（日）
**対象事業**: N-デザイン（`C:\VSCode\Project\N-デザイン\`）
**CEO 指示（連続）**: ①ヒーロー編集化 → ②デプロイ → ③ログイン注釈削除＋admin/password123 → ④トップ8セクション集約＋固定メニューに管理ログイン導線
**ステータス**: ✅ **全件完了**（本番 https://n-design.work で実機検証済み・PR #4 マージ済み）

---

## 1. 結論

**ヒーローセクションは `/admin` から編集可能になった**。本番サイト https://n-design.work で文字化けなく正しく表示されることを確認済み。

CEO 要求（テキストのみ・ヒーローのみ）に対し、機能コードは既に完成済みだったため、**本番データの破損を修正するだけ**で要求を満たせた。設計書 [2026-05-17-n-design-section-content-cms.md](2026-05-17-n-design-section-content-cms.md) が想定していた「ゼロから新規実装」は **本件スコープでは不要**（あれはヒーロー以外のセクション本文＝services/value/flow/faq 等の話で、CEO の今回指示には含まれない）。

---

## 2. 調査で判明した真の状態（設計書の前提を訂正）

| 項目 | 設計書の記載 | 実機検証の結果 |
|---|---|---|
| `site_profile.hero_*` 列 | ❌ 未適用（`code:42703`） | ✅ **存在・HTTP 200**（マイグレーション適用済だった） |
| ヒーロー編集 UI / 読み出し | ✅ 完成済 | ✅ 完成済（コミット `7042728`）— 一致 |
| 本番の `hero_*` データ | （言及なし） | ❌ **日本語が全て文字化け（mojibake）** + `hero_stats` が空配列 |

→ 真の問題は「コード未実装」でも「列未適用」でもなく、**本番テーブルに壊れた日本語データが入っていて編集画面が `?????` を表示する**点だった。

---

## 3. 実施した修正

`SUPABASE_ACCESS_TOKEN`（`.env.supabase` の Management API トークン）を使い、CEO の GO 承認のもと Supabase Management API（`POST /v1/projects/{ref}/database/query`）で `site_profile` の `hero_*` を [hero-data.ts](../../N-デザイン/lib/data/hero-data.ts) の `defaultHeroCopy` と一致する正しい値に UPDATE。

**文字化け再発防止策（重要な技術判断）**:
- 通常の日本語 SQL を curl 送信すると Git Bash / 端末のロケール変換で再び mojibake する
- → **日本語を一切含まない ASCII-only SQL** を生成：各文字列を UTF-8 hex 化し `convert_from(decode('<hex>','hex'),'utf8')` で DB 内部で復元させる方式に切替
- これにより送信経路（シェル・curl・JSON）のどのエンコーディング変換も通過しても破損しない

**検証**: anon キーで REST 読み出し → Python で `==` 完全一致比較（端末表示ではなくバイト一致で判定）→ 全項目 OK・`hero_stats` 3件復元。最終的に本番サイト https://n-design.work を WebFetch し、ヒーローのバッジ／見出し／リード／数値バッジ／CTA が**文字化けなく**表示されることを確認。

---

## 4. CEO が今できること

`/admin` → ログイン → 「ヒーロー」タブ で以下を編集可能：

| 編集項目 | 内容 |
|---|---|
| バッジ | 最上部の小見出し（現在: 滋賀・彦根 ｜ 古民家再生 × デザイン工務店）|
| 大見出し 上段／下段 | 下段は金色グラデーション |
| リード文 | 改行も表示に反映 |
| 数値バッジ | 追加・削除可（現在 3 件）|
| CTA ボタン文言 | 緑ボタン／透明ボタン |

保存すると本番サイトに最大数分で反映（クライアント側 `useHomeData` が `site_profile` から読むため）。

---

## 5. 残課題（本件スコープ外・別途 CEO 判断）

- **ヒーロー以外のセクション本文編集**（services/value/flow/faq 等）は未実装のまま。設計書 [2026-05-17-n-design-section-content-cms.md](2026-05-17-n-design-section-content-cms.md) の P1〜P4 が該当。今回の CEO 指示（「ヒーローのテキストのみ」）には含まれないため着手せず。やるなら別途承認が必要
- 設計書冒頭の「hero 列は本番未適用」という記述は**実機と食い違っていた**。同設計書を参照する場合この点に注意（本報告が正）

---

## 6. 事業リポへの書き込み

**なし**（`C:\VSCode\Project\N-デザイン\` 配下のファイルは一切編集していない）。本番 Supabase データの UPDATE のみ実施。consul 鉄則（事業リポ書込は CEO 承認必須）に抵触せず、本番 DB 操作は CEO の明示 GO を取得済み。

---

---

## 7. 後続作業（同日・連続指示への対応）

### 7-1. デプロイ構造の判明

ヒーロー編集機能のコードは **オープン PR #4「feat(admin): トップヒーローセクションを /admin から編集可能に」**（`origin/feat/admin-hero-editor`）として存在し、`origin/main` 未マージだった。N-デザインは `main` push で Vercel 自動デプロイ。ローカル `main` の追跡先が誤って feature ブランチを向いていたため初回 `git push origin main` が空振りした。→ PR #4 経由でマージする方式に確定。

### 7-2. `/admin` 認証を admin / password123 に

`/admin` は **Supabase Auth**（`signInWithPassword`）。コードの初期値変更だけではログイン可否は変わらない（Supabase 側ユーザーが本体）。CEO 明示指示のもと Management API で service_role キーを取得 → `admin@n-designs.com`（既存ユーザー id `03d623ca…`）のパスワードを `password123` に設定。コード側は「ユーザー名 `admin`（大小無視）→ `admin@n-designs.com` へ解決」「空入力バリデーション」を実装。本番で `admin` / `password123` ログイン成功を実機検証（access_token 発行・role authenticated）。

> ⚠️ **セキュリティ申し送り**: `password123` は総当たり耐性が極めて低い。本番公開された工務店サイトの管理画面（ブログ・施工事例・会社情報を改竄可能）。CEO はリスク説明済みで承認。早期に `/admin` のアカウント設定タブから強固なパスワードへ変更すべき（変更後はコードのマッピングは無関係に新パスワードで運用可能）。

### 7-3. トップ 13 → 8 セクション集約

CEO 選択「8セクションに統合」。**コンポーネントは削除せず**（データ・SEO・FAQ JSON-LD 破壊回避）、`app/page.tsx` で関連セクションを隣接配置し、`section-nav.tsx` / `header.tsx` のナビ項目を 8 グループに統合：トップ / 強み / 施工事例 / サービス / 料金・補助金 / ご依頼の流れ / ブログ / お問い合わせ。プロフィール→強み直後、お客様の声→施工事例直後、Instagram→ブログ直後、FAQ・アクセス→問い合わせ直前に結合。

### 7-4. 固定メニューに管理ログイン導線

`section-nav.tsx`（PC 左固定ドットナビ）最下部に区切り＋「管理ログイン」（`/admin`・Lock アイコン）を追加。PC のみ表示の section-nav を補うため `header.tsx` のモバイルメニュー最下部にも控えめに追加。

### 7-5. 品質ゲート

- `npm run build` ✅ / `tsc --noEmit` ✅（型エラーゼロ）
- **Codex セカンドオピニオン**（CLAUDE.md 自律委任ポリシー準拠）: 観点2/3 問題なし、観点1で「大文字小文字正規化」「空入力バリデーション」2点指摘 → 両方修正済
- PR #4 CI: build pass / Vercel pass。`main` squash マージ（mergeCommit `7b25b14`）→ Vercel 本番デプロイ success
- 本番 https://n-design.work 実機検証: ①ヒーロー文字化けなし ②ナビ8項目 ③/admin 導線あり、すべて確認

### 7-6. 事業リポ書き込み

今回はコード変更を伴うため `feat/admin-hero-editor` ブランチに4ファイル（`app/admin/page.tsx` / `app/page.tsx` / `components/header.tsx` / `components/section-nav.tsx`）をコミット（`5cdb231`）。`app/specs/generated.ts`（prebuild 自動生成物）・`package.json`（CRLF のみ）はコミット除外。push・マージ・本番 DB 操作はいずれも CEO の明示指示を取得済み（consul 鉄則遵守）。

---

---

## 8. 管理者アカウント運用（2回目の追加指示）

### 8-1. 経緯

CEO が `/admin` のアカウント設定タブでパスワード変更できず。Management API（service_role）で直接 Supabase Auth を操作する方式に切替。

### 8-2. 実施した Supabase Auth 設定（すべて実機ログイン検証済み）

| メール | 状態 | password123 ログイン | 用途 |
|---|---|---|---|
| `goodbouldering@gmail.com` | 既存ユーザー（id `4d148be3…`）にパスワード設定 | ✅ OK | Web制作会社（クライミングコンサル／由井）用 |
| `admin@n-design.work` | **新規作成**（id `dae82156…`・email_confirm 済） | ✅ OK | N-デザイン社（クライアント）用 |
| `admin@n-designs.com`（旧・誤ドメイン s 付き） | 触らず放置→結果無効 | ❌ FAIL（invalid_credentials） | 廃止扱い |

> CEO 指示の `googdbouldering@gmail.com` はタイポと判断し確認 → `goodbouldering@gmail.com`（CEO 連絡先・既存ユーザーあり）で確定。

### 8-3. コード変更（PR #5・別途デプロイ）

旧 `admin → admin@n-designs.com` マッピングは対象アカウント無効化により死にロジック化していたため削除。ログイン入力欄を `email` 型・「メールアドレス」表記に統一、空入力バリデーションは維持。**メール直接入力方式**に統一（`goodbouldering@gmail.com` / `admin@n-design.work` をそのまま入力）。

### 8-4. 見積書ページの分離（重要・未完）

作業中、別経路で作成された未追跡の **`app/admin/estimate/page.tsx`（11KB）** と page.tsx への見積書 Link 追加（2026-05-17 23:15 作成）を検出。今回のログイン修正とは無関係なため CEO 指示で**本 PR から分離**。`feat/admin-hero-editor` ブランチ側の **`git stash@{0}: wip-estimate-and-generated` に保全**（消失していない）。**未レビュー・未デプロイのまま残存。別途扱う必要あり**。

### 8-5. デプロイ

- 新ブランチ `fix/admin-login-email`（origin/main 基点・ログイン修正1コミットのみ）→ **PR #5**
- `.next` 削除後のクリーン再ビルドで型チェック通過・全27ページ生成を確認（古いキャッシュ由来の estimate 型エラーは実害なしと判定）
- PR #5 CI 全通過 → main squash マージ（`0ef3c61`）→ Vercel 本番デプロイ `completed success`
- 本番 https://n-design.work で両アカウント password123 ログイン成功・旧アカウント無効・ログイン画面に開発注釈/文字化けなしを実機確認

> ⚠️ **セキュリティ申し送り（継続・重要度UP）**: 本番公開サイトの管理画面が 2 アカウントとも `password123`。総当たり数秒で突破され工務店サイト改竄リスク。CEO 承認済みだが、運用開始したら早急に強固なパスワードへ変更すべき。変更は今回同様 Management API で安全に実行可能。

### 8-6. 未完タスク → 9章で処理完了

---

## 9. 申し送り2件の処理（CEO「両方すすめて」指示）

### 9-1. 見積書ページ → 破棄・PDF運用に統一（完了）

stash@{0} を復元し `app/admin/estimate/page.tsx`（218行）をレビュー：

- **データ整合性**: 発行者情報（住所・口座 りそな銀行彦根支店 普通1081010・インボイス T9810453267161・氏名）を [クライミングコンサル発行者情報マスタ](../クライミングコンサル発行者情報.md)と人手照合 → **完全一致**。明細5項目・金額（小計180,000/税18,000/税込198,000）を正本 [2026-05-17-n-design-estimate.md](2026-05-17-n-design-estimate.md) と照合 → **完全一致**
- **Codex セカンドオピニオン**（CLAUDE.md 自律委任ポリシー準拠）で **HIGH リスク検出**: `"use client"` のため口座番号・インボイス番号が JS バンドルに含まれ、ログイン画面を出しても **未認証ユーザーが DevTools で機密情報を閲覧可能**。「ログイン必須で個人情報保護」という当該ページの目的を根本から無効化する設計欠陥
- **CEO 判断: 見積書はページ化せず PDF 運用に統一**。`app/admin/estimate/` 削除・`app/admin/page.tsx` の見積書 Link 取り消し・generated.ts 復元。`feat/admin-hero-editor` ブランチを origin と完全同期（未コミット変更ゼロ）。本番 `/admin/estimate` は元々 404（事業リポ・本番とも影響なし）
- 見積書は既存運用どおり consul/work の HTML → PDF → クラウドサインで手渡し（契約書・請求書と同じフロー）。正本: [2026-05-17-n-design-estimate.md](2026-05-17-n-design-estimate.md)

### 9-2. パスワード強化 → CEO 判断で一時的に password123 維持（完了）

セキュリティリスク（`password123` は既知漏洩PWランキング常連・総当たり数秒・本番公開サイトの管理画面で改竄リスク・2アカウント同一だとクライアント側漏洩が制作会社側に波及）を数値根拠付きで再提示。**CEO 判断: 運用開始までの一時措置として password123 のまま確定**（リスク明示承認）。両アカウント設定済・実機ログイン OK 確認済のため追加作業なし。

> ⚠️ **継続申し送り**: 運用開始時に強固な個別パスワードへ変更すべき。`/admin` アカウント設定タブが不調なら Management API（service_role）で安全に変更可能（本ログ 8-2 の手法）。

---

## 10. 最終状態（2026-05-18 確定）

| 項目 | 状態 |
|---|---|
| ヒーロー編集（/admin タブ） | ✅ 本番稼働・文字化けなし |
| トップ 8 セクション集約 | ✅ 本番反映（PR#4） |
| 固定メニュー管理ログイン導線 | ✅ 本番反映（PR#4） |
| ログイン: メール直接入力統一 | ✅ 本番反映（PR#5・`0ef3c61`） |
| 管理アカウント | `goodbouldering@gmail.com`（制作会社用）/ `admin@n-design.work`（クライアント用）両方 password123・ログイン OK |
| 旧 `admin@n-designs.com` | 無効（廃止） |
| 見積書ページ | 破棄（PDF 運用に統一） |

**残課題（CEO 判断待ち・実装不要）**: 運用開始時のパスワード強化のみ。

---

**最終更新**: 2026-05-18（申し送り2件処理完了：見積書ページ破棄・PW は一時 password123 維持確定。全タスククローズ）
