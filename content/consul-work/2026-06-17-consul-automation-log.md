# consul automation log 2026-06-17

## growth-council-cloud-runner

| 項目 | 内容 |
|---|---|
| 名前 | 全事業司令塔ダッシュボード |
| 目的 | 事業別担当プロファイルで全事業を点検し、小レポートを作り、最大7件のCEO承認待ち提案へ統合する |
| 実行元 | Codex cron automation |
| cwd | `C:\VSCode\Project` |
| schedule | 毎日 09:10 JST |
| rrule | `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU;BYHOUR=9;BYMINUTE=10;BYSECOND=0` |
| 正本ファイル | `consul/work/2026-06-17-growth-council-cloud-runner.md` |
| 入口 | `consul/00_司令塔ダッシュボード.html` |
| 事業担当台帳 | `consul/rag-factory/business-metadata.yaml` |
| 事業別出力 | `consul/work/YYYY-MM-DD/business-agent-reports/<business_id>.md` |
| 統合出力 | `consul/work/YYYY-MM-DD-all-daily-growth-council.md` |
| 最終確認日 | 2026-06-17 |
| 実行制限 | 提案のみ。事業フォルダー書き込み、SNS投稿、メール送信、広告、課金、デプロイ、DB変更、外部連絡はCEO承認後だけ |

補足: 事業担当は実体サブエージェントを大量作成せず、`business-metadata.yaml` の事業プロファイルとして扱う。司令塔は必要な専門エージェント視点だけを使う。
