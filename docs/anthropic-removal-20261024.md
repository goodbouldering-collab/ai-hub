# AI相談のAnthropic依存除去

最終更新: 2026-10-24。対象は既存記事の生成基盤と管理API。公開記事・ニュース・画像は変更しない。

## 原因と修正

`scripts/update_codex_update_log.py` と旧定期workflowがAnthropicの認証を必須としていた。Python要約、旧管理API、Cloudflare内の旧記事生成にも同じ依存が残っていた。

- 生成は既存OpenAI Responses APIへ統一。`OPENAI_API_KEY`、`OPENAI_MODEL`を使用し、SDKの追加はしない。既定モデルは既存管理機能と同じ `gpt-5.6-luna`。記事専用 `CODEX_BLOG_EDITOR_MODEL` と管理専用 `AI_HUB_OPENAI_MODEL` で上書きできる。
- `--editorial-file <JSON>` で既存Codex作業の編集結果を渡せる。APIキー不要でも、公式原文・引用URL・コマンド・記事構造の既存検証を通った内容だけ保存する。差分がなければ生成しない。
- 不完全応答・空テキスト・認証エラーは受け入れない。本文やキーを上流エラーメッセージへ露出させない。生成リクエストは `store: false`。
- Python/npmのAnthropic SDK、キー要求、モデル設定、接続表示、設定雛形を除去。ニュースの出典・既存記事・過去の運用記録にあるAnthropicの言及は履歴として保持する。
- 旧workflowの対象パスを現行の `content/ai-news/codex-update-log.md` に修正。日次実行の再開は行わない。

## 実行経路

記事更新は既存ローカル/heartbeat作業を継続する。GitHub側のCodex更新と旧Pagesは停止・readback済み、dailyも既存の停止状態を維持。Cloudflare guardは稼働状態を維持する。portfolio-syncは実績フックから利用されるため変更しない。

```powershell
python scripts/update_codex_update_log.py --editorial-file <検証対象の編集JSON>
```

APIを使う場合も既存接続だけを使用する。キー作成・保存・権限・課金・SNS投稿をこの変更では行わない。既存の事業共有 `.env.shared` のOpenAIキーを値を出さず検出。Pythonは環境変数、事業内 `.env` / `.env.shared`、同じGit事業の共有設定の順で読み、キーを書き換えない。実課金の生成は未実施。

## 検証と公開

PythonのResponses形式・失敗時保全・記事契約、4層のCloudflare Workerで実際のログインを使う合成認証とOpenAI呼出先・未完了応答拒否、既存管理・暗号化キー保存・Cloudflareテスト、TypeScriptと公開経路検査を実施する。公式仕様: https://developers.openai.com/api/docs/guides/text

公開元は台帳登録済みの `work/genspark-profile-edit/cloudflare-runtime`。最新公開資産 `.wordpress-ai-cms-release-20261023-final/public` をハッシュ照合して保持し、統合SHAのWorkerだけを反映する。新しいCodex記事候補0.164や未公開日次ニュースを混ぜない。

工程証拠: `tmp/delivery/20261024-remove-anthropic.json`、事業ルート `tmp/anthropic-removal-20261024/`。PR・配備ID・本番確認は工程記録で確定する。PR #209統合・本番反映済み。統合SHA `163dc865d4c415962a283f1c72d7cd63e8e05014`、初回Cloudflare version `da8fde2d-ff81-4601-ab24-81a35619bbd9`。公開776資産不変、4公開HTMLの配信SHA一致、7経路確認。IAB既存認証で接続状態とpingのAnthropic項目消失を確認。GitHubの未使用ANTHROPIC_API_KEYは削除・名前一覧を再確認済み。Cloudflareにはそのsecretは元から存在しない。Python39件・Worker14件・Cloudflare7件・TypeScript・CI2件成功。

事業ルートの分岐済みcheckoutにも提供元変更だけをbackportし、既存未コミット変更を保存した。mainとの100件規模の既存競合は修復していない。現用・公開の正本は統合済み登録公開元を継続使用する。次回の公開資産baselineは `.anthropic-removal-release-20261024-final/public`。本番旧記事APIのサーバーOpenAIキーは未設定であり、新制作画面は既存の利用者保存キー経路を保持。秘密設定や実記事生成を本変更の完了と混同しない。
