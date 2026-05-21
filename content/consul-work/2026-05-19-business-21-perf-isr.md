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

## 第2フェーズ（2026-05-19/20）: 真因はリージョンだった

ISR 化後も体感が遅いとの追加指摘で再調査。

### 失敗した遠回り

最初に「470KB の重い HTML/RSC ペイロード」を疑い HomePageClient を SC 化
+ next/dynamic 化のリファクタを実装したが、実測で gzip 後 +18KB 悪化させた
だけで HTML サイズも変わらなかった（next/dynamic ssr:true は HTML を減らさない /
SC 化も HTML として出力されるので物理サイズは不変）。設計判断を誤った。
未コミットだったので破棄し 75fb5f7 に復帰。教訓: 構造改修の前に必ず Lighthouse 等の
公式トレースで真因をボトルネック別に数字で確定すること。

### 真因（Chrome DevTools perf trace で確定）

ISR 静的化は正常動作していた（X-Nextjs-Prerender:1 / X-Vercel-Cache:HIT /
DB往復ゼロ）。にもかかわらず TTFB が遅い理由は別軸:

- X-Vercel-Id: `kix1::iad1::xxx` = 日本(kix1)受信→米バージニア(iad1)処理
- vercel.json に regions 未指定→ Vercel 既定の iad1（米東部）で ISR キャッシュ /
  Function が配置される
- 結果、日本ユーザーは X-Vercel-Cache HIT でも毎回**太平洋を往復**
- Document download 自体は 2ms。圧縮(br)も効いている。
  ボトルネックは純粋に**配信リージョンの地理的距離**

### 対策

vercel.json に `regions: ["hnd1"]` を1行追加（コミット 1c1d782）。
初回試行 d215f72 は "//regions" というコメント疑似プロパティを混ぜたため
Vercel schema の additionalProperties:false で拒否→ Builds:0ms の ERROR。
コメントキー削除で 1c1d782 が READY。

### 効果（Chrome DevTools 公式トレース実測）

| 指標 | iad1(米) | hnd1(東京) | 改善 |
|---|---|---|---|
| **TTFB** | 1,314 ms | **69 ms** | -1,245 ms (-95%) |
| **LCP** | 2,230 ms | **1,092 ms** | -1,138 ms (-51%) Good 判定圏内 |
| CLS | 0.00 | 0.00 | 完璧維持 |
| Total（curl 平均） | 約5秒 | 約0.7秒 | -86% |
| DocumentLatency 警告 | 「FCP/LCP 1,212ms 短縮可能」 | インサイト消失 | 解消 |

LCP の「Good」基準 2,500ms を大きく下回ったため緊急対応はここで一段落。
残る Render delay 1,022ms（14セクション巨大DOM・インラインSVG 156個）は
別軸の構造改善案件として保留（緊急性なし）。

2026-05-19 codex:codex-rescue 発火2回目（ビジネス21/HTML軽量化リファクタ実装委任/結果: Codex使用枠上限で実行不可・Claude 単独実装→破棄）

## 第3フェーズ（2026-05-20）: 背景HD動画3MBが残りの体感遅延

サーバー TTFB は hnd1 配信で 70〜200ms に改善したのに「やはり遅い」と CEO 指摘。
最初 Supabase 経由の遅延を疑われたが、トップは前回 ISR 化で Supabase 不要構造に
なっていた（admin_settings は revalidate=300 のバックグラウンド再生成時のみ）。

真因: components/public/Background.tsx で全公開ページに fixed inset-0 で常駐し、
Pexels の HD 1920x1080 mp4 を **preload="auto" autoPlay loop** で読み込んでいた。
- 1ファイル目 = 2.9MB (Content-Length: 3001114 で確認)
- 全ページ (トップ/about/area/countries/legal/news 等) で並行ダウンロード
- サーバーが速くてもブラウザ側で外部 CDN 通信とレンダリングを圧迫

対策（コミット d7ea95d）: video 要素と source を削除。装飾レイヤー(グラデーション/
ぼかし球体/グリッド/ビネット)は純 CSS なので維持。ベースグラデーションを濃く調整。

実測効果:
- Lighthouse の **ThirdParties / ImageDelivery 警告が消失**（Pexels CDN 通信ゼロの直接証拠）
- LCP 1,233ms / Good 圏内維持
- メインスレッド・通信帯域・モバイルデータ通信量への負荷を大幅軽減
  （Lighthouse 瞬間スコアには出にくいが、スクロール時のカクつき・
  4G/5G環境・データ通信量の負担は確実に改善）

教訓: サーバー側 (Vercel/Supabase) ばかり疑っていたが、CEO の「背景の動画では?」
という観察が決定打だった。レンダリング側の重いメディア (特に外部 CDN の動画 autoPlay)
は数字に出にくいが体感を確実に壊す。次回からは初手で実 HTML/ネットワークタブを
ブラウザ側も含めて見る。
