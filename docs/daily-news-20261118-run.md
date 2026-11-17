# 2026-11-18 AIニュース・Codex日次実行

ニュース候補は48時間内の5話題をoutputs/daily-20261118へ保存。公開ニュースの件数・配置の回答待ちは継続し、現行4件を維持する。

Codex公式whats-newのNovember 17, 2026が従来の週次日付範囲パーサから漏れていたため、単日付と範囲の双方に対応。最新のCodex記載ブロックを選び、指紋比較・履歴重複防止・巻戻り拒否を維持する。編集JSONを保存し--editorial-fileで更新した。CLI安定版はrust-v0.169.0のまま、記事はGPT-6.2 Astra/Solの公式発表へ更新。

直前正常版は登録元.current-release/public、source d14f8ae7d1286532a080fec6ddac1ee8587e29ad（PR253）。782資産と本番5資産SHAを照合して.daily-baseline-20261118/publicへ固定。更新前再生成は782資産差分0。公開候補はindex.html、ai-news/index.html、blog/index.html、sitemap.xmlの4資産のみ変更。他778資産・ニュース本文・認証API Workerは維持。

標準prepare_current_release.mjsはcontract.aiNews=true時に既存Python builderを一時領域で実行し、全manifest・本番先行版一致・既存出力保護を適用。既定portfolio経路も維持する。

公開・統合・本番HTTPとブラウザの実績はoutputs/daily-20261118へ保存する。IAB未接続の場合はPC/iPhone幅と追加の両診断操作確認を未完了で引継ぎ、HTTP検証と混同しない。
公開時のAIニュース生成は登録元HEADをSHA固定し、必要入力をgit archiveから安全な一時領域へ展開して実行する。未コミット・未追跡入力を読まない。候補のworkingTreeモードは明示指定とcheckLive=falseが必須で、公開経路では利用しない。生成完了前にHEAD不変と全資産manifestを再確認する。
