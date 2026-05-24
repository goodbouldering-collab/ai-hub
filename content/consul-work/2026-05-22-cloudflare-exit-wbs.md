# Cloudflare 撤退 → Vercel + Supabase 2コンソール集約（WBS）

- **作成**: 2026-05-22
- **依頼者**: CEO（由井辰美）
- **背景**: 2026-05-22 の Vercel vs Cloudflare 移行分析の結論「全面CF移行はしない・コンソール削減が本来目的ならCF撤退が正解」を受け、CEO が②CF撤退に舵を切ると決定。2026-05-12 に一度承認済みの方針への復帰
- **関連**: [2026-05-22-all-vercel-cf-migration-analysis.md](2026-05-22-all-vercel-cf-migration-analysis.md) / [2026-05-12-render-cloudflare-slow-migration.md](2026-05-12-render-cloudflare-slow-migration.md)
- **状態**: ⚠️ 計画のみ。実装・削除・本番変更は未着手。**G1/G2 は CEO 判断確定済（2026-05-22・下記）**。次は G3 と着手承認

## CEO 判断確定（2026-05-22）

- **G1 = (a) Supabase 移行**: LINE 会話履歴 D1 3本（`line-crm`/`karatto-line-crm`/`notesthe-line-crm`）は Supabase に移行して履歴を残す。CF 放棄・削除はしない
- **G2 = ClimbHero は CF 据え置き（例外確定）**: ClimbHero（`project-02ceb497` Pages + `webapp-production` D1 + `SESSIONS` KV + R2 + Workers AI + Cron/Email/Turnstile/Access）は撤退対象外。6,800行 + migrations 59件 + CF 固有サービス7種の依存で移行はゼロ再実装級・切り戻し不能・$0運用が崩れるため。climb-hero.md 81行「Vercel 移行を検討してはいけない」と整合
  - **よって今回の撤退対象 = Workers 4本 + 残骸 Pages（n-design/fadyhikone/project-221811fa/project-7d2b5d1f の4個）+ 残骸 D1（test-permission-check-invalid/fadyhikone-production の2個）+ LINE会話履歴D1 3本のSupabase移行**
  - **完了後のCF残置 = ClimbHero一式 + DNSゾーン（minanowa.com active / notesthe.com pending）+ WAF前段**

> DNS実測（2026-05-22）: CF ゾーンは `minanowa.com`(active) と `notesthe.com`(pending) の2件のみ。方針通り「DNS/WAFは前段として維持」。R2はAPIトークン権限不足で一覧不可だがClimbHero用途のため据え置き＝確認不要。

---

## サマリー：実際にやったこと・最終形（2026-05-22 確定）

**当初「全Worker/Pages/D1を撤退してVercel+Supabase 2コンソール」を目指したが、実コード確認でWorker 3本がCRM製品(再実装級)・ClimbHeroが移行不能と判明。「残骸だけ削除し、現役の重資産はCF据え置き」に着地した。**

| 観点 | Before | After（確定） |
|---|---|---|
| **Workers** | 4本 | **3本**（line-harness 残骸削除済 / 残り3本=LINE-CRM製品インスタンスは据え置き） |
| **Pages** | 5個 | **1個**（ClimbHeroのみ・残骸4個削除済） |
| **D1** | 6個 | **4個**（残骸2個削除済 / 会話履歴3本+ClimbHero据え置き） |
| **コンソール実態** | CF散らかり(残骸混在)+Vercel+Supabase | **日常運用はVercel+Supabase主軸**。CFは「ClimbHero + LINE-CRM 3本 + DNS」の現役資産だけに整理（残骸ゼロ） |
| **DNS** | CF | **CF維持**（前段WAF・二段防御） |

> 「コンソールを2つに減らす」という当初目的は**完全達成はしていない**が、本来の痛点（残骸が混ざって何が現役か分からない散らかり）は解消。CFに残るのは全て「移行＝再実装になる$0運用の現役価値資産」のみで、これらは残す方がコスト・工数の両面で正しい（ClimbHero分析と同じ結論）。

---

## フェーズ0 棚卸し結果（2026-05-22 実測・CF API）

