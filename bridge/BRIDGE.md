# AI指示を実行するCodex bridge

実行司令室の「AI指示」と、このPCだけで動く公式 `codex app-server` をつなぐ機能です。App Server自体は公開インターネットへ置きません。

## 起動

Windowsでは `start-bridge.cmd` を開くか、次を実行します。

```powershell
npm.cmd run bridge
```

表示された6桁コードを実行司令室へ入力します。短命の接続情報はブラウザのメモリだけに置かれ、画面を閉じると消えます。

## 安全境界

- loopback `127.0.0.1:43117` だけで待ち受ける
- 本番の実行司令室とlocalhostだけをOrigin許可する
- 接続コード、短命capability、CSRF、容量制限、rate limitを検証する
- `projects.json` の事業フォルダだけを実行対象にする
- ブラウザから任意のcwd、Skill path、CLI引数、method、commandを渡さない
- 公開、送信、課金、権限追加、重要な変更はApp Serverのrequest IDごとに確認する
- 実行結果とthread IDは所有者別のD1履歴へ保存し、同じ成果物を再開・全体調整できる

## 検証

```powershell
node --test app-server/bridge.test.mjs
npm.cmd run bridge:smoke
```

現在の実装はCodex CLI / App Server Schema `0.145.0-alpha.18` を正本とし、実行時はCLIの `model/list` から利用可能なSolモデルを優先します。
