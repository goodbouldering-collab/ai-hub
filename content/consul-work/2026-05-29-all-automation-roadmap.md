# consul 自動化ロードマップ（全8案・見積もり）

最終更新: 2026-05-29（実装ステータス追記）
対象: consul 本部リポジトリ（C:\VSCode\Project\consul\）
方針: 既知事故の再発防止 > 新規便利機能。投資判断は「**実装コスト時間 vs 防ぐ事故の発生確率 × 影響**」で評価。

## 実装ステータス（2026-05-29 時点）

| # | 案 | ステータス | 備考 |
|---|---|---|---|
| #1 | Stop hook（git status + 未push表示） | ✅ **既に実装済み** | `~/.claude/settings.json` L106-118 に `[WARN] uncommitted/unpushed commits:` を表示する PowerShell コマンドが既設置。ロードマップ起票時の「未実装」認識がズレていた。本日確認 |
| #2 | gitleaks pre-commit | ✅ **新規実装** | gitleaks 8.30.1 を winget でインストール／`consul/.git/hooks/pre-commit` に設置／ダミーAWS+GitHubトークンで検知→exit 1 拒否を検証済／`GITLEAKS_SKIP=1` エスケープも検証済 |
| #3〜#8 | 残り6本 | ⬜ 未着手 | CEO 判断待ち（投資対効果サマリ参照） |

### #2 実装メモ（後継への引き継ぎ）

- gitleaks **v8.20+ で `protect/detect` サブコマンド廃止**。新コマンドは `gitleaks git --staged`。古い記事/AI の指示にそのまま従うと "no leaks found" で誤検知ゼロになる罠あり
- AWS の公式例示キー `AKIAIOSFODNN7EXAMPLE` は gitleaks の組み込み allowlist にあるためテストでは検知されない。テストする場合はランダム化した値を使う
- winget で入れた gitleaks の本体は `%LOCALAPPDATA%/Microsoft/WinGet/Packages/gitleaks.gitleaks_*/gitleaks.exe`。winget の Links ディレクトリは Windows によっては PATH に未登録のため、pre-commit スクリプトは絶対パスをフォールバックで持つ設計
- 緊急時のバイパス: `GITLEAKS_SKIP=1 git commit ...` または `git commit --no-verify`（後者は他フックも全てバイパスするので推奨は前者）

## 現状の自動化資産（2026-05-29 時点）

| カテゴリ | 件数 | 内訳 |
|---|---|---|
| consul 配下の GHA workflow | **1本** | [.github/workflows/seo-weekly.yml](.github/workflows/seo-weekly.yml)（毎週月 08:00 JST・実稼働中） |
| consul 配下の Claude hooks | **0本** | [.claude/hooks/](.claude/hooks/) ディレクトリ自体が未作成 |
| consul 配下の pre-commit / Git hooks | **0本** | `.git/hooks/` は default のまま |
| work/ ファイル累積 | **133本** | フラット保存・最古は 2026-05-11、直近4日（25〜28）だけで14本追加 |
| 全事業横断 cron | **6本**（全 GitHub Actions） | 詳細は [work/2026-05-26-all-cron-inventory.md](work/2026-05-26-all-cron-inventory.md) |
| memory 件数 | **16本** | `MEMORY.md` index 経由で全件読込み中 |

つまり consul は「司令塔メタリポ」として軽く保たれているが、**安全網（push 漏れ検知・secret 検知・cron 死活）が手薄**。これが本ロードマップの主戦場。

---

## #1. stop hook で `git status` + 未push commit を表示

### 何を防ぐか

memory「[consulはcommitだけでなくpush必須](C:/Users/yui/.claude/projects/c--VSCode-Project-consul/memory/consul-must-push-not-just-commit.md)」記載の**約3週間 push 漏れ事故の再発**。ai-hub の sync-consul-docs cron が無音で古いまま動いていた実証済みの事故。CLAUDE.md の安全ゲートは「人間（私）が忘れる」のが弱点。

### 実装内容

`~/.claude/settings.json` の `hooks.Stop` に PowerShell ワンライナーを追加。応答終了時に毎回 `git status --short` と未 push commit を表示する。