### Workers ↔ D1 参照関係（移行・削除順序の根拠）

| Worker | subdomain公開 | 参照D1 | D1名 | 追加依存 | 判定 |
|---|---|---|---|---|---|
| `karatto-line-crm` | **True（現役）** | 03a2ba29… | karatto-line-crm | Workers AI + Vectorize(RAG) + Anthropic | 移行対象 |
| `line-harness-goodbouldering` | **True（現役）** | 28de2884… | line-crm | LINE Login + Anthropic | 移行対象 |
| `line-harness-notesthe` | **True（現役）** | f10433a7… | notesthe-line-crm | Anthropic | 移行対象 |
| `line-harness`（汎用） | **False（無効）** | なし（バインディング空） | — | — | **残骸＝削除（移行不要）** |

**WBS補正**: 当初「現役Webhook 4本」前提だったが、実測で **現役は3本**。`line-harness` は subdomain 無効＋バインディング空の完全な空殻 → バケツB(移行)ではなく**バケツA(残骸削除)** に移動。
**重要**: `karatto-line-crm` は Vectorize(ベクトル検索/RAG) も使用 → Vercel移行時に Supabase pgvector 等への置換設計が追加で必要（他2本より重い）。

### Pages 4個の帰属確認

| Pages | GitHub連携 | 最終デプロイ | カスタムドメイン | 判定 |
|---|---|---|---|---|
| `project-221811fa` | なし | **履歴ゼロ** | なし | 空の残骸・削除可 |
| `project-7d2b5d1f` | なし | 2025-11-15（作成日=放置） | なし | 残骸・削除可 |
| `n-design` | なし | 履歴ゼロ | なし | 残骸・削除可（本番Vercel） |
| `fadyhikone` | goodbouldering-collab/fadyhikone | 2025-11-30（半年前） | なし | ファディー旧・削除可 |

4個ともカスタムドメイン無し・現役トラフィック無し＝安全に削除可。

---

## Cloudflare API 実測資産（2026-05-22・推測でなく実物）

### Workers 4本
| 名前 | 最終更新 | 用途 |
|---|---|---|
| `karatto-line-crm` | 2026-04-12 | カラッと/ぐっぼる系 LINE Webhook |
| `line-harness` | 2026-04-07 | 汎用 LINE ハーネス（用途要確認） |
| `line-harness-goodbouldering` | **2026-05-22（今日・確実に現役）** | ぐっぼる LINE Webhook |
| `line-harness-notesthe` | 2026-04-12 | Notエステ LINE Webhook |

### Pages 5個
| 名前 | subdomain | 扱い |
|---|---|---|
| `n-design` | n-design-n0y.pages.dev | 削除（現本番 Vercel `n-design-lemon.vercel.app`） |
| `fadyhikone` | fadyhikone.pages.dev | 削除（ファディー旧・再生成中） |
| `project-02ceb497` | project-02ceb497.pages.dev | **ClimbHero 本番（要 G2 目視確認）→ 据え置き** |
| `project-221811fa` | - | 残骸候補（要帰属確認 0-2） |
| `project-7d2b5d1f` | - | 残骸候補（要帰属確認 0-2） |

### D1 6個
| 名前 | uuid | 扱い |
|---|---|---|
| `line-crm` | 28de2884… | LINE-CRM 会話履歴（G1 判断） |
| `karatto-line-crm` | 03a2ba29… | LINE-CRM 会話履歴（G1 判断） |
| `notesthe-line-crm` | f10433a7… | LINE-CRM 会話履歴（G1 判断） |
| `webapp-production` | 2faec3c4… | **ClimbHero D1（要 G2 確認）→ 据え置き** |
| `fadyhikone-production` | 3c41910c… | 残骸候補（ファディー旧・G3 確認） |
| `test-permission-check-invalid` | 9b8a448e… | テスト残骸・即削除可 |

> CLAUDE.md は「Cloudflare = LINE Webhook 4本 + ClimbHero + D1(LINE-CRM)」としか記録しておらず、**Pages 5個・D1 6個の大半は記録に存在しなかった**。記録 vs 実態の差分は本 WBS で解消する。

