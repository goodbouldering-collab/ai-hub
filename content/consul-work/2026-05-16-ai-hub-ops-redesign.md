# AIハブを consul の運用ハブ（スケジュール/タスク/エージェント可視化）に — 設計再構築

**作成日**: 2026-05-16（土）
**対象事業**: AIハブ（`C:\VSCode\Project\ai-hub\`）
**ステータス**: 📋 設計書（実装未着手）。事業リポ書き込みは [consul 鉄則](../CLAUDE.md)により **CEO 承認後**に着手
**確定方針（2026-05-16 CEO 回答）**:
- 公開ポータルは無傷、`/ops/` 配下に Basic 認証付き内部ダッシュを追加
- データは Google Calendar（scheduler 経由）+ [consul/work/](consul/work/) を**読むだけ**（二重管理しない）
- エージェントコントロールは**読み取り専用の状態可視化**（AIハブからエージェント起動はしない）

---

## 0. 最重要：これは「新規設計」ではなく「ギャップ補完」

調査の結果、ご依頼の機能の**過半は既に実装・稼働済み**だった。ゼロから設計し直すと既存実装を破壊・重複させる。正しい対応は「現状を確定し、欠けている2点だけを足す」こと。

### 既に動いているもの（事実・要再設計なし）

| ご依頼の機能 | 実装状況 | 実体 |
|---|---|---|
| タスク管理 | ✅ 稼働中 | [scripts/build_agents_status.py](../../ai-hub/scripts/build_agents_status.py) が `content/consul-work/*.md` を解析し `tasks_open` を抽出（現在15件） |
| エージェント可視化 | ✅ 稼働中 | `outputs/agents_status.json` に `per_business_recent` / `daily_histogram` / `cma_apps` を生成 → [api/admin/status.ts](../../ai-hub/api/admin/status.ts) が配信 |
| work/ ドキュメント閲覧 | ✅ 稼働中 | `/admin/docs`（`content/consul-work/` に32件同期済）+ `vercel.json` の `includeFiles` で関数バンドル |
| AI チャット（運用相談） | ✅ 稼働中 | [api/admin/chat.ts](../../ai-hub/api/admin/chat.ts) + `api/_lib/chat_context.ts` |
| Basic 認証ゲート | ✅ 稼働中 | `api/_lib/http.ts` の `withAdmin`（`ADMIN_USER`/`ADMIN_PASS`） |

### 欠けているもの（本設計書のスコープ）

| # | 欠落 | 影響 |
|---|---|---|
| **G1** | **スケジュール（Google Calendar）連携が皆無** | `agents_status.json` に予定フィールドなし。CEO は予定を AIハブで見られない |
| **G2** | **`/ops` 統合ビューがない** | タスク・エージェント状態は `/admin` 配下に散在。スケジュールと束ねた「運用ダッシュボード」入口が未整備 |
| **G3** | **データ同期経路が consul → ai-hub 片方向で手動依存** | `content/consul-work/` への同期が誰がいつ走らせるか不明確（後述 §4 で要確認） |

---

## 1. 現行アーキテクチャ（実測）

```
consul/work/*.md ──(同期: 経路要確認 G3)──▶ ai-hub/content/consul-work/*.md
                                                    │
                          scripts/build_agents_status.py（解析・タスク抽出）
                                                    │
                                                    ▼
                                      ai-hub/outputs/agents_status.json
                                                    │
                          ┌─────────────────────────┼─────────────────────────┐
                          ▼                         ▼                         ▼
                  /admin/status (JSON)       /admin/docs (本文閲覧)      /admin/chat (相談)
                          │
                  site/static/admin/index.html が fetch して描画
                          │
                  Basic 認証ゲート（withAdmin / ADMIN_USER・ADMIN_PASS）
```

- ホスティング: Vercel（`ai-hub.vercel.app`）。`api/**/*.ts` が Serverless Functions
- `agents_status.json` の生成タイミング: `scripts/build_agents_status.py` を**誰が叩くか**が現状不明（G3）。`run.py` 本体には組み込まれていない可能性が高い → §4 で要確認

---

## 2. 設計：欠落2点の補完（既存を壊さない原則）

### G1: スケジュール（Google Calendar）連携

**データソースは consul の既存資産を読むだけ**（CEO 確定方針）。新規 DB を作らない。

#### 経路A（推奨）: scheduler エージェント経由でスナップショット JSON 化

consul には既に `scheduler` エージェント + [consul/google_ops/scripts/refresh.py](consul/google_ops/scripts/refresh.py) の OAuth 基盤がある。これを使い、予定を JSON スナップショット化して AIハブに渡す。

```
consul/google_ops/scripts/refresh.py(get_credentials)
        │  ← 既存基盤。新規認証は作らない
        ▼
