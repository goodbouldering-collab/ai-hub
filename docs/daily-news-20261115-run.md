# 2026-11-15 Codex更新

公式安定版rust-v0.169.0（11月13日08:37 UTC）と週次October 26–30を照合。過去作業の検索・履歴折りたたみ・相談タブ再開を既存source/fingerprint/update_articleと--editorial-fileで反映。CLIと任意有効化の対象を明記し、モデル・料金・提供条件を推測しない。0.167.2を過去要約へ、初回公開日・OGP保持。ニュース掲載方針は未確定のため公開4件と配置を保持。

直前正常版は登録元.codex-update-release-20261113/public、source e4090c70aa322991e8553874c2c10a07283e161c。782資産manifest・本番7SHA・更新前再生成差分0を照合。manifestと必要なシェルを最新化。候補4資産変更・778保持、47テスト・assets成功。最初のテストはsparse checkoutにworkflow参照がなく2件失敗したが、同じGit版の参照ファイルを追加して全件成功。既存workflowは再開しない。

既存Wrangler通常更新で401解消、Worker本文一致、Vercel projects/Git連携なし、旧定期workflow停止を確認。統合SHAから再生成し、中央ForDeployガード後に同一Workerで配備する。公開後のlive/ハッシュとIAB実画面・診断6項目を区別し、未確認を完了扱いにしない。最上位Astraの公式変更イベントなし、my-update未起動。結果はoutputs/daily-20261115とautomation memoryへ保存。
