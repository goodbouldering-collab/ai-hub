# Claude Code マルチエージェント運用の「正しい」指示法

**作成日**: 2026-05-16（土）
**目的**: 動画で紹介されていた「マルチエージェント（チーム）運用」を、Claude Code の実際の仕組み・本 consul 環境の実構造に合わせて**正しく動く形**に修正して体系化する
**保存規則**: consul の `work/` フラット保存・日付プレフィックス命名に準拠

> このファイルは「動画の一般論」を鵜呑みにせず、**実際に動くもの**へ直した版。元解説の誤り箇所を表で示し、その上で consul の `.claude/agents/` 10 体体制を実例に正しい設計を解説する。

---

## 0. 結論（先に要点）

動画の解説は方向性は合っているが、**4 つの前提が Claude Code の実装と食い違う**ため、そのままでは動かない or 非効率になる。

| # | 動画の記述 | なぜ動かない / 非効率か | 正しい形 |
|---|---|---|---|
| 1 | 各エージェント専用ディレクトリに `CLAUDE.md` を置いて性格を決める | サブエージェントは `CLAUDE.md` では定義されない。`CLAUDE.md` は**ワークスペース/プロジェクト全体の共有指示**であり、エージェント単位の人格分割の仕組みではない | `.claude/agents/<name>.md` に **frontmatter（`name`/`description`/`tools`/`model`）+ 本文プロンプト**で定義する |
| 2 | ターミナルを複数開き、人間が各セッションに役割を叩き込む | VS Code 拡張運用（CEO はターミナルを開かない方針）と矛盾。また人間が全セッションを手動同期するのは破綻しやすい | **1 セッションをオーケストレーターにし、`Agent` ツールでサブエージェントを並列起動**する |
| 3 | `git worktree add ../project-coder feature/x` を人間が手で叩く | consul は事業フォルダが**独立 git リポ**。親から `../` に切ると別リポを汚染。手動 worktree は後片付けも人間負担 | `Agent` ツールの **`isolation: "worktree"`** を使う。変更なしなら自動クリーンアップ |
| 4 | 「エージェント1のリストに基づき」と人間が結果を中継 | サブエージェントの最終メッセージは**親に tool result として自動で返る**。人間中継は不要 | 親が agent1 の戻り値を agent2 の `prompt` に組み込んで**連鎖**する |

---

## 1. 役割定義は `CLAUDE.md` ではなく `.claude/agents/<name>.md`

### 動画の誤り

> 各エージェントの性格を決める「憲法」のような CLAUDE.md を各エージェント専用ディレクトリに配置します。

これは **2 つの異なる概念を混同**している。

| 概念 | 実体 | 役割 |
|---|---|---|
| `CLAUDE.md` | プロジェクト/ワークスペース直下の Markdown | **全エージェント・全セッション共通**の制約（コーディング規約・ディレクトリ規則）。人格を分けるものではない |
| サブエージェント定義 | `.claude/agents/<name>.md`（frontmatter 付き） | **個別エージェントの人格・権限・モデル**。ここで初めて「コーダー」「テスター」が分かれる |

### 正しい書式（consul の実物 [developer.md](../.claude/agents/developer.md) に準拠）

```markdown
---
name: coder
description: Use proactively when 設計書に基づくコード実装・テスト追加が必要なとき。設計には踏み込まず実装に徹する。
tools: Read, Write, Edit, Bash, Grep
model: sonnet
color: cyan
---

# coder（実装担当）

設計担当が出した設計書に基づき、クリーンなコードを実装する。**設計判断はしない**。

## 必ず守る順序
1. 指定された設計書（`work/YYYY-MM-DD-<略称>-design.md` 等）を Read
2. 対象事業フォルダ直下の `CLAUDE.md` を Read（コーディング規約・データ層を把握）
3. 既存コードを Grep / Read で十分に調査
4. 実装と同時にテストコードも作成
5. 変更内容を `work/YYYY-MM-DD-<略称>-dev-<内容>.md` に作業ログとして残す

## 振る舞いの原則
- 既存ファイルの編集を優先（新規作成は最終手段）
- コメントは原則書かない（命名で表現）
- 後方互換ハック・過剰な抽象化を禁止
- 設計の妥当性に疑問があれば実装を止め、オーケストレーター（親）に差し戻す
```