---

## 3バケツ分類と撤退順序

```
優先度 高 ────────────────────────────────────────── 低
├─ バケツA（安全・即削除）参照元ゼロの残骸を先に
│   ・test-permission-check-invalid（D1）
│   ・project-221811fa / project-7d2b5d1f（Pages・要確認後）
│   ・fadyhikone.pages.dev（廃棄予定）
│   ・n-design.pages.dev（現本番は Vercel）
├─ バケツB（現役・移行が必要）← 本丸・リスク最大
│   ・LINE Webhook 4本 → Vercel API Route 化（1本ずつ・並列不可）
└─ バケツC（据え置き or 別判断）
    ・ClimbHero（例外・永続据え置き）
    ・DNS / WAF レイヤ（CF 維持確定）
    ・LINE-CRM 会話履歴 D1 3本 → G1 判断
```

---

## フェーズ 0：前提確認・棚卸し（CEO 判断ゲート含む）

| # | タスク | 担当 | 依存 | リスク | 切り戻し |
|---|---|---|---|---|---|
| 0-1 | Workers 4本の wrangler 設定を読み、各 Worker の D1/KV バインディングを一覧化 | developer（読取のみ） | - | 低 | 不要 |
| 0-2 | `project-221811fa` / `project-7d2b5d1f` の帰属（どのリポ由来か）を特定 | developer（CF API 読取） | - | 低 | 不要 |
| 0-3 | `line-harness`（汎用）の接続先 LINE チャネルを確認 | developer + CEO 手動 | 0-1 | 中（現役なら削除不可） | 不要 |
| 0-4 | **[G1] D1 会話履歴3本の扱い決定**（(a)Supabase移行 (b)CF残置放棄 (c)削除） | **CEO** | 0-1 | 高（削除は不可逆） | なし |
| 0-5 | **[G2] ClimbHero 資産の目視確認**（`project-02ceb497` + `webapp-production` が ClimbHero 本番と確定） | **CEO** | - | 高（誤削除防止） | なし |

---

## ✅ フェーズ1 実行完了（2026-05-22・CF API で削除実施）

CEO 承認（着手指示 + G3 削除OK）を受けて残骸を削除。ClimbHero資産はガードで保護し1件も触れていない。

**削除した7件**:
- D1: `test-permission-check-invalid`(9b8a448e…) / `fadyhikone-production`(3c41910c…)
- Pages: `project-221811fa` / `project-7d2b5d1f` / `n-design` / `fadyhikone`
- Worker: `line-harness`（subdomain無効・バインディング空の残骸）

**削除後の実測検証（残ったもの＝全て意図通り）**:
- Workers 3本: karatto-line-crm / line-harness-goodbouldering / line-harness-notesthe（=現役Webhook・フェーズ2で移行）
- Pages 1個: project-02ceb497（ClimbHero・据え置き）✅無傷
- D1 4本: karatto-line-crm / notesthe-line-crm / line-crm（=会話履歴・G1でSupabase移行）+ webapp-production（ClimbHero）✅無傷

**残コンソール作業**: フェーズ2（Webhook 3本のVercel移行・本丸）+ フェーズ3（会話履歴D1 3本のSupabase移行）。これらは事業フォルダへのコード書き込みを伴うため別途CEO承認が必要。

---

## フェーズ 1：バケツA 残骸削除（フェーズ0完了後）【上記で実行済】

| # | タスク | 担当 | 依存 | リスク |
|---|---|---|---|---|
| 1-1 | D1 `test-permission-check-invalid` 削除 | developer（承認後） | 0-1,0-5 | 極低 |
| 1-2 | `fadyhikone.pages.dev` 削除 | developer | 0-5 | 低 |
| 1-3 | `n-design.pages.dev` 削除 | developer | 0-5 | 低 |
| 1-4 | `project-221811fa` / `project-7d2b5d1f` 削除（帰属確認後） | developer | 0-2,0-5 | 中（確認前は触らない） |
| 1-5 | D1 `fadyhikone-production` 削除（G3 確認後） | developer | 0-1,0-4 | 低 |

