# AIハブ整理仕分け — 削除するもの / 改造するもの / 残すもの

**作成日**: 2026-05-17（日）
**対象**: AIハブ（`C:\VSCode\Project\ai-hub\`）
**CEO 指示（2026-05-17）**:
1. 複雑になった情報を「削除するもの」と「改造するもの」に仕分けせよ
2. MD を全部 HTML 化する構造はやめろ（ややこしい）
3. 管理ページを開いたら「これからやること／これまでやったこと／日々のプロンプト」が出先(スマホ)から分かる集大成にする
4. 投稿・動画・ブログなど新規生成物を次々追加できるようタスクを整理（カレンダー・メール含む）

**前提**: 5/16 調査（[2026-05-16-ai-hub-ops-redesign.md](2026-05-16-ai-hub-ops-redesign.md)）で
「3パイプライン停止＋ai-hub.vercel.app が別 Next.js プロジェクトを配信」が確定済み。
本書はその上に「情報の物理的な整理（断捨離）」を重ねたもの。**実行はすべて CEO 承認後**（事業リポ書き込み = consul 鉄則）。

---

## A. 結論サマリ（先に要点）

| 区分 | 対象 | 件数/規模 |
|---|---|---|
| 🗑 **削除** | 移行残骸・スクショ墓場・MD→HTML 全件複製・古いアーカイブ JSON | 約 200 ファイル超 |
| 🔧 **改造** | ポータル生成（build_portal.py の MD 大量 HTML 化部分）・管理画面の入口 | 2 系統 |
| ✅ **残す（無傷）** | 公開ポータル本体・AI Watch パイプライン・講習資料・実績/講師ページ | コア資産 |
| 🆕 **新設** | `/ops` 単一ダッシュ（タスク/予定/プロンプトを“データで”出す。MD を HTML 化しない） | 1 画面 |

**設計思想の転換（最重要）**:
今は「**consul の work/*.md を全部 ai-hub に同期 → 全部 HTML 化して並べる**」。
これが「ややこしい」の正体。
→ 新方針：**MD は HTML 化しない**。`/ops` が JSON（`agents_status.json`）を読んで
**「重要タスク」「予定」「使うプロンプト」だけを構造化して描画**する。
work/*.md は“原文リンク”として持つだけ（全文 HTML 化＝廃止）。

---

## B. 🗑 削除するもの（ゴミ・残骸・重複）

### B-1. 確実に削除してよい（機能に無関係な残骸）

| パス | 中身 | 根拠 | リスク |
|---|---|---|---|
| `ai-hub/_tmp/` | 開発中スクショ 48枚（portal-*.png, admin-*.png 等） | デバッグ用画像置き場。本番・ビルドに不使用 | なし |
| `ai-hub/data/_migrate_chunk_*.sql`（6） | SQLite→Supabase 移行 SQL の分割 | 2026-04-21 の移行作業残骸。移行は完了済 | なし |
| `ai-hub/data/_migrate_chunks.json` / `_migrate_dump.json` | 同上 移行ダンプ | 同上 | なし |
| `ai-hub/outputs/archive/2026-04-*.json` | 日次収集の古い生 JSON（4月分） | NotebookLM 参照は `outputs/notebooklm/` 側。archive は内部中間物 | 低（要 §B-3 確認） |

> 合計の体感: `_tmp` 48 + `data/_migrate*` 8 + `archive` 数十 = **約 100 ファイル超が純粋なゴミ**。

### B-2. 設計転換に伴い削除する「MD 全 HTML 化」構造（CEO 指示②の本丸）

| パス | 中身 | なぜ消すか |
|---|---|---|
| `ai-hub/content/consul-work/*.md`（32件） | consul/work/ の MD を丸ごとコピーした塊 | **これを全 HTML 化しているのが「ややこしい」の原因**。`/ops` は JSON で要点を出す方式に変えるため、この“全文コピー＋全 HTML 化”は不要 |
| `build_portal.py` 内の consul-work 一覧 HTML 生成ロジック | 32 MD を `<details>` 等で全部ページに展開する処理 | 設計転換で廃止。`/ops` 側に「重要分だけ JSON 描画」へ寄せる |
| `.github/workflows/sync-consul-docs.yml` | consul → ai-hub に MD を全コピーする日次同期 | **要判断**：MD 全文同期が前提の仕組み。新方式では「要点 JSON だけ同期」に作り替えるので、現行のままなら停止 or 改造 |

> ⚠️ `sync-consul-docs.yml` は「削除」ではなく「**B-2 の設計転換で改造（全 MD コピー → 要点 JSON だけ）**」が正しい。完全削除すると同期が途絶える。§C-3 参照。

### B-3. 削除前に CEO 確認が要るもの（消すと困る可能性）

| パス | 確認したいこと |
|---|---|
| `outputs/archive/*.json` | NotebookLM や差分検出が過去 archive を遡る運用が無いか（CLAUDE.md は `notebooklm/` 保持を明記、archive は言及なし＝多分消してよいが念のため） |
| `outputs/full/`・`outputs/support_sns/` | 週次フル版・サポート SNS の生成物。AI Watch の正規出力なので**残す**側。誤って B 群に入れない |
| `data/history.db` | **絶対削除しない**（差分検出の土台。CLAUDE.md 明記）。`thumb_cache.json` も生成キャッシュなので残す |

---

## C. 🔧 改造するもの（捨てずに作り変える）

### C-1. `site/build_portal.py`（1285行）

- **残す**: 公開ポータルトップ（ヒーロー・実績数値・サービス・FAQ・講師）の生成。これは AIハブの“顔”で無傷。
- **改造**: consul-work 32 MD を全部 HTML に流し込んでいる部分を**撤去**。トップに出すのは「重要タスク N 件のサマリ」だけにし、本文は持たない（リンクで原文へ）。
- 方針: build_portal.py は公開面に専念。運用面（タスク/予定/プロンプト）は `/ops`（C-3）に分離。

### C-2. 管理画面の入口（`/admin` 系）

- 5/16 調査で **`/admin` は本番 404**（ai-hub.vercel.app が別 Next.js プロジェクトを配信）。
- これは**コードの問題ではない**ので「改造」ではなく **R0: Vercel ダッシュボードのドメイン/プロジェクト紐付け是正**（CEO 判断）が先。
- `/admin` 配下（記事生成・カラーミー・Shopify・docs・chat）は**機能としては残す**。ただし「集大成ページ」は `/admin` に混ぜず `/ops` で新設（C-3）。

### C-3. `/ops`（集大成ダッシュ）— 新設だが既存資産の“組み替え”なので改造扱い

- データ源は既存 `outputs/agents_status.json`（`build_agents_status.py` が work から抽出）。**新 DB を作らない**。
- **MD を HTML 化しない**。JSON の以下キーだけを画面に出す:
  - `tasks_open`（重要タスク・優先度順でトップ固定）← CEO 指示③④の核
  - `schedule`（Google Calendar スナップショット）← scheduler 経由（5/16 設計 G1）
  - `prompts`（**新規キー**：日々使う定型プロンプト集。後述 D）
  - `per_business_recent` / `cma_apps`（これまでやったこと＝活動ログの要約）
- `sync-consul-docs.yml` は「全 MD コピー」→「**要点 JSON（agents_status 相当）だけ同期**」に改造。

---

## D. 🆕 新設（CEO 指示③④を満たす最小追加）

| 追加物 | 役割 | 置き場 |
|---|---|---|
| `/ops` 単一ページ | スマホで開く集大成。①重要タスク ②予定 ③プロンプト ④活動ログ の4ブロック。MD 全文は出さずリンクのみ | `site/static/ops/index.html` + `api/ops/index.ts`（Basic 認証は既存 withAdmin 流用） |
| プロンプト・ライブラリ | 「投稿」「動画台本」「ブログ」など定型生成プロンプトを登録・複製・コピー。新規生成物を次々足す入口 | `config/prompts.yaml`（YAML 1ブロック追加で増える＝コード触らない方式。CLAUDE.md の sources.yaml と同じ思想）|
| 予定スナップショット | Calendar を読むだけ JSON 化（作成・変更しない） | `consul/google_ops/scripts/export_schedule_snapshot.py`（5/16 設計 P1） |

> プロンプトを YAML で持つ理由：CEO の「投稿/動画/ブログを次々追加したい」に対し、
> **コードを打たずに `prompts.yaml` に1ブロック足すだけで新ジャンルが増える**形にする
> （`sources.yaml` で RSS を足すのと同じ運用＝CLAUDE.md の既存思想に合致）。

---

## E. 実行順序（依存関係つき・すべて CEO 承認後）

| 順 | 作業 | 区分 | リポ書込 | 前提 |
|---|---|---|---|---|
| **0** | 本仕分けを CEO 承認（削除対象 §B の最終 OK/NG） | 判断 | なし | — |
| **1** | §B-1 ゴミ削除（_tmp / _migrate* / archive） | 削除 | ai-hub（要 CEO） | 承認 |
| **2** | R0: ai-hub.vercel.app の紐付け是正（5/16 R0） | 改造 | Vercel 設定（要 CEO） | 承認 |
| **3** | `sync-consul-docs.yml` を「要点 JSON 同期」に改造／`daily.yml` 復旧 | 改造 | ai-hub Actions（要 CEO） | 2 |
| **4** | build_portal.py の MD 全 HTML 化撤去 + §B-2 の content/consul-work 削除 | 削除+改造 | ai-hub（要 CEO） | 3 |
| **5** | `config/prompts.yaml` 新設 + `/ops` ページ実装 | 新設 | ai-hub（要 CEO） | 4 |
| **6** | scheduler の予定スナップショット連携（G1） | 新設 | consul（鉄則対象外）+ ai-hub 取込（要 CEO） | 5 |

---

## F. CEO への確認ポイント（ここだけ決めれば走れる）

1. **§B-1 のゴミ（_tmp 48枚 / _migrate* 8件 / archive の4月JSON）は削除してよいか？**（機能影響なしと判断）
2. **§B-2：`content/consul-work/*.md` 32件の“全文 HTML 化”を廃止**してよいか？（＝MD は ai-hub に全文コピーせず、`/ops` は要点 JSON だけ表示。原文は consul/work/ にありリンクで飛ぶ）
3. **プロンプト集を `config/prompts.yaml` で持つ方式**でよいか？（コード不要で投稿/動画/ブログのジャンルを足せる）
4. 個人カレンダー（`lossismore`）を `/ops` に載せるか、事業（`goodbouldering`）だけにするか（5/16 Q4 から継続。プライバシー判断）

---

**最終更新**: 2026-05-17（v1・整理仕分け確定。実行は §F の CEO 回答待ち）