ポイント:

- **`description` が委任トリガー**。secretary 等の親はこの description を見て「この依頼はこのエージェント」と判断する。曖昧だと振り分けが外れる
- **`tools` で権限を絞る**。コーダーに `Bash` は要るがアーキテクトに `Write`/`Edit` は不要 → 設計担当が誤って実装しない安全弁になる
- **`model` を役割で変える**。深い分析は `opus`（consul では advisor のみ opus）、定型実装は `sonnet`。動画はここに触れていないが、コスト・品質の要

### consul の実体制（既に正しくこの方式）

consul は `.claude/agents/` に **10 体**を frontmatter 方式で常駐させており、動画の「CLAUDE.md 分割」案は既に不要。secretary が司令塔、各専門エージェントが実務。**事業横断で使い回す**設計（「ぐっぼる専用 writer」のような事業別エージェントは作らない）。

| エージェント | model | tools（抜粋） | 役割 |
|---|---|---|---|
| secretary | sonnet | Read, Grep, Glob, TodoWrite | 受付・振り分け（**自分では実装も執筆もしない**） |
| developer | sonnet | Read, Write, Edit, Bash, Grep | 実装（事業リポ書き込みは CEO 確認必須） |
| advisor | opus | — | 深い分析・コンサル（唯一 opus） |
| writer | sonnet | — | 事業ごとのトーンで文章生成 |

動画の「コーダー / アーキテクト / テスター」は、consul では **developer を軸に、設計フェーズは advisor または pm、検証フェーズは developer 内のテスト工程**で吸収できる。新たに3体作るより既存体制を使うほうが consul の「事業横断で使い回す」原則に沿う。

---

## 2. オーケストレーターは「人間が複数ターミナル」ではなく「親セッション + `Agent` ツール」

### 動画の誤り

> ターミナルを複数開き、各セッションの最初に役割を叩き込みます。

VS Code 拡張運用（[consul/CLAUDE.md](../CLAUDE.md) の「VS Code 拡張だけで完結させる運用」/ CEO はターミナルを開かない方針）と真っ向から衝突する。また、人間が N 個のセッションを手で同期するのは N が増えるほど破綻する。

### 正しい形：1 セッションから `Agent` ツールで委任

Claude Code は **`Agent` ツール**で 1 つの親セッションからサブエージェントを起動できる。複数を**独立作業なら 1 メッセージ内で並列起動**する（依存があるものは順次）。

```
# 親（オーケストレーター = secretary 役）の動き

1. Agent(subagent_type="advisor",  prompt="〇〇機能の設計案を work/2026-05-16-x-design.md に出力。実装はするな")
2. ↑の戻り値（設計書パス）を受け取る
3. Agent(subagent_type="developer", prompt="work/2026-05-16-x-design.md を読み実装。CEO 確認前に書き込むな")
4. ↑の戻り値を受け取り、テスト工程へ
```

- サブエージェントの**最終メッセージは tool result として親に返る**（人間中継不要 = 動画の誤り #4 の解消）
- 独立タスクは**同一メッセージで複数 `Agent` 呼び出し** → 真の並列
- consul では secretary がこの親役。[secretary.md](../.claude/agents/secretary.md) の「委任プロトコル」がまさにこのオーケストレーション

### 設計担当と実装担当の分離（動画の本質は正しい）

動画の核心「**考える担当と手を動かす担当を分ける**」自体は正しく、Claude Code でも有効。ただし分け方は:

| フェーズ | consul での担当 | 委任プロンプトの肝 |
|---|---|---|
| 分析 | advisor / pm | 「課題をリストアップ。修正はするな」 |
| 設計 | advisor | 「データ構造と API 設計を `work/...-design.md` に。実装に踏み込むな」 |
| 実装 | developer | 「その設計書を Read してから実装。設計を疑うなら止めて差し戻せ」 |
| 検証 | developer（テスト工程） | 「実装したものに対しテストを書き `npm test` / `next build` 通過まで」 |

各委任プロンプトに **(a) 入力（読むべきファイルパス） (b) 出力先（`work/` の保存パス） (c) スコープ境界（やってはいけないこと）** を必ず書く。consul の secretary が「委任プロンプトの組み立て」で必須としている 3 点と同じ。

---

## 3. コンフリクト回避は手動 `git worktree` ではなく `Agent(isolation: "worktree")`

### 動画の誤り

> git worktree add ../project-coder feature/new-logic を人間が叩く。

consul では各事業フォルダ（`C:\VSCode\Project\<事業名>\`）が**それぞれ独立した git リポジトリ**。親ディレクトリから `../project-coder` に worktree を切ると、

- どのリポの worktree なのか曖昧（親 consul リポ？ 事業リポ？）
- 後片付け（`git worktree remove`）も人間負担
- 事業リポへの書き込みは CEO 確認必須という consul の鉄則を**バイパスしてしまう危険**

### 正しい形：`Agent` ツールの `isolation: "worktree"`

`Agent` ツールは `isolation: "worktree"` を渡すと、**そのエージェント専用の一時 git worktree を自動生成**し、変更がなければ自動クリーンアップする。人間が `git worktree add/remove` を叩く必要はない。

```
Agent(
  subagent_type="developer",
  isolation="worktree",
  prompt="feature/new-logic 相当の作業を隔離 worktree で実施。完了後、差分の要約を返せ。マージは親が判断する"
)
```

- 並列に複数 developer を別 worktree で走らせても物理的に衝突しない（動画の意図はこれで正しく満たせる）
- ただし **consul の鉄則は不変**：事業リポへの実書き込み（worktree 内であっても、最終的に事業リポにマージする操作）は **CEO の事前確認が必須**。worktree 隔離は「衝突回避」の手段であって「CEO 確認を飛ばす口実」ではない
- マージ判断は**人間（CEO）または親セッション**が行う。サブエージェントに `git push` / `git merge` を自走させない（破壊的操作は CEO 明示指示が前提）

---

## 4. 修正版・実践運用フロー（consul 準拠）

動画の「3 ステップ運用フロー」を consul の実体制で正しく動く形に置き換えたもの。

```
CEO「〇〇事業に △△ 機能を追加して」
        │
        ▼
【secretary（親 = オーケストレーター）】
  1. 対象事業を特定 → consul/<事業名>.md を Read（トーン・KPI・進行中タスク把握）
  2. TodoWrite で全体フローを可視化
  3. 以下を順に Agent ツールで委任
        │
        ├─▶【advisor】"コードを読み課題をリストアップ。修正はするな。
        │              結果を work/2026-05-16-<略称>-issues.md に保存"
        │        └─ 戻り値（課題リスト）を親が受領
        │
        ├─▶【advisor】"上記課題に基づき修正プラン+設計を
        │              work/2026-05-16-<略称>-design.md に。実装はするな"
        │        └─ 戻り値（設計書パス）を親が受領
        │
        ├─ 親が CEO に「<事業名>/<対象ファイル> を <こう変更> します。よろしいですか？」確認
        │   （consul 鉄則：事業リポ書き込みは CEO 事前確認必須）
        │
        └─▶【developer (isolation: worktree)】"承認済み設計書 work/...-design.md を
                       Read し実装。テストも同時作成。差分要約を返せ。
                       git push/merge はするな"
                 └─ 戻り値（差分要約）を親が受領 → CEO に報告