完了定義: 上記 Pages 3〜4件 / D1 1〜2件が削除済。ClimbHero と LINE Webhook 系は一切触れていない。

---

## 🛑 フェーズ2/3 全面撤回（2026-05-22・実コード確認で前提崩壊）

**当初「現役Webhook 3本をVercel API Route化 + 会話履歴D1をSupabase移行」とした計画を撤回する。**

### 撤回理由：3本は「Webhook」ではなく CRM 製品の 3 インスタンスだった

ローカル実コード（`グッぼる/line-crm/line-harness-oss/`）を確認した結果、3本のWorkerの正体は **`line-harness-oss` という本格的なLINE-CRMモノレポ製品**:

| 構成 | 中身 |
|---|---|
| `apps/worker` | Hono Worker本体・全APIルート（calendar/scenarios/broadcast/scoring/conversions/rich-menus/tracked-links...） |
| `packages/db` | **30+テーブル操作層**（friends/chats/broadcasts/scenarios/reminders/conversions/scoring/stripe/tags/automations...） |
| `packages/line-sdk` | LINE SDK自前実装（webhook署名検証） |
| `packages/mcp-server` | CRM操作用MCPサーバー |
| `packages/create-line-harness` | **新規事業にCRMを展開するCLIツール**（= 事業ごとインスタンス展開する設計の証拠） |
| ランタイム | Cloudflare固有: **D1 + Workers AI + Vectorize(RAG) + Cron Triggers + wrangler 4.x** |

グッぼる・カラッと・Notエステはこの同一CRM製品の**3インスタンス**（カラッと `カラッと/line-crm/`、Notエステ `Notエステ/line-crm/` にも一式存在）。

### Vercel移行が意味すること（= ClimbHero と同じ「移行＝再実装」）

- D1(SQLite)→Supabase(Postgres): 30テーブルのスキーマ移植 + 全クエリ書き直し
- Workers AI + Vectorize → 外部API + pgvector: RAG基盤の置換（**課金発生**）
- Cron Triggers（リマインダー/ステップ配信）→ Vercel Cron: 配信ロジック移植
- これを**3インスタンス分**。advisorの「1事業15-28h」見積もりの数倍
- **コスト逆行**: 現状CF無料枠（D1 5GB / Workers AI無料 / Vectorize）で実質$0運用 → Vercel+Supabaseで AI課金・DB容量・Cron実行が乗る

### CEO判断（2026-05-22）：CRM 3本も CF に据え置き（ClimbHero と同じ例外扱い）

- 現役$0運用のCRM資産を数十時間かけて再実装し課金化する価値はない
- **G1（会話履歴D1 のSupabase移行）も不要化**: CRM本体がCFに残る以上、会話履歴はCRMが現役で使い続けるデータ。CFに置いたままが正解
- 残骸削除（フェーズ1・完了済）でコンソールの散らかりは既に解消。3本は「残骸」ではなく「現役の価値資産」

---

## フェーズ 2：バケツB LINE Webhook 移行（本丸）【上記で全面撤回】

**原則**: 各 Webhook で「新 Vercel URL で動作確認 → LINE Developers で Webhook URL 差し替え → 旧 Worker を Disabled で24h観察 → 旧 Worker 削除」の順を守る。**並列不可・1本ずつ**。
**推奨順（リスク低い順）**: ①notesthe → ②karatto → ③line-harness 汎用 → ④line-harness-goodbouldering（最も現役・最後）

