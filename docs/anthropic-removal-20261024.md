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

APIを使う場合も既存接続だけを使用する。キー作成・保存・権限・課金・SNS投稿をこの変更では行わない。ローカルで既存OpenAIキーは検出しておらず、実生成は未検証。

## 検証と公開

PythonのResponses形式・失敗時保全・記事契約、4層のCloudflare Workerで実際のログインを使う合成認証とOpenAI呼出先・未完了応答拒否、既存管理・暗号化キー保存・Cloudflareテスト、TypeScriptと公開経路検査を実施する。公式仕様: https://developers.openai.com/api/docs/guides/text

公開元は台帳登録済みの `work/genspark-profile-edit/cloudflare-runtime`。最新公開資産 `.wordpress-ai-cms-release-20261023-final/public` をハッシュ照合して保持し、統合SHAのWorkerだけを反映する。新しいCodex記事候補0.164や未公開日次ニュースを混ぜない。

工程証拠: `tmp/delivery/20261024-remove-anthropic.json`、事業ルート `tmp/anthropic-removal-20261024/`。PR・配備ID・本番確認は工程記録で確定する。現時点ではローカル検証段階。
