# 親リポ claude-workspace 未コミット混在 — CEO 引き継ぎ資料

**作成日**: 2026-05-17（日）
**経緯**: みんなのWA Render削除に伴い親 `C:\VSCode\Project\CLAUDE.md` の計画表を訂正 → push しようとして `non-fast-forward` rejected → 作業ツリーに第三者の大量未コミット変更を発見 → [consul 鉄則5](../CLAUDE.md)に基づき Claude は親リポに手を出さず、本資料で CEO に引き継ぐ
**Claude が行った親リポ操作**: [CLAUDE.md](CLAUDE.md) の3行訂正を commit（`cec5da1`）のみ。**add/stash/reset/pull/push は一切していない**（push は rejected で未実行）

---

## 1. 親リポの現状

| 項目 | 値 |
|---|---|
| ローカル HEAD | `cec5da1 docs: 集約マイグレーション計画を実態に修正`（Claude の訂正コミット） |
| origin/main | `92919e6 docs(claude-md): 各クライアントのデプロイ方針を Vercel 集約に更新`（2026-05-11・6日前） |
| 未push コミット | 4件（下記） |
| 未コミット変更 | 15ファイル（Claude 関与なし・第三者作業） |

### 未push の4コミット（ローカルにあるが GitHub に無い）

```
cec5da1 docs: 集約マイグレーション計画を実態に修正            ← Claude(2026-05-17・今回)
6f35b8d agents_system: 残課題3点を解消（Next.js 16固定/例外耐性/timeout延長）  ← 第三者
ab176a8 agents_system: Vercel 集約版に正常化、cma が再稼働      ← 第三者
67fe491 docs(claude): consolidate LINE/Vercel direction notes + add Cron policy ← 第三者
```

→ Claude の `cec5da1` 以外の3コミットは Claude が作っていない。別セッション/別作業の未push分。

## 2. 未コミットの15ファイル（Claude 関与なし・要 CEO 判断）

### 削除(D) — 852行規模・不可逆性高

| ファイル | 最終存在コミット |
|---|---|
| `MIGRATION.md`（186行） | `67c6920 2026-04-26 初期化` |
| `MIGRATION_BACKUP.ps1`（104行） | `67c6920 2026-04-26` |
| `MIGRATION_BOOTSTRAP.ps1`（167行） | `67c6920 2026-04-26` |
| [_audits/README.md](_audits/README.md) ほか [_audits/](_audits/) 配下4本（監査記録） | `a593c70 2026-05-03` |

### 変更(M) — 共有基盤含む（consul 鉄則5の対象）

[set-ports.js](set-ports.js)（最終 `8bc655c 2026-05-04`）, `clients.code-workspace`（同）, `.mcp.json`, [Notエステ/CLAUDE.md](Notエステ/CLAUDE.md), [カラッと/CLAUDE.md](カラッと/CLAUDE.md), [グッぼる/CLAUDE.md](グッぼる/CLAUDE.md), [ファディー/CLAUDE.md](ファディー/CLAUDE.md), [agents_system/README.md](agents_system/README.md)

### 未追跡(??)

[consul/](consul/), [_archive/](_archive/), [Notエステ/](Notエステ/), [プロギング/](プロギング/), `.obsidian/`

## 3. なぜ Claude が処理しないか

1. これらの変更/削除を**誰がなぜ行ったか不明**。別作業の途中の可能性。Claude が commit/stash で巻き込むとその作業を破壊する
2. `MIGRATION.md` 等の削除は不可逆性が高く、中身未確認で rebase の道連れにできない
3. [set-ports.js](set-ports.js) / `clients.code-workspace` は[consul 鉄則5](../CLAUDE.md)「共有基盤への変更は CEO 明示指示が必要」に直接該当

## 4. CEO への推奨アクション（順序）

1. まず `git -C C:\VSCode\Project status` を自分の目で確認し、15ファイルの変更が**意図したものか/作業途中か**を判断
2. 意図した変更なら: 適切な単位で commit → `git pull --rebase origin main`（リモート6日前分を取り込み）→ `git push`
3. 不要な変更なら: 該当ファイルを `git checkout --` で破棄してから 2 を実施
4. **Claude の `cec5da1`（CLAUDE.md計画表訂正・ai-hub URL=ai-hub-jp / みんなのWA Render削除済）は残す価値あり**。捨てるなら consul 側の [minanowa.md](../minanowa.md) と [work/2026-05-17-minanowa-render-deletion.md](2026-05-17-minanowa-render-deletion.md) に同じ情報が push 済みなので情報自体は失われない

## 5. 実害評価

**小さい。** 親 [CLAUDE.md](CLAUDE.md) の計画表訂正（ai-hub URL誤記・みんなのWA Render削除）が GitHub に反映されていないだけ。同じ判断・記録は **consul リポに push 済み**（minanowa.md / work/）。親 CLAUDE.md がやや古いままなのは、次に親リポを整理する誰かが本資料を見れば追従できる。

## 6. 教訓（commit→push 必須ルールの安全ゲート穴）

2026-05-17 制定の「commit したら push まで必須」安全ゲートは「ビルド通過/秘密情報スキャン」しか見ていなかった。**「作業ツリーに第三者の未完了変更が混在していないか」「リモートと分岐していないか」を push 前ゲートに追加すべき**。今回それが露呈。次回ルール見直し時に [[consul-must-push-not-just-commit]] へ反映する。
