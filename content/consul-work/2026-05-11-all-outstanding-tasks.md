# 9事業横断・残タスク棚卸し（2026-05-11）

各事業情報ファイル（`<事業名>.md` × 9）と親 CLAUDE.md・直近 git log から
「明示的に残っている宿題」を本部視点で集約。
KPI 欄が「(記入待ち)」のものは、依頼があれば別途ヒアリングする前提で本リストには含めない。

---

## 🔥 ブロッカー級（着手判断が要る）

### 1. ファディー再生成（Phase 1）
- **出典**: [fadie.md:55-58](../fadie.md), 親 CLAUDE.md「集約マイグレーション計画 #6」
- **状態**: 2026-05-01 方針確定 → Vercel プロジェクト枠 (`prj_ipW2tSduDUDtmrRyv3bgaTz6hRGF`) 確保のみ・**未デプロイ**
- **次アクション**: みんなのWA の `api/*` 構造を雛形に Vercel プロジェクト初期化（Phase 1）+ Supabase `fadie` スキーマ設計（Phase 2）
- **依存**: みんなのWA を流用元として参照（[minanowa.md:60](../minanowa.md)）
- **注意**: 旧 Workers / D1 (`fadyhikone-production` / `webapp-production`) は Phase 5 まで残置
- **判断待ち**: そもそも事業詳細・ターゲットが未確定。再生成と並行して「何を作るのか」を整理する必要あり

---

## 🟡 営業開始前チェックリスト（CEO の意思決定タイミング次第）

### 2. ビジネス21 営業開始 5 ステップ
出典: [business-21.md:41-46](../business-21.md)
1. Vercel Hobby → **Pro ($20/月) 昇格**（商用利用の規約クリア）
2. **独自ドメイン取得**（候補: `business21.com` / `business21.jp`）
3. Vercel に独自ドメイン追加 + DNS 切替（Cloudflare DNS + Vercel ホスト）
4. `NEXT_PUBLIC_SITE_URL` を独自ドメインに更新 → Redeploy
5. Supabase Auth の Site URL / Redirect URLs に独自ドメイン追加

→ 営業開始日が決まり次第まとめて実行。**いつ営業開始するかが起点**。

### 3. Nデザイン Round 12 の優先順位決定
出典: [n-design.md:43](../n-design.md)
- 候補: **工程進捗トラッカー / お客様マイページ / 多言語対応**
- Round 11 まで完了 (2026-05-03)。次の弾の選定が止まっている
- **判断材料**: 営業現場で何が一番効くか（CEO ヒアリング必要）

---

## 🔵 Cloudflare 集約プロジェクト・残 Phase（ClimbHero）

### 4. ClimbHero Phase 3 / 5 / 6
出典: [climb-hero.md:62-77](../climb-hero.md)

| Phase | 内容 | ブロック理由 |
|---|---|---|
| Phase 3 | R2 アップロードAPI（アバター/サムネ） | **R2 Dashboard 有効化** が手動で必要 |
| Phase 5 | Cloudflare Access で `/admin/*` SSO 保護 | **Zero Trust Dashboard 設定** が手動で必要 |
| Phase 6 | Stripe Customer Portal | サブスク開始時期の判断待ち |

→ Phase 3, 5 は **CEO が Cloudflare Dashboard で 1 アクション**するだけで動き出す。

---

## 🟢 運用クローズ系（様子見中→そろそろ判定）

### 5. Render Starter (みんなのWA) の完全削除
出典: [minanowa.md:47](../minanowa.md), 親 CLAUDE.md「集約マイグレーション計画 #5」
- 2026-04-30 09:06 suspend 済 → 完全削除は **「Vercel 安定運用 1〜2 週間確認後」**
- **本日 2026-05-11**＝ suspend から 11 日経過。**判定タイミング到来**
- アクション: Vercel 側のエラーログ・本番疎通を確認 → 問題なければ Render Dashboard から完全削除

### 6. Render keepalive ワークフロー全廃の検討
出典: 親 CLAUDE.md「Vercel 集約後の運用ルール #5」
- 「本マイグレーション計画完了次第、親リポ `render-keepalive.yml` も廃止」と明記
- 残存 Render プロジェクト: **0件**（minanowa suspend 後）→ 廃止条件は満たしている
- アクション: `.github/workflows/render-keepalive.yml` の matrix を空にする / ファイルごと削除

---

## 🟣 運用継続中の保留事項（緊急度低）

### 7. AIハブ・カラーミーテンプレ OAuth 権限問題
出典: [ai-hub.md:47, 78](../ai-hub.md)
- `COLORME_LIVE_TEMPLATE_ID=1064` への OAuth 権限不足のため、現状 **1086 を本番テンプレとして運用中**
- 本来運用：1086 = プレビュー、1064 = ライブ
- アクション: カラーミー OAuth スコープ再申請 or 1086 を恒久本番化する設計変更

### 8. ぐっぼる / カラット / notエステ の KPI 未記入
- KPI 欄が「(記入待ち)」のまま
- 本部として目標数字が無い＝施策評価ができない状態
- アクション: CEO ヒアリングで各事業の北極星指標 1〜2 個を決める

---

## ⚪ 本部側（consul）の宿題

### 9. 全事業の KPI ヒアリング → 事業情報ファイル更新
- 全 9 事業の `現在のKPI` がほぼ空欄
- このままだと marketer / advisor が施策提案の根拠を持てない

### 10. 進行中タスク欄の更新習慣
- 多くの事業ファイルの「進行中タスク」が「(記入待ち)」または古い
- 週次 or イベント発生時に自動的に更新する仕組み（pm エージェント運用）の整備

---

## 優先度サマリ（CEO 判断推奨順）

1. **🔥 ファディー：何を作るのか先に決める**（再生成は手段、目的が未確定）
2. **🟡 ビジネス21：営業開始日を決める**（決まれば一気に 5 ステップ実行）
3. **🟢 みんなのWA Render 完全削除 + keepalive 廃止**（即実行可・本日判定 OK）
4. **🟡 Nデザイン Round 12 選定**（営業に直結する候補から）
5. **🔵 ClimbHero Phase 3/5**（Dashboard 1 操作で進む）
6. **⚪ 全事業 KPI ヒアリング**（中長期の本部機能の基盤）
7. **🟣 AIハブ OAuth・KPI 記入**（運用の細かいクリーンアップ）