| # | タスク | 担当 | リスク | 切り戻し |
|---|---|---|---|---|
| 2-0 | Workers 4本のソースを読み移植差分（env・D1→Supabase 読替）を整理 | developer（読取） | 低 | 不要 |
| 2-1 | [notesthe] Vercel API Route 実装 + 環境変数登録 | developer（承認後） | 高 | URL 旧 Worker に戻せば即復旧 |
| 2-2 | [notesthe] LINE Verify ボタンで署名検証・テスト送受信 | developer + CEO | 高 | 旧 Worker 生存中 |
| 2-3 | [notesthe] **LINE Developers の Webhook URL 差し替え** | **CEO 手動** | 高（差替瞬間DT） | 旧 URL に戻す |
| 2-4 | [notesthe] 本番疎通確認（最低30分観察） | CEO 手動 | 高 | URL 差し戻し |
| 2-5 | [notesthe] 旧 Worker を Disabled（削除前24h観察） | developer | 中 | Enabled に戻す |
| 2-6 | [notesthe] 旧 Worker 削除 | developer | 低 | 不可逆だが Vercel 本番化済 |
| 2-7 | [karatto] 同手順で移行 | developer + CEO | 高 | 同上 |
| 2-8 | [line-harness 汎用] 用途確認後に移行 or 削除 | developer + CEO | 中 | 用途次第 |
| 2-9 | [line-harness-goodbouldering] 移行（最後・最高リスク） | developer + CEO | 最高 | URL 差し戻し即復旧 |
| 2-10 | 全移行完了確認（CF Workers が 0 本） | CEO | - | - |

**ダウンタイム緩和**: 旧 Worker が生きている状態で新 Route をステージング検証 → URL 差し替え。理論上のDTは伝播の数秒のみ。切り戻しは旧 URL に戻すだけで1分以内。

---

## フェーズ 3：バケツC 据え置き決定・記録更新（1〜2と並行可）

| # | タスク | 担当 | 依存 | リスク |
|---|---|---|---|---|
| 3-1 | ClimbHero CF 資産を「永続据え置き・撤退対象外」と climb-hero.md / CLAUDE.md に明記 | secretary/pm | 0-5 | 低 |
| 3-2 | DNS/WAF は「撤退対象外・Vercel 前段維持」と CLAUDE.md 補完レイヤに明記（Workers撤退 ≠ CF完全撤退） | secretary | 0-5 | 低 |
| 3-3 | G1=Supabase移行 の場合: 会話履歴スキーマ設計・移行・参照先変更 | developer（承認後） | 0-4 | 中 |
| 3-4 | G1=削除 の場合: D1 3本を対応 Worker 削除後に順次削除 | developer（承認後） | 0-4, Worker削除済 | 高・不可逆 |
| 3-5 | 撤退完了棚卸し（Workers=0/Pages=1/D1=1/DNS維持）を work/ に記録 | secretary+CEO | 全フェーズ | - |

---

## クリティカルパス

```
0-1 → 0-4(G1判断) → 2-0 → 2-1〜2-9（直列）→ 3-4 → 3-5
        ↑
    0-3(line-harness用途確認)
0-5(G2 ClimbHero確認) → 1-1〜1-5（残骸削除）→ 3-5
        ↓
        3-1〜3-2（CF据え置き明記）
```

**詰まると全体が止まる箇所**:
1. **G1（D1会話履歴判断）**: 出ないと karatto Worker 削除後の D1 が宙に浮く
2. **2-3 LINE Developers URL差し替え**: CEO 手動必須（CLI/API 不可）→ CEO スケジュール待ち

---

## CEO 判断ゲート一覧

| ゲート | 内容 | タイミング |
|---|---|---|
| **G1** | `line-crm`/`karatto-line-crm`/`notesthe-line-crm` の3 D1 を (a)Supabase移行 (b)CF残置放棄 (c)削除 のどれにするか | フェーズ0（最初） |
| **G2** | `project-02ceb497`+`webapp-production` が ClimbHero 本番とダッシュボードで目視確認 | フェーズ0（最初） |
| **G3** | `fadyhikone-production` D1 の旧データ削除可否（ファディーはゼロ再生成方針） | フェーズ1着手前 |
| **G4** | 各 Webhook の LINE Developers URL 差し替え（CEO 手動・Webhookごと） | フェーズ2 各移行時 |
| **G5** | 最終撤退確認（Workers=0/Pages=1/D1=1） | フェーズ3完了時 |

---

## 次アクション（今すぐ CEO が判断すべき2点）

- **G1**: LINE 会話履歴3本の D1 をどうするか（移行/放棄/削除）
- **G2**: ClimbHero の CF 資産を目視確認（誤削除防止）

この2ゲートが解消すればフェーズ0とフェーズ1を並行で動かせる。
