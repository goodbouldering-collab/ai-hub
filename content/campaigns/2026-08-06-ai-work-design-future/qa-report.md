# 検証記録

最終タイトル: **AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」**

Reel: 約28.8秒 / 6場面

レビュー状態: `review_ready_waiting_final_approval`

公開状態: `未投稿`

## 記事

- [x] 静的サイトビルド（ブログ14件、対象記事生成）
- [x] PC幅 1440×1100
- [x] iPhone幅 390×844 / DPR 3
- [x] 固定メニュー／ハンバーガー（開閉、`aria-expanded`、白背景・濃色文字）
- [x] 横スクロールなし（PC／iPhoneとも `overflow: 0`）
- [x] PC／390pxで画像5点の `complete`・`naturalWidth`（全点 1672×941）、PillowでWebP decode・形式・寸法を確認
- [x] 動画の再生情報とポスター（`readyState: 4`）
- [x] CTA、目次、参考資料リンクをDOMで確認
- [x] コンソールエラー／警告なし、エラーオーバーレイなし
- [x] ホームルートも表示、本文あり、横スクロールなし

## リール

- [x] 1080×1920
- [x] 28.80秒
- [x] 30fps
- [x] H.264 / yuv420p
- [x] 日本語女性ナレーションあり（Nanami Neural）
- [x] 6場面を0.0／5.4／9.4／14.0／18.2／23.2秒へ同期
- [x] AAC / 48kHz
- [x] 通常速度 `+0%`、中央テキストとナレーションの正規化一致
- [x] BGM権利根拠 `self-generated/no external samples`
- [x] FFmpeg実測: ナレーション -18.80 dBFS、原BGM -30.00 dBFS、gain後bed -43.10 dBFS、duck後BGM -49.30 dBFS
- [x] BGM入力gain -13.10 dB、実測ducking 6.20 dB、ナレーション優位 30.50 dB
- [x] `qa.json` / `posting-manifest.json` の全音声閾値判定が合格
- [x] 6画面、各3行以内
- [x] 上下UIセーフエリアをストーリーボードと実寸フレームで確認

## 回帰確認

- [x] Python `unittest discover -s tests -v`: 58件成功
- [x] Reel `test_build_reel.py -v`: 8件成功
- [x] TypeScript `tsc --noEmit`: 成功
- [x] `git diff --check`: 成功
- [x] 2026-08-07 顧客目線の追記を本文・編集方針・ファクトチェックへ反映
- [x] 追記後のPC幅 1440×1000／iPhone幅 390×844で横はみ出し0
- [x] 追記後も画像5点は `naturalWidth: 1672`、動画は `readyState: 4`
- [x] 追記後のブラウザコンソールにエラー・警告なし

## 本番

- [ ] Vercelデプロイ成功
- [ ] 本番記事URL HTTP 200
- [ ] 本番PC／iPhone表示
- [ ] Instagram投稿先 `@climbingconsul`
- [ ] リール公開URL
- [ ] 2回目承認後のストーリー／ブランドコメント