```

動画の「エージェント1→2→3を人間が中継」は、**親セッションが戻り値を次の prompt に差し込むことで自動化**される。人間（CEO）が介在するのは **CEO 確認ゲート 1 箇所だけ**で済む。

---

## 4.5. 最新レイヤ：Skill（`context: fork`）と多モデル連携

ここまで（§1〜§4）は「動画の誤りを直した正しい実装」だが、Claude Code には**さらに新しいレイヤ**がある。`Agent` ツールと `.claude/agents/` だけで止まると、これも取りこぼす。出典は公式ドキュメント（[code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) / [/sub-agents](https://code.claude.com/docs/en/sub-agents) / [/agent-sdk/skills](https://code.claude.com/docs/en/agent-sdk/skills)、2026-05 時点）。

### Skill とは（Subagent との決定的な違い）

| 項目 | **Skill** (`.claude/skills/<name>/SKILL.md`) | **Subagent** (`.claude/agents/<name>.md`) |
|---|---|---|
| 呼び出し | ユーザー手動 `/skill-name` ＋ description マッチで自動発動 | 親が `Agent` ツールで明示委任 |
| 実行 context | デフォルトは**メイン会話に統合**（毎ターン存続） | 常に**独立 context**（結果だけ親に返る） |
| 向く用途 | 再利用する手順・規約・ガイダンス | 単発の探索・重い分析・並列ジョブ |
| 定義の階層ロード | ① name/description は常時 ② SKILL.md 本体は呼び出し時 ③ 付随ファイルは参照時 → **数百定義してもメモリ効率的** | フルプロンプトが委任時にロード |

### 動画にも私の初版にも無かった核心：`context: fork`

Skill の frontmatter に **`context: fork`** を指定すると、その Skill は**サブエージェントとしてフォーク実行**され、メイン会話の context を圧迫しない。`agent:` でどのサブエージェントタイプ（`Explore` / `Plan` / `general-purpose` / `.claude/agents/` の任意のカスタム名）で走らせるかも指定できる。

```yaml
---
name: deep-research
description: トピックを徹底調査する。コードベース横断スキャンが必要なとき自動発動。
context: fork          # ← これでサブエージェント化（メイン context を汚さない）
agent: Explore         # ← 読み取り専用ツールに最適化されたエージェントで走らせる
allowed-tools: Read, Grep, Glob
---

$ARGUMENTS を徹底調査せよ:
1. Glob / Grep で関連ファイルを特定
2. Read で解析
3. 要点だけ要約して返す（生ファイルは返さない）
```

**これが意味すること**：動画の「分析担当・設計担当・実装担当を分ける」は、`.claude/agents/` を増やさなくても **Skill + `context: fork` で役割をパッケージ化**して実現できる。consul の「事業別エージェントを増やさない」原則とも両立する（エージェント体制は10体のまま、再利用手順を Skill 側に切り出す）。

### Subagent 側に Skill をプリロードする最新パターン

逆向きもある。サブエージェント定義の frontmatter に `skills:` を列挙すると、そのエージェント起動時に Skill が前段ロードされる。

```yaml
# .claude/agents/custom-researcher.md
---
name: custom-researcher
description: 専門調査エージェント
skills:
  - analyze-code
  - deep-research
