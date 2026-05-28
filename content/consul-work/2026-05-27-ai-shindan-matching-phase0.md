# AI診断マッチング（RebuildMatch）Phase 0 生成ログ

- **日付**: 2026-05-27
- **事業略称**: ai-shindan-matching（新規・既存10事業外）
- **配置**: `C:\VSCode\Project\AI診断マッチング\`（CEO指示で本番事業フォルダとして新規作成）
- **スタック**: Next.js 15.5.18 (App Router) + TypeScript / Anthropic SDK + OpenAI SDK + Google Places API
- **ポート**: 3010（既存 3001-3009 と衝突回避）

## 何を作ったか（Phase 0）

URL を入れると実クロール → **Claude × OpenAI の2社AIが3パス合議** → SEO/MEO/LLMO/JSON-LD を各100点診断 → 改善指示（何を/なぜ/どう/優先度）→ 直せる登録エンジニアにマッチ → 見積もり依頼導線（モック送信）。

### CEO 追加要件の反映

1. **診断軸を SEO/MEO/LLMO(AIO)/JSON-LD の4軸×100点に完全差し替え**（元SPECの5軸 STRUCTURE等は廃止）
2. **MEO は Google Places API でGBP実データ照合**（住所/店名抽出→GBP突合。キー未設定ならAI推定）
3. **Claude + OpenAI 2社AI × 3パス（初稿→相互批判→統合判定）ルーティング合議**。各軸に「両AI一致/要確認」検証バッジ
4. **改善点ジャンルにマッチするエンジニアプロフィール**（skill_tags + 業種/プラットフォーム/地域/返信目安）
5. **トップに「なぜ信頼できるか」を前面**（2社合議・3回検討・実測根拠・直したくなる指示の4点）

### 主要ファイル

- `lib/skills.ts` — 診断軸とスキルタグの共有enum（単一の真実）
- `lib/crawl.ts` — 機械クロール（title/見出し/JSON-LD/AIボット許可/住所）
- `lib/places.ts` — Google Places API でGBP照合
- `lib/diagnose.ts` — 2社AI×3パス合議エンジン（モデル: claude-opus-4-7 / gpt-4o）
- `lib/engineers.ts` — シード＆マッチング（Phase1でSupabase RPCへ）
- `app/api/diagnose/route.ts` — 診断API（キーはサーバ側 .env のみ）
- `app/page.tsx` / `components/ClientFlow.tsx` / `components/EngineerFlow.tsx`

## 検証

- `npm run build` 成功（型エラー解消済）
- dev 起動・home 200・信頼性セクション描画確認・API空URL→400 確認
- Next.js は CVE 回避のため 15.1.4 → 15.5.18（patched backport）に更新。critical RCE 解消、moderate 2件（postcss 由来・transitive）残

## 残（次フェーズ・要CEO確認後）

- Phase 1: Supabase接続/DDL/診断保存
- Phase 2-3: Stripe（詳細$5・サブスク$9/$90）+ webhook
- Phase 4: 見積もり実送信（Resend）+ ダッシュボード
- clients.code-workspace / set-ports.js への登録（親基盤変更=CEO明示指示が必要なため未実施）
- git init / GitHub / Vercel 連携（未実施）

## 追補（2026-05-27 同日・CEO要件深掘り）

CEO の「ディープリサーチで的確性を検証」要件に対し、**根拠ゲート（evidence gate）**を追加実装:
- 各改善指示(fix)に `evidence`（実測の裏付け）と `verified`（機械照合結果）を持たせた
- `verifyEvidence()` が AI の evidence 文字列を crawl/GBP の観測トークンと照合。裏が取れない高優先指摘がある軸は agreement を「両AI一致」→「一部相違あり」へ自動ダウングレード
- confidence 文に「N件中M件が実測裏付け確認済み」を開示
- UI: 各fixに「✓ 実測裏付けあり / △ 要確認(推定)」バッジと「根拠: ...」行
- 「Codexで診断」は本番サーバから叩けないため **OpenAI(GPT) API で代用**することをCEO承認 → UI表記を「Claude × GPT の2社AI合議」に正確化
- トップの信頼性②を「根拠ゲート」に差し替え

## 追補2（2026-05-28・見積依頼の実送信）

CEO「見積依頼を登録エンジニアのメール/連絡先へ」に対応。alert モックを廃止し実導線化:
- `lib/engineers.ts` に `email`（+任意 lineUrl/tel）を追加。シードのマッチ材料に連絡先を含めた
- `lib/supabase.ts`: PostgREST直叩きの軽量保存（`SUPABASE_URL`/`SERVICE_ROLE_KEY` 未設定ならスキップ）
- `app/api/requests/route.ts`: 依頼受領→(任意)Supabase保存→(任意)Resend送信→`mailto` 情報(宛先/件名/診断結果込み本文)を返す
- `ClientFlow`: フォームを controlled 化し `/api/requests` を実呼び出し。返却 mailto でメーラー起動、LINE/電話の代替リンクも表示
- 送信手段=mailto（CEO選択）、保存=Supabase同時（キーあれば）。Resendキーがあればサーバ送信も併用
- スモークテスト: `/api/requests` が ok:true・正しいエンジニアメール・診断結果込みの percent-encoded mailto を返すことを確認（キー無し時は saved:false でmailtoは動作）
- build 通過（`/api/diagnose` + `/api/requests` の2 dynamic route）

## 追補3（2026-05-28・診断モジュール本体を設計指針②に沿って組み込み）

CEO提示の「サイト診断モジュール 設計指針」②を実装。デザインは先行作成の「ターミナル探査官」指示書に準拠。

**構造の刷新（4軸 → 2軸9観点）**:
- `lib/skills.ts` を Web診断5観点（安全性/信頼性/検索対応/AI対応/速さ）＋ MEO診断4観点（店舗情報/サイト整合/口コミ写真/運用継続性）の2トラック構造に再設計。WebとMEOは別軸で**合算しない**（指針どおり）
- `lib/scoring.ts`: 観点の加重平均・状態ラベル閾値・優先度=影響度×緊急度（機械判定）・安全性危険は最上位
- `lib/glossary.ts`: 用語の一元管理（識別子参照・3行説明・公式リンク）
- `lib/copy.ts`: スコア帯別/観点別の辛口ユーモアコピー（URLハッシュで安定選択）
- `lib/diagnose.ts`: 合議エンジンを2軸9観点に全面書き換え。issue に impact/urgency/estimateHours/evidence/verified/skillTags。見積受け渡し用の優先度順フラットリスト issueList を生成
- `lib/crawl.ts`: isHttps（安全性）・hasContactInfo（信頼性）を追加採取

**段階開示UI（ターミナル探査官）**:
- `ScanLog.tsx`: スキャンログ枠（`> ... [OK]/[SCANNING]/[WARNING]`・スキャンライン・カーソル点滅・**完了で即停止**）
- `Term.tsx`: 専門用語の対訳ツールチップ（glossary参照）
- `ClientFlow.tsx` 全面書き換え: 入口は最小限（verdict＋2トラック点数）→ トラックを開くと観点バー → 観点を開くと改善issue → 改善プラン（優先度順・残りはプロ向けレポートとして展開）→ 直せるエンジニア → 見積依頼。掘るほど深まる段階開示
- `page.tsx`: ヒーローをターミナル調＋2トラック訴求に
- globals.css: scanlog/scanline/cursor/term ツールチップのCSS追加

**未実装（指針の「次に詰める領域」・次フェーズ）**: 見積もり4パターン提示（制作会社/AI制作会社/AI担当/自作）、MEO半自動セルフチェックUI、PageSpeed API（速さの実測）、Places APIキャッシュ、業種別入口、結果ページ共有、同業ベンチマーク蓄積

build 通過（home 200・新ヒーロー/2トラック描画確認）。モデル: claude-opus-4-7 / gpt-4o。

## 追補4（2026-05-28・設計指針②の「次に詰める領域」を実装）

3項目を実装し全 build 通過:

1. **見積もり4パターン** (`lib/estimate.ts` + `EstimatePanel.tsx`): 従来制作会社／AI制作会社（推奨・バランス◎）／社内AI担当／自作。Web=単発改修費用・MEO=月額運用費用で別建て。issueList の estimateHours から時間単価×圧縮率でレンジ算出。制作会社系2つに「この方向で見積もり依頼」導線（エンジニア一覧へスクロール）。MEO自作は「技術力でなく継続力の問題」と注記（指針どおり）

2. **PageSpeed Insights API** (`lib/pagespeed.ts`): 「速さ」を実測化。`GOOGLE_PAGESPEED_API_KEY` 任意（キー無しでも公開APIは叩けるがレート制限）。失敗/タイムアウトは available:false でAI推定にフォールバック。diagnose の evidence に pagespeed を渡し、SPEED観点は performance を主根拠に。verifyEvidence も pagespeed 対応

3. **MEO半自動セルフチェック3出口** (`MeoSelfCheck` + `/api/meo` + `diagnoseMeoOnly`): GBP未検出時に①未開設（最大の指摘として赤字）②自動特定失敗→店名/住所を手動指定して再照合③対象外業種→診断出さない、の3出口。手動再照合は Web再診断せず MEOトラックだけ単発生成（軽量）

API は /api/diagnose・/api/meo・/api/requests の3本。build 通過・home 200 確認（途中の500はstale .next + ポート占有の事故で、rm -rf .next で解消＝コード問題ではない）。

**まだ未実装（指針の残り）**: Places APIキャッシュ、業種別入口、結果ページ共有（個別情報を含めない）、同業ベンチマーク蓄積。Supabase永続化(Phase1)・Stripe(Phase2-3)も未着手。

## 追補5（2026-05-28・設計指針②の残り「次に詰める領域」を実装）

3項目を追加し全 build 通過:

1. **Places APIキャッシュ** (`lib/places.ts`): プロセス内メモリTTL（24h・上限500件）。同一クエリ（店名+住所）の再診断はAPIを叩かずキャッシュ返却（従量課金対策）。found/not-found の両方をキャッシュ（課金済み結果のため）、transient失敗はキャッシュしない（再試行可能に）。恒久キャッシュはPhase1でSupabaseへ

2. **業種別入口** (`lib/industries.ts` + `/diagnose/[industry]`): 工務店/クリニック/飲食/美容室/士業の5業種をSSGで事前生成（ロングテールSEO）。各ページは担当者の困りごとに寄せた見出し（**「AI」を見出し第一語に置かない**指針を遵守）＋業種別 painPoints＋MEO訴求。同じ ClientFlow を heading/lead 差し替えで再利用。トップに業種チップ導線

3. **結果ページ共有** (`lib/share.ts` + `/share`): スコア（web/meo）と短い意訳文**のみ**をURL-safe base64でトークン化。**URL・住所・店名・GBP情報・改善本文は型レベルで含まない**（SharePayloadがweb/meo/copyしか持たない=個別情報を含めない設計を構造で担保）。`/share?d=<token>` で点数カードを表示し「自分も診断する」CTAへ。ClientFlowに「結果を共有（点数のみ・個別情報なし）」ボタン（クリップボードコピー）

build 通過（home/komuten/share すべて200・share はトークン復号して点数描画を確認）。SSGで業種5ページ事前生成。

**残り（指針＋ロードマップ）**: 同業種ベンチマーク蓄積（データ構造はPhase1のSupabase設計時に考慮）、Supabase永続化(Phase1)、Stripe(Phase2-3)、見積依頼の実送信高度化。

## Codex 委任ログ

2026-05-27 codex:rescue 発火（ai-shindan-matching/lib/diagnose.ts+crawl.ts のセカンドオピニオンレビュー/入口判定で重い新規実装と判断・High1+Medium3+Low1 検出、全5件を修正しbuild再通過）