```json
"hooks": {
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        { "type": "command", "command": "powershell -NoProfile -Command \"if (Test-Path .git) { $s = git status --porcelain; if ($s) { Write-Output '⚠️ 未commit/未push の変更:'; git status --short }; $u = git log '@{u}..HEAD' --oneline 2>$null; if ($u) { Write-Output ''; Write-Output '⚠️ 未push commit:'; Write-Output $u } }\"" }
      ]
    }
  ]
}
```

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **5 分**（CEO が hooks セクションをコピペ追加） |
| 維持コスト | ゼロ（受動的表示のみ） |
| Claude 使用枠への影響 | ゼロ（ローカル実行・LLM 経由しない） |
| 副作用 | 応答末尾に毎回 4〜6 行追加表示。`.git` がないディレクトリでは何も出ない |

### 推奨度

**★★★（最優先）**。コスト 5 分 vs 実証済み事故の再発防止。投資対効果が文字通り桁違い。

---

## #2. pre-commit で `gitleaks` による secret scan

### 何を防ぐか

memory「[push前にpassword発見・伏字化抹消](C:/Users/yui/.claude/projects/c--VSCode-Project-consul/memory/password-leak-found-before-push.md)」記載の **password 混入未遂事故**。次回は手動レビューで気付かない可能性がある。CLAUDE.md 安全ゲート②（diff に秘密情報なし）を人間チェックではなく機械チェックに昇格。

### 実装内容

- **A方式**: `gitleaks` を Windows にインストール（`scoop install gitleaks` または `winget install gitleaks`）し、`.git/hooks/pre-commit` で `gitleaks detect --staged` を実行
- **B方式**: `pre-commit` フレームワーク（Python）導入し、`.pre-commit-config.yaml` で `gitleaks` リポを参照（10事業フォルダへテンプレ展開が容易）

CEO の運用が主に PowerShell + git CLI なので **A方式推奨**（依存少・1ファイル設置）。

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **30 分**（gitleaks インストール + `.git/hooks/pre-commit` 1ファイル + 動作確認） |
| 維持コスト | gitleaks のバージョンアップを年1〜2回（脆弱性パターン更新） |
| Claude 使用枠への影響 | ゼロ |
| 副作用 | false positive 発生時は `.gitleaksignore` で除外。consul の token_*.json は既に .gitignore 済なので影響軽微 |

### 推奨度

**★★★（最優先）**。次回 password 混入を気付けない可能性が現実的に存在する。30 分の投資で「機械が止める」を獲得。

---

## #3. MEMORY.md 自動コンパクション（古い memory の統合提案）

### 何を防ぐか

`MEMORY.md` の index 肥大化と重複。現在 16 件・各セッション開始時に全件 system-reminder 経由で読み込まれる。半年後に 50 件超えるとコンテキスト圧迫が無視できない。

### 実装内容

- 月1回（または stop hook で月初検知時）、`memory/*.md` の `originSessionId` と作成日を集計
- 「同じトピックで複数の memory が乱立していないか」「90日以上更新なしで一度も `[[name]]` 参照されていない memory はないか」をリスト化
- 統合・削除候補を [work/](work/) に提案 markdown として出力（CEO が判断して手動実行）

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **1 時間**（Python スクリプト + GHA cron 1本） |
| 維持コスト | 月1回 5 分の CEO レビュー |
| Claude 使用枠への影響 | コンテキスト圧迫の予防的削減 |
| 副作用 | 提案だけ・自動削除はしない（memory 紛失防止） |

### 推奨度

**★★（中優先）**。memory 16 件は現状ギリギリ管理可能。3〜6ヶ月後の予防策。今すぐ着手はオーバー。

---

## #4. work/ の月次自動アーカイブ

### 何を防ぐか

[work/](work/) フラット保存で **133本**累積。直近4日（5/25〜28）だけで 14 本追加＝月 100 本ペース。CLAUDE.md ルール「フラット保存（サブフォルダ作らない）」は維持しつつ、90日以上経過のものを `work/archive/YYYY-MM/` へ機械的に退避することで現役 work/ の見通しを保つ。

### 実装内容

- GHA scheduled（月1日 09:00 JST）で `find work/ -maxdepth 1 -name "*.md" -mtime +90` 相当を実行
- 該当ファイルを `work/archive/YYYY-MM/` へ git mv して commit
- アーカイブ対象判定は **mtime** ではなく**ファイル名先頭の日付プレフィックス**から計算（編集で mtime が動くので）

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **1 時間**（GHA workflow + Python 移動スクリプト） |
| 維持コスト | ゼロ（完全自動） |
| Claude 使用枠への影響 | Glob/Grep 結果の対象範囲が縮小→検索高速化 |
| 副作用 | アーカイブ後のファイルは `work/archive/` から `Read` で参照可能。リンク [work/2026-05-11-...](work/2026-05-11-...) が一部切れる可能性→GHA 内で grep 自動置換するか、CEO の手動修正に任せる |