新規: consul/google_ops/scripts/export_schedule_snapshot.py
        │  今日〜14日先の予定を取得し JSON 出力
        ▼
consul/work/_schedule_snapshot.json （consul 側に置く・gitignore 検討）
        │  ← 同期は G3 と同じ経路に相乗り
        ▼
ai-hub/content/consul-work/_schedule_snapshot.json
        │
build_agents_status.py に schedule ローダ追加（既存 JSON に "schedule" キー追記）
        ▼
agents_status.json.schedule = [{date, time, title, account}]
```

- **AIハブ側に Google OAuth トークンを置かない**（漏洩面を増やさない）。認証は consul 側の既存基盤に閉じる
- スナップショットは**読み取り専用**。AIハブから予定の作成・変更はしない（誤登録防止＝ scheduler の既存原則と一致）
- `account_label` は `goodbouldering` / `lossismore` の2系統をそのまま持つ

#### build_agents_status.py への最小追加（既存ロジックを壊さない）

`_collect()` の戻り dict に `"schedule"` キーを足すだけ。既存の `recent_works` / `tasks_open` 等の生成には一切触れない。

```python
def _collect_schedule() -> list[dict]:
    snap = WORK_DIR / "_schedule_snapshot.json"
    if not snap.exists():
        return []   # 無ければ空。既存挙動に影響なし
    try:
        data = json.loads(snap.read_text(encoding="utf-8"))
        return data.get("events", [])[:30]
    except Exception:
        return []
```

`status.ts` は JSON をそのまま返すだけなので**変更不要**（`schedule` キーが増えても素通し）。

### G2: `/ops` 統合ビュー

`/admin` は既にカラーミー運用・記事生成で使われている**運用過密ページ**。スケジュール/タスク/エージェント可視化を混ぜると責務が膨らむ。**`/ops` を別入口として新設**し、`/admin` には手を入れない。

```
新規 rewrite (vercel.json):
  { "source": "/ops",  "destination": "/api/ops" }
  { "source": "/ops/", "destination": "/api/ops" }

新規ファイル:
  api/ops/index.ts            … withAdmin で Basic 認証ゲート（/admin と同じ仕組み流用）
  site/static/ops/index.html  … 統合ダッシュボード（既存 status.json を fetch して描画）