---
```

→ 「Skill = 再利用する知識/手順」「Subagent = 独立実行の器」を**組み合わせる**のが最新の正解。動画の二分法（人格を分ける）より一段抽象度が高い。

### 多モデル連携も広義のマルチエージェント（consul は既に方針化済み）

「マルチエージェント = Claude 同士の分業」だけではない。**Claude が詰まったら別 AI（Codex）に丸投げ**するのも実運用上のマルチエージェント。consul は[既に Codex 自律委任を ON](../CLAUDE.md) にしており、`/codex:review`（セカンドオピニオン）、`/codex:rescue`（ゼロから別 AI に考えさせる）、`Agent` の `codex:codex-rescue` サブエージェント（重い調査でメイン context を圧迫しそうなとき）を使い分ける運用が確立している。動画はこのレイヤに一切触れていないが、**実務で効くのはむしろここ**。

### SDK でも使える（CLI 専用ではない）

Skill は Claude Agent SDK（Python / TypeScript）からも利用可能。`setting_sources=["user","project"]` を渡すと filesystem から Skill を discovery する。ただし **`allowed-tools` frontmatter は SDK では効かない**（CLI のみ）。SDK では main query の `allowedTools` で制御する。consul は CLI 拡張運用なのでこの差は実害なしだが、将来 SDK で自動化を組むなら要注意。

### 3 段階で見た位置づけ

| 段階 | 方式 | 状態 |
|---|---|---|
| 古（動画） | 専用 `CLAUDE.md` ＋ 複数ターミナル ＋ 手動 worktree | ❌ 動かない/非効率 |
| 中（本書 §1〜4） | `.claude/agents/` ＋ `Agent` ツール ＋ `isolation:"worktree"` | ✅ 正しく動く |
| 最新（本章） | ＋ Skill `context: fork` ＋ Skill/Subagent 組み合わせ ＋ 多モデル委任 | ✅ context 効率・再利用性が最大 |

---

## 5. 動画解説 vs 正しい実装 早見表

| 観点 | 動画の解説 | Claude Code / consul の正しい実装 |
|---|---|---|
| エージェント定義 | エージE専用 `CLAUDE.md` | `.claude/agents/<name>.md`（frontmatter + 本文） |
| 人格・権限の分離 | プロンプトで都度叩き込む | frontmatter の `description`/`tools`/`model` で恒久定義 |
| オーケストレーション | 人間が複数ターミナル | 1 親セッション + `Agent` ツール（並列/順次） |
| 結果の受け渡し | 人間が手で中継 | 親が tool result を次の prompt に連鎖 |
| 衝突回避 | 手動 `git worktree add ../x` | `Agent(isolation: "worktree")` 自動生成・自動掃除 |
| 安全弁 | （言及なし） | `tools`/`allowed-tools` 制限・CEO 確認ゲート・破壊操作禁止 |
| モデル選択 | （言及なし） | 役割別に opus/sonnet（深い分析のみ opus）。Skill 側 `model:` でも上書き可 |
| 再利用手順のパッケージ化 | （言及なし） | Skill `.claude/skills/<name>/SKILL.md`（3層ロードで省メモリ） |
| context 効率 | （言及なし） | Skill `context: fork` でメイン会話を汚さず役割分割 |
| 多モデル連携 | （言及なし） | Claude が詰まったら Codex へ委任（consul は方針化済み） |

---

## 6. consul に取り込むべきか（提案）

- **新規エージェント（coder/architect/tester）を 3 体追加するのは非推奨**。consul は「事業横断で使い回す・事業別エージェントを増やさない」原則。動画の役割分割は **既存の secretary → advisor → developer の連鎖**で実現済み
- ただし §4.5 を踏まえると、**取り込む価値があるのは「Skill 化」**。例：分析フェーズを `.claude/skills/issue-scan/SKILL.md`（`context: fork` / `agent: Explore`）に切り出せば、エージェント体制を10体のまま維持しつつ「考える担当」を再利用可能にできる。これは consul の原則と両立する数少ない採用候補
- 一方 secretary 等の**既存エージェント定義・共有基盤の書き換えは CEO 明示指示が必要**（[consul/CLAUDE.md](../CLAUDE.md) の鉄則）。本書はあくまで提案であり、体制変更は未実施
- ブログ化（技術知見の対外発信）用に HTML 版を併設：[2026-05-16-claude-multiagent-correct-method.html](2026-05-16-claude-multiagent-correct-method.html)

---

**最終更新**: 2026-05-16（v2・§4.5「最新レイヤ：Skill `context: fork` / Skill×Subagent 組み合わせ / 多モデル連携」を公式ドキュメント裏取りの上で追記。初版は動画の誤り4点修正版）