### 注意点

CLAUDE.md「**最大2階層まで**」ルールとの整合性。`work/archive/2026-05/foo.md` は 2 階層なので OK。ただし「サブフォルダ作らない」の原則とは緩い緊張関係になる→CEO 判断要。

### 推奨度

**★★（中優先）**。133本はまだ管理可能だが、年末には 1000 本越える試算。早めにルール化するほど痛みが小さい。

---

## #5. 全事業 cron 死活監視（GHA 横断ダッシュボード化）

### 何を防ぐか

memory「[consulはcommitだけでなくpush必須](C:/Users/yui/.claude/projects/c--VSCode-Project-consul/memory/consul-must-push-not-just-commit.md)」記載の「ai-hub 死活は `gh run list` で見る」現状。**人間が能動的に見ない限り無音**。各事業ジョブには「失敗時 Issue 自動作成」が個別にあるが、**事業横断で1枚にまとまっていない**。

### 実装内容

- GHA scheduled（毎週月 09:00 JST、SEO週次直後）で以下を実行:
  1. `gh run list --repo <各事業リポ> --limit 5 --json status,conclusion,workflowName,createdAt` を全6本のリポに対して取得
  2. 1本でも `conclusion == "failure"` があれば consul に Issue 作成
  3. 全成功でも [work/YYYY-MM-DD-all-cron-health.md](work/) に「直近 run のステータス表」を生成して `REPORTS-HUB.md` に追記
- consul リポ自体には push 権限のある PAT が必要（既に `GOOGLE_OAUTH_CREDENTIALS` 等で secrets 運用ノウハウあり）

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **1.5 時間**（workflow + 6リポ分の `gh run list` 集約スクリプト + secret 設定） |
| 維持コスト | 事業追加時に集約対象リポ名を 1 行追加（年1〜2回） |
| Claude 使用枠への影響 | ゼロ（GHA 内で完結） |
| 副作用 | gh CLI のレート上限は 5000 req/h なので 6リポ × 週1 では問題なし |

### 推奨度

**★★（中優先）**。AIハブ同期失敗を3週間見逃した実績の再発防止としては #1 が即効、これは「横断可視化」で別レイヤの保険。#1 を入れた後に余裕があれば。

---

## #6. scheduler/mailer の週次ヘルスチェック（OAuth トークン失効検知）

### 何を防ぐか

memory「[gsc-ga4-seo-integration-status](C:/Users/yui/.claude/projects/c--VSCode-Project-consul/memory/gsc-ga4-seo-integration-status.md)」記載のとおり、**OAuth テストモードのトークンは7日で失効**。本番公開後の無期限トークンに切り替え済だが、リフレッシュトークン自体の失効（Google 側の判定・90日無使用等）は能動検知しないと「使おうとした瞬間」まで気付かない。

### 実装内容

- GHA scheduled（毎週日 12:00 JST、SEO週次の前日）で `python google_ops/scripts/refresh.py --account goodbouldering --dry-run` 相当を実行
- access_token の refresh が成功すれば OK、失敗したら Issue 作成
- 同時に `token_goodbouldering.json` の `expires_at` フィールドを表示し、健康状態を可視化

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **1 時間**（refresh.py に `--dry-run` フラグ追加 + workflow 作成） |
| 維持コスト | ゼロ |
| Claude 使用枠への影響 | ゼロ |
| 副作用 | 既存 SEO 週次が同じ token を使うので、SEO 週次が失敗した時点で実質検知される＝**冗長**との見方も成立 |

### 推奨度

**★★（中優先）**。SEO 週次自体が「token 健全性チェッカー」を兼ねているので、優先度は #5 より下。**lossismore アカウントを認可するなら必須化**（現状 goodbouldering 1本だけなので冗長気味）。

---

## #7. Codex 委任ログの月次レビュー bot

### 何を防ぐか

memory「[codex-delegation-policy-thresholds-provisional](C:/Users/yui/.claude/projects/c--VSCode-Project-consul/memory/codex-delegation-policy-thresholds-provisional.md)」記載のとおり、CLAUDE.md の Codex 自律委任ポリシー（15分/3回/5ファイル）は**実データゼロでの仮置き**。委任ログを溜めて再評価する設計だが、**自動集計の仕組みがない**ので CEO が手動で work/ を grep する必要がある。

### 実装内容

