# Notエステ トップページ刷新（グラスモーフィズム＋インタラクティブ＋SEO）

日付: 2026-05-22
事業: notエステ（not-este）
対象: `C:\VSCode\Project\Notエステ\web\app\(frontend)\page.tsx` 他

## 依頼

他エステサロンのSEOを研究し、トップを「最高に使いやすく反応のあるページ」に。最新のインタラクティブ＋グラスモーフィズムで洗練させる。

## 方針（CEO確認済み）

- 刷新範囲: ヒーロー＋全体演出
- 配色: 現状ゴールドを洗練（ブランド継続性維持）
- push範囲: デザイン改修6ファイルのみ（作業ツリーに別作業=admin認証/Supabase SSRの未コミット分が混在していたため選択コミット）

## SEOリサーチ要点（2026最新）

- エステ利用者の60%超がネット予約 → 予約導線の摩擦最小化が最重要
- ローカルSEO/MEO + NAP統一 + Instagram連携が必須
- 「地域名×施術名」キーワード、E-E-A-T（料金・実績明示）

## 実装内容

- `app/globals.css`: glass/glass-strong/glass-dark/card-glass、text-gold-gradient、heading-rule、float-slow/shimmer/pulse-ring keyframes、.reveal、reduced-motion補強
- `tailwind.config.ts`: backdropBlur/shadow-glow/gold-radial 拡張
- `components/Reveal.tsx`（新規）: IntersectionObserverでスクロールリビール（一方向trigger・reduced-motion即表示）
- `components/StickyCTA.tsx`（新規）: ヒーロー通過後に現れる追従予約バー（モバイル下部固定/PC右下フロート、inertでフォーカス制御）
- `components/BgVideo.tsx`（新規）: reduced-motionで動画pause→ポスターのみ
- `page.tsx`: ヒーロー刷新（信頼指標バー・浮遊グロー・パルスCTA）、全セクションReveal+card-glass化、JSON-LD（Service+AggregateOffer / FAQPage）追加

## Codex レビュー反映（ISSUE 4件＋WARN 複数）

- StickyCTA: aria-hidden→inert
- 背景動画: reduced-motion pause（BgVideo新設）
- Service JSON-LD: url/provider住所・電話追加、price=0オファー除外
- 1要素BreadcrumbList削除（Googleが無視するため）
- pulse-ring/float-slowをreduced-motionで明示停止、float装飾にwill-change
- card-glassのbackdrop-filter除去（多数同時表示のFPS対策）、全a要素にnoreferrer、装飾sectionにaria-label

## 検証

- `npm run typecheck` 通過
- `npm run build` 通過（HTTPガード含む）
- 安全ゲート①ビルド②秘密情報なし③意味ある単位（admin作業を巻き込まず選択コミット）→ 全クリア

## 結果

- commit 4dd7b67 → origin/main push 済（Vercel自動デプロイ）
- 本番: https://notesthe.vercel.app
- 注: コミットメッセージ先頭に `@ ` が混入（here-string渡しの副作用）。機能影響なし・push済みのためforce整形は見送り

2026-05-22 codex:codex-rescue（review相当） 発火（not-este/実装直後セカンドオピニオン/ISSUE4件指摘→反映）
