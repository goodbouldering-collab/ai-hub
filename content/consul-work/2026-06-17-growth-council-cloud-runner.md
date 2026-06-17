# Growth Council Cloud Runner 設計・MVP実装メモ

作成日: 2026-06-17
対象ルート: `C:\VSCode\Project`
状態: MVP実装。提案・可視化専用。事業フォルダ、本番、外部サービスは触らない。

## 1. 目的

全事業を毎日見張る司令塔を作る。ただし、1体の巨大エージェントに全判断を背負わせない。

CEOが毎朝見る場所は1つに固定する。

- 入口: `consul/00_司令塔ダッシュボード.html`
- 既存の朝入口: `consul/00_毎朝見る.md`
- 日次統合出力: `consul/work/YYYY-MM-DD-all-daily-growth-council.md`
- 事業別小レポート: `consul/work/YYYY-MM-DD/business-agent-reports/<business_id>.md`

## 2. 階層設計

```text
CEO
  -> 司令塔ダッシュボード
    -> growth-council-cloud-runner
      -> growth-orchestrator
        -> 事業担当プロファイル
          -> 専門エージェント視点
            -> 事業別小レポート
        -> 統合レポート
```

### 司令塔

`growth-orchestrator` が最終統合を担当する。毎日最大7件に絞り、CEO承認待ちへ並べる。

### 事業担当プロファイル

事業ごとの担当は、実体サブエージェントを大量に増やさず、`consul/rag-factory/business-metadata.yaml` を正本にしたプロファイルとして扱う。

この方式なら、既存の `.claude/agents/*.md` と `.codex/agents/*.toml` を壊さずに、各事業へ1担当を付けたように運用できる。

### 専門エージェント視点

必要なときだけ以下の視点を使う。

- market-scouter
- local-hikone-scout
- climber-student-voice
- parent-household-voice
- beauty-wellness-voice
- national-ads-architect
- pivot-challenger
- backoffice-agent-builder
- marketer / writer / designer / developer / cfo / pm

常時何百体を走らせるのではなく、必要な担当・視点だけを呼ぶ。

## 3. RAG方針

RAGは事業別に絞る。

1. 共通ルールRAG: 親 `AGENTS.md`、`consul/AGENTS.md`、承認ルール、cron方針。
2. 事業別RAG: `consul/<business>.md`、各事業の `AGENTS.md` / `CLAUDE.md` / `README.md`。
3. 履歴RAG: `consul/work/*.md` の直近ログ。
4. automation RAG: Codex automation定義・memory。ただし外部パスは必要時のみ。

初期実装は `consul/rag-factory/` の台帳を使う。ベクトルDBはまだ使わない。`rg` / ファイル台帳 / 日付順確認を優先する。

## 4. 日次実行時刻

推奨スケジュール:

- 毎日 09:10 JST
- RRULE: `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU;BYHOUR=9;BYMINUTE=10;BYSECOND=0`

理由:

- 08:00 AIハブ改善ループとぶつからない。
- 17:00 ブログSEO/SNS提案とぶつからない。
- CEOが10時にダッシュボードを開けば確認できる。

## 5. 出力契約

### 事業別小レポート

保存先:

```text
consul/work/YYYY-MM-DD/business-agent-reports/<business_id>.md
```

必須項目:

```markdown
# <事業名> 事業担当小レポート: YYYY-MM-DD

## 今日の状態

## 確認した根拠
| 種別 | ファイル/URL | 確認日 | メモ |
|---|---|---|---|

## 提案候補
| ID | 提案 | 根拠 | 期待値 | コスト | ブロッカー | CEO判断 |
|---|---|---|---|---|---|---|

## 未確認・古い可能性がある情報

## 次に実測すべきこと
```

### 統合レポート

保存先:

```text
consul/work/YYYY-MM-DD-all-daily-growth-council.md
```

必須項目:

- 今日の結論
- 最大7件の提案
- CEO承認待ち
- 事業別根拠リンク
- 実行禁止事項
- 保留にした提案

### ダッシュボード

保存先:

```text
consul/00_司令塔ダッシュボード.html
```

生成コマンド:

