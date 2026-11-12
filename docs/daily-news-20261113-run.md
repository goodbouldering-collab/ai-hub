# 2026-11-13 Codex更新

公式安定版rust-v0.167.2（11月12日JST）と週次October 26–30を照合。Vertex AI利用時のツール情報差分送信が標準になった変更を、既存source/fingerprint/update_articleと--editorial-fileで検証して反映。0.167.1は過去要約へ移動、初回公開日・OGPは保持。モデル・料金・速度効果や他環境への提供を推測しない。公開ニュース4件と配置は本人回答待ちにつき維持。

基準は登録元.codex-update-release-20261112/public、source95d353042a76b907773e1c331b1ca3e125d8a7d4。782資産manifest・本番7ハッシュ・更新前再生成差分0を確認。manifestとhome/blogシェルを現行版へ追従。候補の変更はトップ・独立ページ・ブログ一覧・サイトマップ4資産のみ。47試験・assets検証成功。Worker本文は現行Git blobと一致。

公開前に統合SHAから再生成し候補と照合。登録cwdで中央ForDeployガード後のみ配備する。公開後にlive・HTML7ハッシュ・Worker資源、IAB診断6項目を確認。未確認は全体完了としない。結果はoutputs/daily-20261113とautomation memoryへ保存する。