- 月初の GHA で `grep -rn "codex:" work/*.md | grep -E "発火|invoked"` を集計
- 月別の発火回数・成功率・対象事業を [work/YYYY-MM-codex-delegation-monthly.md](work/) に出力
- 3ヶ月以上データが溜まったら CLAUDE.md ポリシーセクションの閾値再評価提案を Issue で投げる

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **1 時間** |
| 維持コスト | ゼロ |
| Claude 使用枠への影響 | ゼロ |
| 副作用 | 委任ログ書式が CLAUDE.md 規定通り（`YYYY-MM-DD codex:<コマンド> 発火（事業/理由/結果）`）でないと集計漏れ→書式遵守が前提 |

### 推奨度

**★（低優先）**。価値はあるが「ポリシー再評価」は半年に1回程度の頻度であり、その時に手動で grep すれば 10 分で済む。自動化の費用対効果は低い。

---

## #8. メディアキット配備済7事業の差分検知

### 何を防ぐか

memory「[メディアキットは配備までがスコープ](C:/Users/yui/.claude/projects/c--VSCode-Project-consul/memory/media-kit-scope-deploy-not-distribute.md)」記載のとおり、7事業に配備済のメディアキットアセットは**事業側で勝手に書き換わっても気付かない**。事業横断のブランドガイドライン整合性を保つには「配備時の hash を記録し、定期的に diff」する必要がある。

### 実装内容

- 配備済アセット（各事業の `config/constants.ts`、メディアキットフォルダ、ロゴ/カラーパレット）の SHA-256 を初回登録時に [work/media-kit-baseline.json](work/) に保存
- GHA scheduled（毎週月）で全7事業の現在 hash を再計算し、差分があれば [work/YYYY-MM-DD-media-kit-drift.md](work/) に出力
- 「事業側で正当な更新があった」場合は CEO が baseline.json を更新する運用

### コスト見積もり

| 項目 | 見積もり |
|---|---|
| 実装時間 | **2 時間**（baseline 設計 + 7事業横断スクリプト + workflow） |
| 維持コスト | 事業側の正当な更新ごとに baseline.json 更新（月1〜2回） |
| Claude 使用枠への影響 | ゼロ |
| 副作用 | baseline 更新を忘れると false positive が続く→運用負荷あり |

### 推奨度

**★（低優先）**。「気付かないリスク」は理論的には存在するが、**事業フォルダのコード書き込みは CEO 事前確認**ルール（CLAUDE.md ルール1）があるので、CEO が知らないうちに書き換わる経路自体が薄い。優先度は最下位。

---

## 投資対効果サマリ（推奨実装順）

| 順 | # | 案 | 時間 | 防ぐ事故の実証度 | 推奨度 |
|---|---|---|---|---|---|
| 1 | #1 | stop hook で git status | 5 分 | 3週間 push 漏れ実績 | ★★★ |
| 2 | #2 | pre-commit secret scan | 30 分 | password 混入未遂実績 | ★★★ |
| 3 | #5 | 全事業 cron 死活監視 | 1.5 時間 | AIハブ同期失敗3週間放置実績 | ★★ |
| 4 | #4 | work/ 月次アーカイブ | 1 時間 | 月100本ペースで肥大 | ★★ |
| 5 | #3 | MEMORY.md コンパクション | 1 時間 | 現状16件・3〜6ヶ月後問題化 | ★★ |
| 6 | #6 | OAuth token 健全性 | 1 時間 | SEO週次で実質代替済 | ★★ |
| 7 | #7 | Codex 委任ログ月次集計 | 1 時間 | 手動 grep 10分で代替可能 | ★ |
| 8 | #8 | メディアキット差分検知 | 2 時間 | CEO 事前確認ルールで実質防御済 | ★ |

**合計**: 全8案で 8.5 時間。事故再発防止の本命は #1 + #2 の **35 分**で完了する。

---

## 次に何をするか

CEO の判断待ち:
- **A**: #1 だけ即実装（5分）
- **B**: #1 + #2 セット（35分）= 既知事故の機械的予防完了
- **C**: ★★以上を全部（A + B + #5 + #4 + #3 + #6）= 約 6 時間
- **D**: 全8案実装（8.5 時間）
- **E**: 今は何もしない・このロードマップを参照資料として残すだけ

私の推奨は **B**。#1 と #2 は「事故の実証データがある」ので投資判断が明快、合計 35 分で完結。#3 以降は「予防的」要素が強くなるので、本番事業の優先順位次第。