```

- 認証は `api/_lib/http.ts` の `withAdmin` を**そのまま再利用**（新しい認証機構を作らない）
- データ取得は既存 `/admin/status` の JSON を fetch（**新 API を増やさない**）。`/ops` の HTML から `/admin/status` を叩く
- 画面構成（読み取り専用・3 ペイン）:
  1. **今週の予定**（`schedule` キー・Calendar 由来）
  2. **オープンタスク**（既存 `tasks_open`・work/ 由来）
  3. **エージェント/事業アクティビティ**（既存 `per_business_recent` + `daily_histogram` + `cma_apps`）
- `/ops` からエージェント起動・予定変更は**しない**（CEO 確定：可視化のみ）

### vercel.json の差分（最小）

```jsonc
// includeFiles に schedule スナップショットを追加
"includeFiles": "{site/static/admin/**,site/static/ops/**,content/consul-work/**,outputs/agents_status.json}"
// rewrites に /ops を2行追加（既存は一切変更しない）
```

---

## 3. consul 側の追加（事業リポ外なので consul 鉄則の対象外）

| 追加物 | 場所 | 性質 |
|---|---|---|
| `export_schedule_snapshot.py` | [consul/google_ops/scripts/](consul/google_ops/scripts/) | 新規スクリプト。scheduler の「長いスクリプトは scripts/ に置く」運用に合致 |
| `_schedule_snapshot.json` | [consul/work/](consul/work/) | scheduler が生成。Markdown でないので index には載せない。`.gitignore` 追加を検討（個人予定が入るため）|

→ これらは consul リポ内なので CEO 事前確認の鉄則の対象外（work/ と google_ops/scripts/ は scheduler の書き込み許可範囲）。**ただし個人カレンダー予定を JSON 化する**点はプライバシー観点で CEO 判断が要る（§5 リスク）。

---

## 4. 要確認事項 → P0 調査結果（2026-05-16 実測・コード変更なし）

### Q1: `build_agents_status.py` は誰が・いつ実行しているか → **判明**

- **呼び出し元は1箇所のみ**: [site/build_portal.py:1249](../../ai-hub/site/build_portal.py)。`build_portal.py` の `main()` 冒頭で動的 import → `_mod.main()` で実行
- `build_portal.py` は `run.py` の `[7/7] CEO ポータルトップ生成` から呼ばれる
- `run.py` は `.github/workflows/daily.yml`（**JST 07:00 cron**）で日次実行され、`outputs/` を commit back
- **結論**: `agents_status.json` は **daily.yml 経由で毎日自動更新される設計**。`run.py` 単体には未組込だが `build_portal.py` 経由で連結されている（私の初版設計書の推測「run.py に未組込＝自動更新されない疑い」は **誤り**だった。連結経路が存在した）
- ⚠️ **ただし別の問題が判明**（後述 Q2/総括）：`agents_status.json` 最終コミットは 2026-05-15 だが、これは daily digest ではなく `feat(unify)` という**手動コミット**に巻き込まれた更新。直近の **daily.yml 起因コミットは 2026-05-13（`98d63f2 chore(ai-hub): daily digest 2026-05-13`）が最後**。5/14 以降 daily digest コミットが無い＝**daily.yml が 5/14 以降回っていない疑いが濃厚**

### Q2: consul→ai-hub の同期は誰が走らせるか → **判明・ここが最大の問題**

- 専用ワークフロー [.github/workflows/sync-consul-docs.yml](../../ai-hub/.github/workflows/sync-consul-docs.yml) が存在。**JST 06:00 cron** で consul を PAT clone → `content/consul-work/*.md` を全削除→再配置→commit back する設計
- 必要 Secret: `CONSUL_REPO_PAT`（consul プライベートリポ read 用 classic PAT・CEO 登録）
- **実測した同期ズレ（深刻）**:

| 指標 | 同期元 consul/work/ | 同期先 ai-hub/content/consul-work/ |
|---|---|---|
| 最新ファイル | **2026-05-16**（本設計書含む） | **2026-05-13**（3日古い） |
| `.md` ファイル数 | **41** | **32**（9件欠落） |
| 最終同期コミット | — | **2026-05-13 22:13 `daily sync 2026-05-13`** |

- **結論**: `sync-consul-docs.yml` は **2026-05-13 を最後に実行されていない**。原因候補: (a) `CONSUL_REPO_PAT` の期限切れ/未登録 (b) cron 自体の停止 (c) GitHub Actions の60日無活動による schedule 自動無効化。**実装より先にこれを直さないと、何を作っても3日以上古いデータを表示する箱になる**

### Q3: `/admin` の死活 → **実測：全 admin 系が 404（基盤レベルで死んでいる）**

```
GET https://ai-hub.vercel.app/        → 200（公開ポータルは生きている）
GET https://ai-hub.vercel.app/admin   → 404（Basic認証なら 401 が正常。404 は異常）
GET https://ai-hub.vercel.app/admin/status → 404
GET https://ai-hub.vercel.app/ops     → 404（未実装なので想定どおり）
```

- `/admin` が 401 ではなく **404** = Basic 認証以前に**ルーティング/関数自体が Vercel に存在しない**。[ai-hub.md](ai-hub.md) の「2026-05-13 時点で 404、要復旧」が**未解決のまま継続**

### R1: `/admin` 404 の根本原因究明 → **決定的に特定（2026-05-16 実測）**

`/api/admin/ping` を rewrite を経由せず直接叩いた応答が**動かぬ証拠**だった：

```html
<title>404: This page could not be found</title>
"buildId":"RVnh6Vn3L87wmUOB0ogRC"  "page":"/_error"  "nextExport":true
/_next/static/chunks/framework-5621ce43a28fe9a657d8.js
```

**これは Next.js アプリの 404 ページ**。だが ai-hub リポは Next.js ではない（`package.json` = `ai-hub-admin`、ビルドは Python `build_portal.py`、構成は素の Vercel Functions + 静的 HTML、Next.js 依存ゼロ）。

実測した全エンドポイント:

| URL | 結果 | 意味 |
|---|---|---|
| `/` | 200（`X-Vercel-Cache: HIT`）| 何かがトップだけ配信（キャッシュ or 別物）|
| `/profile.html` | **404** | `site/dist/profile.html` は実在するのに本番に無い |
| `/watch` | **404** | rewrite 対象の静的ページが無い |
| `/api/admin` | **404** | Function 自体が存在しない |
| `/api/admin/ping` | **404 + Next.js の `_error` ページ HTML** | **別の Next.js プロジェクトが応答している** |

**根本原因（確定）**: `vercel.json` や `withAdmin` 認証コードのバグではない。**`ai-hub.vercel.app` ドメインに、この ai-hub リポとは別の Next.js プロジェクトがデプロイ／ドメイン紐付けされている**（あるいは ai-hub の Vercel プロジェクトが Framework Preset を Next.js と誤検出してビルドし、`site/dist` も `api/` も成果物に含まれていない）。**`site/dist/` 静的配信も `api/**` Functions も、本番にそもそも存在しない。**

- **致命的な含意**: `/ops` を新規実装しても、デプロイ先が別物（または誤ビルド）である限り**同じく 404**。コードを1行書く前に、**Vercel プロジェクトのドメイン紐付け／Framework Preset／Root Directory／Build & Output 設定の是正が先**。これは Vercel ダッシュボード操作であり、コード変更ではない（要 CEO・`VERCEL_TOKEN` 経由の API 確認も可）
- 補足: [ai-hub.md](ai-hub.md) には本番 URL を `aiclimb.vercel.app`（404）→ `ai-hub.vercel.app`（200）に「訂正」した記録がある（2026-05-13）。だが今回の実測で **`ai-hub.vercel.app` の 200 はトップだけで、配下は全部別物の 404**。つまり「200 だから正常」という当時の判断自体が誤りで、**ドメインが正しい Vercel プロジェクトを指していない**可能性が高い

### Q4: 個人カレンダー（`lossismore`）を AIハブに載せてよいか → **CEO 判断事項（技術調査では決められない）**

- 技術的事実: `/ops` は現状 Basic 認証（`ADMIN_USER`/`ADMIN_PASS`）のみ。Vercel 上に個人予定 JSON を置くことになる
- これは技術ではなくプライバシーポリシーの問題。**CEO の明示判断が必要**（推奨デフォルト：まず `goodbouldering`（事業予定）のみ。`lossismore` は除外して開始）

### P0 総括：機能不足ではなく「パイプライン2系統が停止」が真の問題

| 系統 | 設計 | 実態 | 影響 |
|---|---|---|---|
| **Vercel デプロイ先** | ai-hub リポを配信 | **別の Next.js プロジェクトが応答（R1 確定）** | `site/dist` も `api/` も本番に存在しない＝**全機能の土台が無い** |
| `daily.yml`（agents_status 更新） | JST 07:00 毎日 | **5/13 を最後に停止疑い** | タスク/エージェント可視化データが陳腐化 |
| `sync-consul-docs.yml`（work/ 同期） | JST 06:00 毎日 | **5/13 を最後に停止（実測9件欠落・3日遅れ）** | そもそも新しい work/ が ai-hub に届いていない |
| `/admin`（閲覧基盤） | Basic 認証 Web | **404（デプロイ先が別物のため）** | 既存の可視化機能すら今ブラウザで見られない |

**3系統すべてが停止している。** スケジュール連携（G1）や `/ops`（G2）を実装しても、土台のこの3つが死んでいる限り無意味。**P0 の結論：新機能より先に「パイプライン復旧」が最優先タスク**。

---

## 5. リスクと緩和

| リスク | 緩和策 |
|---|---|
| 個人予定が Basic 認証のみで露出 | `lossismore` は AIハブに出さず `goodbouldering`（事業予定）だけにする選択肢を CEO に提示。または `/ops` を Vercel の追加保護下に |
| `agents_status.json` が自動更新されず陳腐化（既に発生中の疑い） | Q1 を解決し、`daily.yml` に `build_agents_status.py` 実行を追加（GitHub Actions 範囲なので別途設計） |
| 既存 `/admin` への巻き込み事故 | `/ops` を完全別ファイル・別 rewrite で新設。`/admin` 系ファイル（index.ts/status.ts/docs/chat.ts）には**1行も触れない** |
| consul→ai-hub 同期の二重管理 | 新規 DB を作らず JSON スナップショット片方向に限定（CEO 確定方針どおり） |

---

## 6. 実装フェーズ（P0 調査を踏まえ全面改訂）

P0 で「3系統停止」が判明したため、フェーズ順序を**復旧優先**に組み替えた。新機能（G1/G2）は復旧後。

| Phase | 内容 | 事業リポ書き込み | 前提 |
|---|---|---|---|
| **P0** | Q1〜Q4 調査 | なし | ✅ **完了（本書 §4）** |
| **R1** | ✅ **完了（本書 §4・原因確定）**：`/admin` 404 は `ai-hub.vercel.app` が **別 Next.js プロジェクトを指している**ことが真因。コードは無実 | なし（調査済） | — |
| **R0** | **Vercel ダッシュボード是正**（R1 の確定診断への対応）：`ai-hub.vercel.app` のドメイン紐付けを正しい ai-hub プロジェクトへ／Framework Preset を「Other」に／Root・Build/Output 設定確認。全機能の前提 | Vercel ダッシュボード or `VERCEL_TOKEN` API（**要 CEO**） | **最優先** |
| **R2** | **`sync-consul-docs.yml` 復旧**（`CONSUL_REPO_PAT` 期限/登録確認 → GitHub Actions schedule 再有効化 → 手動 `workflow_dispatch` で同期試走） | ai-hub の GitHub Secret/Actions（要 CEO：PAT 再発行が要る可能性） | R1 と並行可 |
| **R3** | **`daily.yml` 復旧**（schedule 自動無効化なら再有効化 → `workflow_dispatch` で agents_status 再生成確認） | ai-hub Actions | R2 と並行可 |
| **P1** | consul 側: `export_schedule_snapshot.py` 作成 + scheduler 試走（G1 のデータ源） | consul リポのみ（鉄則対象外）。ただし Q4 の CEO 判断必須 | R1〜R3 完了後 |
| **P2** | ai-hub: `build_agents_status.py` に `_collect_schedule()` 追加 | **要 CEO 承認** | P1 完了 |
| **P3** | ai-hub: `api/ops/index.ts` + `site/static/ops/index.html` + `vercel.json` rewrite 2行（G2） | **要 CEO 承認** | P2 完了・R1 解決 |

---

## 7. 結論（CEO への要点）

調査の結果、**当初の依頼「設計し直して」への最も誠実な回答は「設計より先に止まっている配管を直すべき」** という逆転した結論になった。

1. **新規設計は不要だった**。タスク/エージェント可視化・work 閲覧・AIチャットは**既に実装済み**。欠けていた新機能は①Calendar 連携 ②`/ops` 統合入口の2点だけ
2. **だが真の問題はそこではなく、もっと深刻だった**。R1 で **`/admin` 404 の真因が確定**：`ai-hub.vercel.app` は **ai-hub リポではなく別の Next.js プロジェクトを配信している**（`/api/admin/ping` が Next.js の `_error` ページを返した動かぬ証拠）。`site/dist` も `api/` も**本番に存在しない**
3. 加えてパイプライン2系統も停止：`sync-consul-docs.yml`（**実測9件欠落・3日遅れ**）、`daily.yml`（停止疑い）。ただしこれらも「正しいデプロイ先が無い」以上、復旧しても表示先が無い
4. **画面を新設しても完全に無意味**。コードは無実で、デプロイ先が別物。`/ops` を1行書いても同じ 404 になる
5. **次アクション提案**: コードではなく **R0（Vercel ダッシュボードのドメイン/プロジェクト紐付け是正）が唯一かつ最優先**。`ai-hub.vercel.app` を正しい ai-hub Vercel プロジェクトに向け直し、Framework Preset を「Other」に、Build/Output を確認する。これが直れば `/admin` は復活し、その後に R2/R3（パイプライン）→ P1〜P3（新機能）と進める

> ⚠️ R0 は Vercel ダッシュボード操作（または `VERCEL_TOKEN` API）であり、コード変更ではない。だが**どのプロジェクトに向けるか・現行の別 Next.js プロジェクトの正体は何か**は CEO しか知らない可能性が高い。**ここは CEO の確認なしに Claude が触ってはいけない領域**（ドメイン付け替えは他案件を巻き込む恐れ）。[consul 鉄則](../CLAUDE.md)準拠で、調査は完了・是正実行は CEO 判断待ち。

### CEO への質問（R0 を進めるのに必要）

- `ai-hub.vercel.app` のドメインは、いつ別の Next.js プロジェクトに付け替わった記憶があるか？（意図的か事故か）
- Vercel ダッシュボードに ai-hub 用の Vercel プロジェクト（Project ID `prj_e7vh73eF0KZpm8C49esnILvHO98o`・[ai-hub.md](../ai-hub.md) 記載）は今も存在し、最新コミットがデプロイされているか？
- その Project の本番ドメインは現在何になっているか？（`ai-hub.vercel.app` 以外に逃げている可能性）

---

**最終更新**: 2026-05-16（v3・R1 完了。`/admin` 404 の真因は「ai-hub.vercel.app が別 Next.js プロジェクトを配信」と確定。コードは無実。実装未着手・R0 是正は CEO 判断待ち）
