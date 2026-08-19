# AI相談の保護管理ページ用 Codex bridge

AI相談の保護された管理ページ `/admin/command-center/studio` と、このPCだけで動く公式 `codex app-server` をつなぐ機能です。App Server自体は公開インターネットへ置きません。

公開ページ `/seo-llmo-diagnosis/` の技術診断はApp Serverなしで完結します。管理者が同じページから「Codexで深掘りする」を選んだ場合だけ、公開診断レポートを固定 `seo-llmo-diagnosis` Skillへ渡します。自由プロンプト、任意のcwd、Skill path、コマンドはブラウザから渡せません。実行はread-onlyで、サイト修正や公開は行いません。

## 起動

Windowsでは、AI相談リポジトリのルートで次を実行します。

```powershell
npm.cmd run bridge
```

表示された6桁コードを `/admin/command-center/studio` に入力します。短命の接続情報はブラウザのメモリだけに置かれ、画面を閉じると消えます。

ローカルの事業フォルダを登録する場合は `bridge/projects.local.example.json` を `bridge/projects.local.json` にコピーして編集します。後者はGit管理外です。共有シークレットは環境変数 `COMMAND_ROOM_BRIDGE_AUTH_SECRET` またはGit管理外の `bridge/.local/bridge-auth.json` にだけ置きます。

## 安全境界

- loopback `127.0.0.1:43117` だけで待ち受ける
- 本番のAI相談とlocalhostだけをOrigin許可する
- 接続コード、短命capability、CSRF、容量制限、rate limitを検証する
- `projects.json` の事業フォルダだけを実行対象にする
- ブラウザから任意のcwd、Skill path、CLI引数、method、commandを渡さない
- 公開、送信、課金、権限追加、重要な変更はApp Serverのrequest IDごとに確認する
- 実行結果とthread IDはAI相談側の保護された履歴へ保存し、同じ成果物を再開・全体調整できる

## 検証

```powershell
npm.cmd run bridge:test
```

現在の実装はCodex CLI / App Server Schema `0.145.0-alpha.18` を正本とし、実行時はCLIの `model/list` から利用可能なSolモデルを優先します。