```powershell
python consul/tools/build_growth_dashboard.py
```

表示内容:

- 完了 / 実行中 / 失敗 / 未実行の状態点
- 最終生成時刻
- 日次成長会議
- 事業別小レポート
- ブログSEO提案
- SNS提案
- RAG台帳
- automation台帳
- 事業担当プロファイル一覧

## 6. 安全ルール

- 提案のみ。実行しない。
- `C:\VSCode\Project\<事業名>\` へ書き込まない。
- SNS投稿しない。
- Gmail送信しない。
- 広告出稿しない。
- 課金しない。
- デプロイしない。
- DB変更しない。
- 推測と確認済みを分ける。
- 根拠ファイル・確認日・未確認事項を必ず書く。
- CEOが番号で承認したものだけ、次の担当へ渡す。

## 7. automation prompt

```text
全事業横断のGrowth Council Cloud Runnerを実行する。

C:\VSCode\Project\consul\00_毎朝見る.md,
C:\VSCode\Project\consul\AGENTS.md,
C:\VSCode\Project\consul\.claude\agents\growth-orchestrator.md,
C:\VSCode\Project\consul\rag-factory\business-metadata.yaml,
C:\VSCode\Project\consul\rag-factory\sources.yaml,
C:\VSCode\Project\consul\work\ 直近7日分を確認する。

各事業について、business-metadata.yaml の business_id ごとに事業担当プロファイルとして扱い、
その事業の知識正本、直近work、公開URLがあれば確認する。
確認できない外部情報や、ネットワーク/API/認証が必要な情報は未確認として扱う。

各事業の小レポートを consul/work/YYYY-MM-DD/business-agent-reports/<business_id>.md に保存する。
小レポートには「今日の状態」「確認した根拠」「提案候補」「未確認・古い可能性がある情報」「次に実測すべきこと」を含める。

最後に全事業の小レポートを統合し、
consul/work/YYYY-MM-DD-all-daily-growth-council.md に最大7件のCEO承認待ち提案として保存する。

提案にはID、事業名、提案、根拠、期待値、必要コスト、ブロッカー、承認後の担当、触る場所、リスクを含める。

絶対に実行しないこと:
- 事業フォルダへの書き込み
- SNS投稿
- Gmail送信
- 外部連絡
- 広告出稿
- 課金
- デプロイ
- DB変更

保存後、python consul/tools/build_growth_dashboard.py を実行して
consul/00_司令塔ダッシュボード.html を更新する。

続けて、AI Hub管理トップに司令塔ダッシュボードを表示し続けるため、
C:\VSCode\Project\ai-hub\site\static\admin\index.html の先頭導線を確認する。
必要な同期先は `site/static/admin/index.html` と `content/consul-work/` 配下の司令塔正本だけに限定する。
ai-hub が dirty または origin/main より古い場合は、origin/main から一時worktreeを作って同期する。
静的確認として admin HTML に「司令塔ダッシュボード」と「毎日 09:10 JST / ACTIVE」があることを確認する。
/admin がBasic認証で401になる場合は保護状態として扱い、認証情報は出力しない。

最後に、このautomationのmemory.mdへ実行日、出力ファイル、提案件数、ブロッカーを簡潔に追記する。
```

## 8. 表示・確認方法

CEOは以下だけを見る。

```text
C:\VSCode\Project\consul\00_司令塔ダッシュボード.html
```

ブラウザのブックマークまたはデスクトップショートカットにする。
クラウド実行の場合でも、このHTMLを生成物の正本にするか、後段でAIハブ管理画面へ同期する。

## 9. クラウド化メモ

現時点でローカルに見えているCodex automation定義は `execution_environment = "local"` で動いている。

そのためMVPはローカル/クラウド差し替え可能な同一プロンプト・同一出力契約として作る。
Codex CloudまたはGitHub Actionsから実行する場合も、同じprompt、同じ出力ファイル、同じダッシュボード生成コマンドを使う。

クラウドからCEOのPCのChromeを直接開くことはできない。
表示はHTMLブックマーク、Windowsタスクスケジューラ、またはAIハブ管理画面への同期で行う。
