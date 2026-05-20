# 2026-05-20 AI講習・相談・伴走パックを minanowa から AIハブへ移管

## 経緯

午前中の作業で「みんなのWAにAI講習・相談・伴走パックの3コースを表示」したが、CEO 確認で **設置先が間違いだった**。
正しい掲載先は **AIハブ（ai-hub-jp.vercel.app）**。本タスクで:
1. みんなのWAの courses 機能を全撤去
2. 同じ内容を AIハブの TOP に新セクションとして追加

## 最終状態

### AIハブ（追加）
- URL: https://ai-hub-jp.vercel.app/#packages
- セクション名: 「AI講習・相談・伴走パック」（SERVICES の直下、FLOW の直前）
- 3カード: AI個別相談60分 / AI講習会120分 / AI伴走パック6回
- 補助金対応バッジ（緑）+ Square予約リンク（青グラデーション CTA）
- 末尾に補助金まとめ注記（滋賀県未来投資総合補助金 + 彦根市デジタル化補助金）

### みんなのWA（撤去）
- `/api/courses` → 404
- `#courses` セクション → 削除
- 管理画面の「コース」タブ → 削除
- Supabase `legacy_minanowa.courses` テーブル → DROP
- **`events.prepayment_status` カラムは残置**（第28回イベントで使用中）

## 変更内容

### minanowa リポ (`d29b492 revert(courses)`)
8 files changed, 15 insertions(+), 401 deletions(-)
- `api/courses/`, `api/admin/courses/` ディレクトリ削除
- `index.html`: courses セクション・CSS・JS（renderCourses / showCourseDetail）を除去、loadAll から fetch courses 除去、allCourses 変数除去
- `admin.html`: 「コース（AI講習）」メニュー項目・panel・modal・CRUD関数を除去
- `lib/supabase-store.js`: courseFromRow/courseToRow 関数 + readAll/writeAll の courses 処理を除去
- `lib/data-cache.js`: courses shape を EMPTY_DATA と _loadFromSupabase から除去
- `supabase/migrations/0007_drop_courses.sql`: 本番 DROP TABLE を反映する新規 migration（0006 は履歴として残置）
- 本番 Supabase: `drop table if exists legacy_minanowa.courses;` 適用済み

### ai-hub リポ (`3b8e229 feat(portal): SERVICES の直下に「AI講習・相談・伴走パック」セクション追加`)
- `site/build_portal.py`:
  - `_render_courses_packages()` 関数を新設（3カード生成）
  - main 関数で SERVICES の直後 `<section id='packages'>` として挿入
  - CSS `.packages-grid` / `.pkg-card` / `.pkg-cat` / `.pkg-price` / `.pkg-subsidy` / `.pkg-cta` / `.packages-note` を追加
- `site/dist/index.html`: ローカルビルドして `git add -f` で commit（毎日 GitHub Actions で再生成される運用）
- `outputs/agents_status.json`: build_portal.py 実行に伴う付随更新

## 設計判断

**なぜAIハブを「外出しYAML」にしなかったか**: minanowa では courses を Supabase + 管理画面で動的編集できる構造にしたが、AIハブは **静的サイト（build_portal.py で生成）** で、管理画面から個別商品を編集する設計になっていない。今回は「3コースが当面固定」と判断してハードコードで実装。
- 将来コース数が増える / 価格変更が頻繁になる場合は `config/services_packages.yaml` を新設して外出しする。今は不要

**ガード**:
- 安全ゲート全通過（Python構文・JS構文 in HTML scripts・秘密情報・http:// 直書き、全部クリア）
- 本番表示も chrome-devtools で目視確認済み（3カード + 補助金注記すべて意図通り）
- minanowa 撤去後の `/api/courses` 404 確認・他セクション（events/blogs）への副作用なし

## 残課題

- ADMIN_TOKEN を含む各種トークンのローテーション完了確認（CEO 並行作業中）
- 第28回交流会バナー画像（前タスクの指示書あり・CEO 判断待ち）

## 委任ログ

Claude 単独で完遂。Codex 委任なし。
入口判定: 「事業フォルダ書き込み2件・既存パターン踏襲・スコープ明確」→ 単独で十分。
結果: minanowa 1 commit / ai-hub 1 commit / consul 1 commit（この作業ログ）。
