# 2026-05-20 みんなのWA: コース機能 + 事前決済「準備中」化 + トークン漏洩対応

## 何をやったか

1. **第28回交流会の事前決済を「準備中」表示に**: イベントカードに `prepaymentStatus="preparing"` を持たせると、詳細モーダルの「事前決済」ボタンが disabled + 黄色「準備中」バッジに切り替わる
2. **AI講習・相談・伴走パックの商品カタログ機能を新設**: `courses` テーブル + API + TOPページセクション + 管理画面タブまで一式
3. **CEO提供HTMLから3コース初期データを投入**
4. **ADMIN_TOKEN 漏洩のローテーション要請**（並行で CEO 側が対応中）

## 本番反映済みの成果物

- 第28回イベント: https://minanowa.com/event/event-1779267553910-9bjyh488q
  - 詳細モーダルで「事前決済」ボタンがグレーアウト + 「準備中」バッジ表示
  - 既存の他イベントは従来通り（`prepaymentStatus` 未設定 = 既存挙動）
- TOPページ: https://minanowa.com/#courses
  - 「AI講習・相談・伴走パック」セクション
  - 3カラム固定グリッドで3コース表示
  - 補助金対応バッジ（緑）/ 予約ボタン（オレンジ）/ 詳細モーダル
- 管理画面: https://minanowa.com/admin (要admin)
  - 左ナビに「コース（AI講習）」追加
  - 一覧テーブル + 「新規作成」モーダル + 編集/削除

## 投入した3コース

| ID | カテゴリ | タイトル | 価格 | 補助金 |
|---|---|---|---|---|
| course-1779284939843-azmhc7zsk | consultation | AI個別相談 60分 | 2,200円〜5,500円 | なし |
| course-1779284945321-0lt348vga | workshop | AI講習会 120分（月一回・定員8名） | 5,500円 | あり |
| course-1779284950091-ewn7uretg | package | AI伴走パック 6回 | 月額100,000円×6ヶ月 | あり |

予約URLは Square Appointments（個別相談 / 伴走パック）+ minanowa.com 内（講習会）。

## 技術的なポイント

### 新規ファイル
- `supabase/migrations/0006_courses_and_prepayment.sql` — courses テーブル + events.prepayment_status カラム
- `api/courses/index.js` — GET 公開一覧（published=true / sortOrder昇順 でフィルタ）
- `api/admin/courses/index.js` — POST 新規作成
- `api/admin/courses/[id].js` — PUT 更新（partial OK・spreadマージ）/ DELETE 削除

### 既存ファイルの変更点
- `lib/supabase-store.js` — courseFromRow / courseToRow 関数追加、readAll/writeAll で courses 並行 fetch + upsert + syncDeletes。`eventFromRow/ToRow` に `prepaymentStatus ⇔ prepayment_status` の双方向マッピングを追加
- `lib/data-cache.js` — `_loadFromSupabase` の return shape と `EMPTY_DATA` に `courses: []` を追加（**ここを忘れると Supabase に保存されても `/api/courses` が常に空配列になる**。初回 push 後にこのバグで踏み、追加 commit で修正）
- `index.html` — `<section id="courses">` 追加、`renderCourses()` + `showCourseDetail()` 実装、`loadAll()` で `fetch('/api/courses')` 追加
- `admin.html` — メニュー項目「コース（AI講習）」追加、`panel-courses` HTML追加、`renderCourseTbl()` / `openCourseForm()` / `saveCourse()` / `deleteCourse()` 実装、`courseModal` 追加

### prepaymentStatus の UI フロー
1. `index.html` の詳細モーダル生成箇所で `ev.prepaymentStatus==='preparing'` を判定
2. true なら `pay-stripe disabled` クラス + `<span class="pay-prep">準備中</span>` バッジ + `onclick` なし
3. `selectPayMethod` 側でも保険として `if(el.classList.contains('disabled')) return`
4. `registerEventWithPayment` 側でも保険として stripe 選択時に preparing なら onsite にフォールバック + Toast 通知

### 二段ガード（フロント onClick 取除 + 関数内 early-return）の意図
本番 UI ボタンを完全に押せない状態にすることが第一目的だが、開発者ツール等で `class` を書き換えられても push を成立させない設計。バックエンド API 側のガードは入れていない（CEO 承認の A 方針＝フロントのみ）。万一バックエンドを直接叩かれた場合は Stripe 課金は走るが、それは admin token 経由でしかできず、現状は問題視しない判断。

## ADMIN_TOKEN 経路の運用ノウハウ

`/api/admin/*` への直接 POST/PUT は `.env.local` の `ADMIN_TOKEN` を `x-admin-token` ヘッダで送るだけで通る。Claude/CLI から `curl` で叩ける運用が確立した。

```bash
ADMIN_TOKEN=$(grep '^ADMIN_TOKEN=' .env.local | cut -d= -f2-)
curl -X POST https://minanowa.com/api/admin/courses \
  -H "Content-Type: application/json" \
  -H "x-admin-token: $ADMIN_TOKEN" \
  --data-binary @payload.json
```

**注意**: `source <(... | sed 's/^/export /')` 構文を使うと bash の declare -x が stderr に出力され、シェル環境変数全部が画面に流れる現象が今回発生。シークレットを巻き添えで露出させないため、今後は `ADMIN_TOKEN=$(...)` 形式の単純な変数代入のみ使うこと。

## ⚠️ トークン漏洩インシデント（同セッション内発生）

ADMIN_TOKEN を `source <(...)` で読み込もうとした際、想定外に bash の `declare -x` が stderr に流れ、以下のトークンが画面に**平文で露出**:

| トークン | 用途 | 危険度 |
|---|---|---|
| ANTHROPIC_API_KEY | Anthropic API課金 | 最高（不正課金リスク） |
| VERCEL_TOKEN | Vercel全プロジェクト管理 | 高（本番改変可能） |
| SUPABASE_ACCESS_TOKEN | Supabase Management API | 高（DB全権限） |
| GITHUB_PERSONAL_ACCESS_TOKEN | GitHubリポ書込 | 中 |
| RENDER_API_KEY | Render API | 低（既に撤退済） |
| ADMIN_TOKEN（minanowa） | 管理者API | 中（minanowa限定） |

CEO は**並行してダッシュボードでローテーション実施中**。完了次第:
- `.env.local` の ADMIN_TOKEN を新値で差し替え（Vercel env 更新後）
- `~/.bashrc` または環境変数定義箇所の各 token を新値で更新

教訓: bash プロセス置換は `set -a; . file; set +a` か `KEY=$(grep ... | cut ...)` に置換する。`source <(grep ... | sed ...)` は二度と使わない。

## 残課題

1. **トークンローテーション完了確認**（CEO 作業）
2. **第28回交流会バナー画像**（前タスク）: 別ファイル `2026-05-20-minanowa-event28-banner-brief.md` に指示書あり。CEO 判断待ち
3. **コースの予約URL**: 講習会のみ `https://minanowa.com/` という汎用URLになっている。本来は `minanowa.com/#courses` か Square で講習会用のサービスID を発行するのが望ましい

## 委任ログ

このタスクは Claude 単独で完遂。Codex 委任なし。
- 入口判定: 「事業フォルダ書き込みあり・既存パターン踏襲・1事業内完結」→ Claude 単独で十分と判断
- 結果: 5 commit に分かれた（うち1つは data-cache shape 漏れの fix）。総差分: 約 440 行追加 / 10 行削除
