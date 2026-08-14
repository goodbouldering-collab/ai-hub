# ai-hub 経営本部ドキュメント同期不調 — 真因確定・解決済み

**作成日**: 2026-05-17（日）
**ステータス**: ✅ **解決完了・実証済み**
**対象**: ai-hub の `/admin/docs`（consul work/ ドキュメント閲覧）が約3週間古かった問題

---

## 結論（先に答え）

**真因は `CONSUL_REPO_PAT` 失効でも Vercel デプロイ問題でもワークフロー停止でもなかった。**

> **真因：consul リポのローカルコミットが GitHub に `git push` されていなかった。**

- consul ローカル HEAD は進んでいたが `origin/main` は 6f73c34（2コミット遅れ）で停止
- GitHub 上 consul/work/ は **32ファイル・最新 2026-05-13** で固まっていた
- `sync-consul-docs.yml` は **毎日正常に success で完走**していた（PAT も生きていた）
- だが clone 元（GitHub consul）が古い32ファイルのため、同期しても毎日「変更なし」で正常終了
- 結果、全系統が「正常」を返しながら、ai-hub には新しい work/ が永遠に届かなかった

## 解決アクション（2026-05-17 実施）

1. `git -C consul push origin main` → `6f73c34..31452e3` push 成功。GitHub上 consul/work/ が **32→45ファイル**に更新
2. `gh workflow run sync-consul-docs.yml --repo goodbouldering-collab/ai-hub` で即時同期トリガー
3. ラン `25988907273` が `completed success`（10秒）。ログに `Sync 完了: 45 ファイル` / `[main 5ff664d] chore(consul-docs): daily sync 2026-05-17`
4. GitHub上 ai-hub/content/consul-work/ が **32→45ファイル**・最新 [2026-05-17-secrets-inventory.md](2026-05-17-secrets-inventory.md) まで反映を実証

Vercel・PAT・ワークフロー定義は**一切変更していない**（変更不要だった）。

---

## 確定事実テーブル（GitHub Actions 実ログで確証）

| 仮説（5/16設計書・Codex・調査途中） | 実ログによる事実 |
|---|---|
| sync-consul-docs.yml は 5/13 で停止 | ❌ 5/12〜5/16 毎日 `success` で完走 |
| daily.yml は 5/13 で停止 | ❌ 5/12〜5/16 毎日 `success` で完走 |
| ワークフローが GitHub に自動 disable | ❌ 両方 `active` |
| `CONSUL_REPO_PAT` 失効 | ❌ PAT 欠落なら exit 1 で fail。全ラン success ＝ PAT 健在 |
| `ai-hub.vercel.app` が別 Next.js プロジェクト（5/16 R1） | △ 取り違えは事実だが本番は `aiclimb.vercel.app`（[ai-hub.md](ai-hub.md) に正本記録済）。今回問題の主因ではない |

## なぜ全員（5/16設計書・Codex・調査途中の Claude）が外したか

**全員が「どの系統が止まっているか」を探したが、実際は全系統正常で、最上流の入力（GitHub上のconsul）が古かった。**

- 5/16設計書・Codex とも診断材料が「**ローカルの** git log / ファイル数」だった
- ローカル ai-hub は `git pull` されず 5/13 で固着 → 「ai-hub が古い＝同期が止まった」と誤読
- 実際は GitHub（リモート）の sync は毎日成功。ローカルが古いのは別問題（ローカルを pull していないだけ）
- **教訓：リモートで動く CI の死活を「ローカルの git 状態」で推定してはいけない。`gh run list` で実ログを見るまで結論を出さない**

## 再発防止

- **consul は commit したら必ず push する**（push しないと ai-hub 同期・cron 連携・他事業参照が全部古いまま無言で進む）
- consul 鉄則「git 操作は CEO 明示指示が必要」がボトルネックになっていた面がある。コミットだけして push 指示待ちで放置されると本問題が再発する。**「コミット＝push までが1セット」を CEO 判断の既定にするか要検討**（次回 CEO 相談事項）
- daily.yml / sync-consul-docs.yml の死活は今後 `gh run list --repo goodbouldering-collab/ai-hub` で確認（ローカル git では判定不能）

---

## Codex 委任ログ（CLAUDE.md 改定ポリシー §委任ログ に基づく記録）

- 2026-05-17 `codex:codex-rescue` 発火（事業: ai-hub / 理由: パイプライン3系統不調の根本原因究明・5ファイル以上横断調査でコンテキスト圧迫回避 / 結果: Codex も gh ブロックで Actions ログ未取得・3系統停止仮説までは到達したが真因（未push）には未達。最終確定は Claude が gh 認証済みを発見し実ログ取得して達成）。1セッション rescue 1回目（報告ゲート上限3回内）
