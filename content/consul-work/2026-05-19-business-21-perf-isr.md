# ビジネス21 サイト表示の急激な遅延 — 原因と恒久対策

- 日付: 2026-05-19
- 事業: ビジネス21（外国人技能実習・監理団体）
- 依頼: 「サイト表示が急激に遅くなったので早くして」
- 本番: https://business21.vercel.app / リポ: goodbouldering-collab/business21

## 主因（特定済み）

トップ `app/page.tsx` の `export const dynamic = 'force-dynamic'`。
2026-04-29 のトップ CMS 化（コミット `37f8aa2`）で混入。

- 全訪問者が毎リクエストで Supabase `admin_settings` を `maybeSingle()` で都度クエリ
- Vercel の静的キャッシュ / ISR が完全無効化 → CDN ヒット 0・毎回 Function + DB 1 往復
- Supabase Free は 7 日無アクセスで pause（CLAUDE.md 記載）。復帰負荷とアクセス増が重なり体感悪化
- トップ内容（homepage 設定）は管理画面で月数回しか変わらないのに全員が編集鮮度コストを負担

複合要因: `about/system` / `legal/[id]` / `news/[slug]` が `force-dynamic` と
`revalidate` を併記しており、Next.js 16 では force-dynamic が勝って ISR が死に毎回 SSR していた。

## 対策（実施・本番反映済み）

コミット `75fb5f7`（main push 済・Vercel 自動デプロイ）。

| ファイル | 変更 | ビルド後 |
|---|---|---|
| app/page.tsx | searchParams 除去・純粋 ISR `revalidate=300` | `○ Static 5m` |
| app/preview/page.tsx（新規） | 下書き専用・force-dynamic・noindex | `ƒ Dynamic`（設計通り） |
| components/public/HomeBody.tsx（新規） | / と /preview で本体共有（サーバーコンポーネント） | — |
| app/about/system/page.tsx | force-dynamic 撤去（revalidate=3600 活かす） | `○ Static 1h` |
| app/legal/page.tsx | force-dynamic → revalidate=300 | `○ Static 5m` |
| app/legal/[id]/page.tsx | force-dynamic 撤去（revalidate=60 維持） | `ƒ Dynamic`（後述） |
| app/news/[slug]/page.tsx | 同上 | `ƒ Dynamic`（後述） |
| components/admin/HomepageSettingsTab.tsx | プレビュー導線 /?preview=draft → /preview | — |

安全ゲート: ① `npm run build` ✓ Compiled successfully ② 秘密情報直書きなし → 両クリア後 push。

## 残課題（今回スコープ外・改善余地）

`/legal/[id]` `/news/[slug]` は `generateStaticParams` 未定義のため `ƒ Dynamic` のまま。
ただし `revalidate=60` は機能しており force-dynamic 時代の「毎回 SSR」より改善。
完全静的化には記事 ID/slug の事前列挙が必要で影響範囲が広がるため別案件とする。
トップ（最優先・主因）は完全解決済み。

## Codex セカンドオピニオン結果

`/codex:rescue` でコミット 75fb5f7 をレビュー → 3 観点すべて CLEAN。
機能退行なし・ISR/静的分離は意図どおり・サーバー/クライアント境界の崩れなし。
「無期限に古いデータが出続けるケースは存在しない（最大でも各 revalidate 秒で更新）」と確認。

2026-05-19 codex:codex-rescue 発火（ビジネス21/事業フォルダ修正直後のセカンドオピニオン/結果: 3観点CLEAN・退行なし）
