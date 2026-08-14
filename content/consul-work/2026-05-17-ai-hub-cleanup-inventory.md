# AIハブ整理仕分け — 削除するもの / 改造するもの / 残すもの

**作成日**: 2026-05-17（日）
**対象**: AIハブ（`C:\VSCode\Project\ai-hub\`）
**CEO 指示（2026-05-17）**:
1. 複雑になった情報を「削除するもの」と「改造するもの」に仕分けせよ
2. MD を全部 HTML 化する構造はやめろ（ややこしい）
3. 管理ページを開いたら「これからやること／これまでやったこと／日々のプロンプト」が出先(スマホ)から分かる集大成にする
4. 投稿・動画・ブログなど新規生成物を次々追加できるようタスクを整理（カレンダー・メール含む）

**CEO 確定回答（2026-05-17・本書 §F への回答）**:
- **F1 → ゴミ削除は `_tmp` と `data/_migrate*` のみ**。`outputs/archive/*.json` は念のため残す（NotebookLM 参照可能性を保留）
- **F2 → MD 全 HTML 化は廃止。ただし原文閲覧はページ内に残す**（外部リンク飛ばしではなく `/ops` 内で読める折衷。全文を“常時展開して並べる”のをやめ、必要時に開く方式へ）
- **F3 → プロンプト集は画面（`/ops` UI）から追加・編集・複製**する（YAML 手書き運用は不採用。裏の保存形式は YAML/JSON でよいが編集は UI）
- **F4 → Google Calendar 連携は後回し**。今回スコープは「重要タスク」「プロンプト」「活動ログ」の3本。予定は次フェーズ

**前提の訂正（2026-05-17 Vercel API 実測 — 5/16 設計の前提が誤りだったと確定）**:

> 🔴 **5/16 設計書（[2026-05-16-ai-hub-ops-redesign.md](2026-05-16-ai-hub-ops-redesign.md)）の核心結論「3パイプライン停止＋別 Next.js プロジェクト配信」は誤診断だった。**
> Vercel API（`VERCEL_TOKEN`）で実測した事実:
> - ai-hub プロジェクト（`prj_e7vh73eF0KZpm8C49esnILvHO98o`）は**正常稼働・毎日デプロイ継続**（直近 2026-05-17 07:37 READY、main から自動）
> - 正しい本番ドメインは **`aiclimb.vercel.app`**（verified）。`/`=200・`/admin`=**401（Basic 認証が正常動作）**・`/profile.html`=200・`/watch`=200 で**全機能生存**
> - `ai-hub.vercel.app` は **ai-hub の所有でない別ドメイン**（API で no-access、配下 404）。5/13 にこの誤 URL を「本番」と取り違え、以降ずっと 404 を踏んで「壊れている」と誤診断していた
> - **結論：R0（Vercel 是正）・R2・R3（パイプライン復旧）は全て不要だった。土台は健全。`/ops` は素直に実装できる**
> - ai-hub.md の本番 URL 記載は 2026-08-14 に正本（`aiclimb.vercel.app`）へ更新済

**実行はすべて CEO 承認後**（事業リポ書き込み = consul 鉄則）。

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

## E. 実行順序（5/17 Vercel 実測でブロッカー消滅 → 全面短縮）

> 5/16 設計の R0/R2/R3（Vercel 是正・パイプライン復旧）は **誤診断ゆえ全削除**。土台は健全なので「ゴミ掃除 → 表示改造 → /ops 新設」の3手だけで済む。

| 順 | 作業 | 区分 | リポ書込 | 前提 |
|---|---|---|---|---|
| **1** | ゴミ削除 — **`_tmp/`（48枚）と `data/_migrate_chunk_*.sql`・`_migrate_chunks.json`・`_migrate_dump.json`（8件）のみ**。`outputs/archive` は残す（F1） | 削除 | ai-hub（要 CEO 実行承認） | — |
| **2** | 「MD 全展開」の実体特定 → **`api/admin/docs/index.ts` が `content/consul-work/*.md` を全部ブラウザ展開しているのが“ややこしい”の本体**。`build_portal.py`（公開トップ）には MD 全展開は無く触らない。`scripts/build_agents_status.py` は既に理想の「要点 JSON 化」（tasks_open / recent_works 等）をしており**そのまま活かす**。step2 は実コード変更を step3 に統合（docs の全展開を `/ops` の「折りたたみ原文ビューア」に置換） | 改造（実体は step3 に統合） | ai-hub（要 CEO） | 1 |
| **3** | `/ops` ページ実装（§D 改訂版）。①重要タスク（トップ固定）②プロンプト集（画面で追加/編集/複製）③活動ログ ④原文ビューア（折りたたみ）。**正本 URL は `aiclimb.vercel.app/ops`** | 新設 | ai-hub（要 CEO） | 2 |
| ~~—~~ | ~~R0 Vercel 是正 / R2 sync 復旧 / R3 daily 復旧~~ | — | — | **不要（5/17 実測で健全と確定）** |
| **4** | （次フェーズ）Google Calendar 連携 = scheduler スナップショット（F4 で後回し確定） | 新設 | 次回設計 | 3 完了後 |

> ⚠️ 補足：`sync-consul-docs.yml` / `daily.yml` が「5/13 以降コミットが無い」のは事実だが、5/16 が疑った「停止」ではなく **(a) 出力に差分が無くコミット不要だった / (b) 別コミットに同梱された** 可能性が高い（デプロイ自体は毎日 READY）。step 2 着手時に Actions の run 履歴を1回だけ確認し、本当に schedule が回っているかを実測する（コード変更なしの確認）。

### §D 改訂（CEO 回答反映後の `/ops` 構成）

| ブロック | 中身 | F 回答の反映 |
|---|---|---|
| ① 重要タスク | `agents_status.json.tasks_open` を優先度順・**トップ固定**。これからやること | F3=画面で完結 |
| ② プロンプト集 | 投稿/動画台本/ブログ等を **`/ops` UI 上で追加・編集・複製**。保存は裏で `config/prompts.json`（UI 編集前提なので YAML 手書き運用はしない） | **F3=画面から編集**を反映（当初の YAML 手書き案は撤回） |
| ③ 活動ログ | `per_business_recent` + `cma_apps`。これまでやったこと | — |
| ④ 原文ビューア | consul-work の MD を**折りたたみ**で必要時だけ展開（常時全 HTML 展開はやめる＝ややこしさ解消、でも読める＝ F2 折衷） | **F2=原文閲覧は残す**を反映 |
| ～予定～ | **今回スコープ外**（F4） | **F4=後回し**を反映 |

### プロンプト集の保存方式（F3 反映 → さらに技術制約で再々訂正）

- 当初 §D は「`config/prompts.yaml` を手で編集」だったが、**CEO は画面編集を希望**（F3）。
- 一旦「`config/prompts.json` に画面から書き込み」と設計したが、**Vercel Functions の FS は読み取り専用**（親 CLAUDE.md の cron 判定フロー Q3 にも明記）。本番で `config/prompts.json` への書き込みは**物理的に不可能**だった。
- **最終解（実装採用）**: プロンプトは **Supabase テーブル `ops_prompts`** に永続化。
  - AIハブは既に `@supabase/supabase-js` + `SUPABASE_SERVICE_ROLE_KEY` を**画像アップロードで実運用中**（[api/_lib/storage.ts](../../ai-hub/api/_lib/storage.ts)）。基盤は既存・追加コストなし
  - `/api/ops/prompts`（GET/POST/PUT/DELETE）が Supabase を読み書き。認証は既存 `withAdmin` 流用
  - テーブル: `ops_prompts(id uuid pk, category text, title text, body text, created_at, updated_at)`。RLS は service_role 専用（公開しない）
  - 「投稿」「動画台本」「ブログ」等は `category` 列で画面から自由に増やせる（コードも YAML も不要＝F3 完全充足）
- ⚠️ Supabase に `ops_prompts` テーブルを作る SQL（マイグレーション）が前提。実装に同梱し、CEO 承認時に Supabase で実行する手順を提示する。

---

## F. CEO 確認ポイント → ✅ 全 4 点回答済み（2026-05-17）

| # | 確認事項 | CEO 回答 |
|---|---|---|
| F1 | ゴミ削除の範囲 | **`_tmp` と `_migrate*` のみ**。archive は残す |
| F2 | MD 全 HTML 化の扱い | **廃止。ただし原文閲覧は `/ops` 内に残す**（折りたたみ方式） |
| F3 | プロンプト集の持ち方 | **画面（`/ops` UI）から追加・編集・複製**（YAML 手書き不採用） |
| F4 | Calendar 連携 | **後回し**（今回は タスク/プロンプト/活動ログ の3本） |

→ 仕分け・方針は全確定。残るは **§E の各ステップの実行承認**（事業リポ書き込みのため step ごとに CEO GO が要る）。

---

**最終更新**: 2026-05-17（v2・CEO 4 回答反映。方針確定。§E 実行は step ごと CEO GO 待ち）
