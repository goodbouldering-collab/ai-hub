# 2026-05-12 トラスト案件 アーキテクチャ決定ログ

## 文脈

CEO（由井辰美）が Claude.ai での要件定義セッションを完了し、**障害者グループホーム シフト管理
システム**の引き継ぎプロンプトを Claude Code に投入。実装フェーズに移行する初日。

## CEO 指示の主要決定

| 論点 | CEO 判断 | 影響 |
|---|---|---|
| ホスティング | **Vercel 集約に揃える**（仕様書原案の Cloudflare Workers は不採用） | 親 CLAUDE.md の Vercel 集約方針と整合・課金/観測性が一元化 |
| リポ配置 | `C:\VSCode\Project\トラスト\` で独立リポ | ビジネス21 配下統合案（仕様書末尾）は不採用 |
| Phase 1 スタッフ登録 | Bot 会話で合言葉方式の自己登録 | 17人規模で運用負担が小さく、表現も柔軟 |
| 事業関係 | トラスト=**完全独立事業**（ビジネス21 とは資本/業務とも分離） | consul の10事業目として登録、CFO 精算もグループ会社扱いしない |
| **親 CLAUDE.md の「LINE Webhook を Cloudflare 補完レイヤとして残す」方針** | **撤回** | **新規 LINE Bot 案件は全て Vercel に乗せる**。既存 4本（karatto-line-crm 等）は据え置き |
| AI モデル | Claude Opus 4.7（1M context） | シフト生成の制約推論が複雑なため Opus 採用・Sonnet は使わない |

## Claude Code 側の派生判断

| 論点 | 判断 | 理由 |
|---|---|---|
| プロジェクト構造 | monorepo (apps/worker + apps/liff) ではなく単一 Next.js | Vercel は1プロジェクト=1ドメインが綺麗・LIFF と API が同一オリジンなら CORS 不要・17人規模で monorepo は過剰 |
| 画像生成 | satori + Cloudflare Browser Rendering ではなく `@vercel/og`（内部で satori 使用） | Vercel 公式・Edge Function で動く・スタック統一 |
| 画像保存 | R2 ではなく Supabase Storage | 親 CLAUDE.md 共通ルール |
| LINE SDK | 自作ラッパーではなく公式 `@line/bot-sdk` | グッぼる側は自作だったが、ランタイム前提が違うので公式採用が筋 |
| Next.js 初期化 | `create-next-app` ではなく手書き10ファイル | `create-next-app` は日本語フォルダ名（トラスト）を npm package 名扱いして弾く（既知の挙動）・`--name` フラグも効かない |
| ローカルポート | 3010 | 既存9事業が 3001〜3009 を使用済み・10事業目で連番 |
| Supabase スキーマ修正 | 仕様書原文の SQL を順序入れ替え + CHECK 制約追加 | `staff_home_assignments` が `homes` より先に定義されており外部キー違反になる |

## 出力物（このターンで作成）

### `C:\VSCode\Project\トラスト\`（新規10ファイル）
- `package.json` — trust-shift / Next.js 15 / 必要依存のみ
- `tsconfig.json` / `next.config.mjs` / `tailwind.config.ts` / `postcss.config.mjs` / `next-env.d.ts` / `.gitignore`
- `src/app/layout.tsx` / `globals.css` / `page.tsx`
- `src/app/api/line/webhook/route.ts` — **HMAC-SHA256 署名検証実装済み**
- `src/app/liff/shift-request/page.tsx` / `shift-view/page.tsx` — プレースホルダ
- `src/lib/supabase.ts` / `line.ts` / `claude.ts`
- `supabase/migrations/0001_init_schema.sql` — 8テーブル + RLS skeleton + updated_at トリガ
- `supabase/seed.sql` — 勤務パターン + 棟マスタ初期値
- `.env.example` — 全12変数を文書化
- [CLAUDE.md](CLAUDE.md) — プロジェクト憲法
- `docs/REQUIREMENTS.md` — 仕様書（文字化けハンドオフの整形版）

### `C:\VSCode\Project\consul\`（更新）
- [トラスト.md](トラスト.md) 新規作成（事業情報ハブ）
- [CLAUDE.md](CLAUDE.md) 更新：9事業 → 10事業、地形図、事業略称テーブル（trust）、Codex 推奨方針表
- [work/2026-05-12-trust-architecture.md](work/2026-05-12-trust-architecture.md) 新規作成（このファイル）

### `C:\VSCode\Project\CLAUDE.md`（親憲法・更新）
- プラットフォーム横断比較表：Vercel 列に「LINE Webhook も Vercel」追記
- Cloudflare 向き案件説明：「既存 4本維持のみ、新規は Vercel」に書き換え
- 構成図補完レイヤ：「既存維持のみ・新規採用しない」と明示
- 判定フロー Q2：「LINE Webhook 単独では NO」と注記
- Cloudflare 例外パターン・Cloudflare 要点：同方針で書き換え

## CEO 未承認・次ターン以降の必要アクション

| アクション | 必要性 | タイミング |
|---|---|---|
| `npm install`（トラスト/） | 必須・大量ファイル落ちる | CEO 承認後の次ターン冒頭 |
| `clients.code-workspace` への登録 | VSCode CLIENTS パネル表示用 | `npm install` と同時 |
| [set-ports.js](set-ports.js) への 3010 追加 | ポート自動割り当て統合 | `clients.code-workspace` 更新と同時 |
| Vercel プロジェクト作成 | デプロイ準備 | 動作確認後・Phase 1 完了時 |
| Supabase プロジェクト作成 | DB 接続のため | `npm run dev` 起動前に必須 |
| LINE Developers チャネル作成 | Webhook URL 設定・テスト送信 | Supabase 完了後 |
| GitHub リポ作成 | バージョン管理 | CEO 明示指示後 |
| `STAFF_ENROLLMENT_CODE` の決定 | スタッフ自己登録方式 | 実装着手前に CEO と合意 |

## 残課題・確認したい論点

1. **トラストエージェントの法人格・契約形態**: consul/トラスト.md には「独立事業」と明記したが、
   CFO がインボイス処理する際に「個人事業主か法人か」「インボイス番号の有無」が必要。次回 CEO に確認。
2. **本番ドメイン**: `trust-shift.vercel.app` で始めるか、最初から独自ドメイン取るか
3. **管理者の LINE userId**: `ADMIN_LINE_USER_IDS` を埋めるために CEO 本人と運営担当者の userId を取得
4. **改修指導対応の帳票形式**: 「行政の運営指導時に必要な帳票」とは具体的にどの様式か（厚労省告示？県条例？）
5. **既存 Excel データの移行**: 過去のシフト履歴を Supabase に取り込むか、新規スタートか

これらは Day 2 以降の Phase 1 実装と並走して詰める。

## メモ: Cloudflare 撤退影響の整理

CEO 指示により「LINE Webhook を Cloudflare 補完レイヤとして残す」例外を撤回したが、**実害ある変更
ではない**:

- 既存 4本（karatto-line-crm 含む）は据え置き → 即時の移行コストなし
- 親 CLAUDE.md の文言が「新規 LINE Bot は Vercel」になっただけ
- トラストが新方針の1号案件として、Vercel での LINE Webhook 実装パターンを確立する

将来 4本も Vercel に移行する場合は別タスクで判断（D1 依存が強い karatto は移行コストが高いので
据え置きが妥当）。

## 追補: 2026-05-12 後刻 — トラスト=プラットフォーム化への構造変更

### CEO 追加指示

「トラストのアプリは他にも作る可能性があるためこのシフトアプリは管理システムの一つとして
構成して。ビジネス21のような構成で、アプリが増えるたびに / の下が増える感じ。
これは /home-shift として機能するように構成して。
できれば trust.vercel. など github も含め統一した trust にしてほしい。」

### 確定方針

| 項目 | 旧（午前の方針） | 新（CEO 追加指示） |
|---|---|---|
| リポの位置付け | シフト管理単独リポ（`trust-shift`） | **プラットフォーム**（`trust`）。アプリは `/<slug>` で増やす |
| プロジェクト構成 | Next.js src/ ベース | **src/ 廃止・app/ 直下にサブディレクトリ**（ビジネス21 と統一） |
| ルーティング | `/`=管理プレースホルダ、`/liff/*`=LIFF | `/`=ポータル（アプリ一覧）、`/home-shift/`=シフトアプリ、`/home-shift/liff/*`=LIFF |
| Vercel プロジェクト名 | `trust-shift` | `trust` |
| GitHub リポ | 未定 | `goodbouldering-collab/trust` |
| Supabase スキーマ配置 | `supabase/migrations/` | **`supabase/<app-slug>/migrations/`** に隔離（他アプリと混ざらない） |
| ドキュメント | `docs/REQUIREMENTS.md` | `docs/<app-slug>/REQUIREMENTS.md` |
| LINE Webhook | アプリごとに分ける案も検討 | **当面は `/api/line/webhook` 単一**（home-shift のみ）。2つ目アプリが出てから分割判断 |

### 構造変更による出力物（午後）

#### `C:\VSCode\Project\トラスト\`（書き換え）
- `src/` 全削除
- `app/layout.tsx` `app/globals.css` `app/page.tsx`（**ポータル**：home-shift カード1枚を表示・将来カード追加で拡張）
- `app/home-shift/page.tsx`（アプリトップ）
- `app/home-shift/liff/shift-request/page.tsx` / `shift-view/page.tsx`
- `app/api/line/webhook/route.ts`（トラスト共通 webhook 入口・コメントで将来分割の方針明記）
- `lib/supabase.ts` `lib/line.ts` `lib/claude.ts`（共通ライブラリ）
- `supabase/home-shift/migrations/0001_init_schema.sql` ← 旧 `supabase/migrations/` から移動
- `supabase/home-shift/seed.sql` ← 同上
- `docs/home-shift/REQUIREMENTS.md` ← 旧 `docs/REQUIREMENTS.md` から移動
- `tsconfig.json`: `@/*` を `./*` に（src/ を取った）
- `tailwind.config.ts`: content globs を `./app/**` `./components/**` `./lib/**` に
- `package.json`: name を `trust-shift` → **`trust`**・description を「トラストエージェント 業務管理プラットフォーム」に
- [CLAUDE.md](CLAUDE.md): 「単一アプリ」→「プラットフォーム」前提で全面改訂、「アプリを追加するときのルール」を追記

#### `C:\VSCode\Project\consul\トラスト.md`（書き換え）
- 「収容アプリ一覧」テーブル追加（home-shift だけ・今後追記）
- Vercel プロジェクト名・GitHub リポ名を `trust` で固定
- ディレクトリ構成図をプラットフォーム前提に書き換え

### この構造変更の効果

| 観点 | 効果 |
|---|---|
| **2号アプリ追加コスト** | `app/<新slug>/page.tsx` + `supabase/<新slug>/migrations/` + `lib/<新slug>/` + `docs/<新slug>/` を切るだけ。共通の Supabase/LINE/Claude クライアントは `lib/` で再利用 |
| **DB 統合 vs 分離** | Supabase は1プロジェクトで複数アプリの schema を内包。RLS で各アプリのテーブルを保護。**プロジェクト分割しない**ことで Pro $25/月の課金を1本に抑える |
| **Vercel プロジェクト数** | 1本（`trust`）。Pro $20/月の Vercel Team 集約ルールに沿う・アプリ増えても課金増えない |
| **デプロイ単位** | 1アプリ修正でも全アプリ巻き込みで再デプロイされる弱点はあるが、Next.js のビルドキャッシュで実害小・SaaS 化など分離要件が出たら別プロジェクトに切り出し |
| **LINE 統合** | スタッフが1つの公式アカウントで複数業務システムを使える（リッチメニューでアプリ切替）将来像が描ける |

### CEO 未承認・次ターン以降の必要アクション（更新版）

| アクション | タイミング |
|---|---|
| `npm install`（トラスト/） | CEO 承認後の次ターン冒頭 |
| `clients.code-workspace` への登録 + [set-ports.js](set-ports.js) に 3011 追加（3010 は ai-hub・修正済） | 上と同時 |
| Vercel プロジェクト `trust` 作成（API or ダッシュボード） | 動作確認後 |
| Supabase プロジェクト作成 → `supabase/home-shift/migrations/0001` 実行 | `npm run dev` 起動前 |
| LINE Developers でチャネル作成 → Webhook URL を `trust.vercel.app/api/line/webhook` に設定 | Supabase 完了後 |
| GitHub リポ `goodbouldering-collab/trust` 作成 + 初回 push | CEO 明示指示後 |
| `STAFF_ENROLLMENT_CODE`（合言葉）の文言決定 | 実装着手前 |

