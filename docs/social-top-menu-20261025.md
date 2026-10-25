# SNS集客メニュー（2026-10-25）

確認済み4媒体を、固定ヘッダー直下・本文先頭へ配置。ブランドアイコン＋媒体名を横並びにし、白と既存の緑系で主コンテンツを邪魔しない入口にする。44pxの押下領域、キーボードフォーカス、新しいタブの読み上げを用意。390px幅で4件が同一行に収まることをIABで確認。

URLの正本はconfig/official-social.json。プロフィール確認が終わった媒体を順次ここへ追加し、core/official_social.pyのアイコン対応も追加する。未完了Facebook・YouTube・TikTokは掲載しない。

SVGはSimple Icons 15.20.0（CC0）から取得しローカル保持。https://github.com/simple-icons/simple-icons/tree/15.20.0 。実行時の外部依存はない。

公開候補はPR215のハッシュ済み781資産を基に生成しindex.htmlだけ変更。管理WorkerはPR217を保持。Python構文検査、資産差分、IAB PC/390pxの表示・リンクを確認。

プレビュー: http://127.0.0.1:4187/ 。親PID52580、期限2026-10-29 13:51:04 +09:00。
