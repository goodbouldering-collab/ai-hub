# 2026-10-28 Codex CLI 0.165.0更新

公式MarkdownとOpenAI GitHub安定版を検証済み取得関数で取得。CLIは0.164.0から0.165.0へ更新。作業履歴の絞り込み・会話中の推論設定変更を追記し、Terraを維持。初回公開日とOGPは保持。編集JSONは事業ルートoutputs/daily-20261028/codex-editorial.json、--editorial-fileで検証した。

ニュースの公開内容は10/13版4件とブログ内入口を保持。48時間の5候補は同outputsへ保存し、掲載方針の回答待ちを継続。

基準は登録元.codex-update-release-20261027/public。781manifestと本番主要5ハッシュ一致、更新前再生成差分0。候補はindex.html、ai-news/index.html、blog/index.html、sitemap.xmlの4資産だけ変更し、777資産を保持。47テストとassets検証成功。

登録元の既存staged/未コミット変更を保護し、分離worktreeで対象のみcommitする。統合SHAから再生成・Worker本文照合・中央ForDeployガード後に公開。実際のSHA・公開結果・PC/iPhone確認・未完了理由は同outputs/README.mdと正本tmp/delivery/20261028-codex-cli-165.jsonに記録する。
