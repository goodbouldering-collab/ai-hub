# AI時代、経験者が再び強くなる理由｜Instagramリール

作成日: 2026-08-10
投稿先: `@climbingconsul`
Reelレビュー状態: 約24.7秒 / 5場面 / review_ready_waiting_final_approval / 未投稿
状態: 最終承認待ち（未投稿）

本番埋め込み確認: 記事の著者注記直後・ヒーロー画像前に `reel.mp4` と同一のMP4を配置済み。PC（1440px）・スマホ（390px）で動画読み込みと横はみ出しなしを確認済み（2026-08-10）。

## 内容

- `reel.mp4`: 1080×1920、約24.7秒、30fps、H.264、日本語女性ナレーション・オリジナルBGM付き
- `narration.m4a`: 5場面に同期した通常速度のナレーション音声
- `background-music.wav`: 48kHzステレオ、92 BPMの軽量な自動合成BGM
- `music-bed.wav`: 原BGMへ入力ゲインを適用したダッキング前の比較用音源
- `ducked-background-music.wav`: 生成済みナレーションをsidechainにした実際のダッキング後BGM
- `narration.md`: 声の設定、同期位置、読み上げ台本
- `voice/`: 場面ごとの音声原本
- `cover.png`: リール表紙
- `storyboard.png`: 5場面一覧
- `preview.gif`: 軽量プレビュー
- `story-preview.png`: ストーリー画像とリンクスタンプ配置見本
- `captions.md`: 画面文、キャプション、ストーリー、ブランドコメント
- `story.md`: リール公開後に使うストーリー一式
- `tone.md`: ブランド調査とデザイン根拠
- `posting-manifest.json`: 公開順序と承認状態
- `qa.json`: 動画仕様と実測音声dB、入力ゲイン、ダッキング量、声/BGM差、権利根拠、閾値合否の機械検証
- `posting-manifest.json` の `site_media`: 元記事へ埋め込む同一MP4・カバー画像の本番URL
- `source/`: 記事と共通の生成画像
- `frames/`: 動画の5場面

## 再生成

```powershell
.\.venv\Scripts\python.exe media\output\myreel\2026-08-10-ai-experience-3d-reality\build_reel.py
```

生成後も自動投稿はしない。ブログの本番URLを確認し、完成一式の最終承認を得てからInstagramへ直接投稿する。リール公開後、ストーリーとブランドコメントは2回目の承認後に投稿する。Threadsは使用しない。

音声QAはFFmpeg `volumedetect` で、生成済みナレーションと3段階のBGM（原音／gain後bed／duck後）を同じナレーション実音区間で測る。`music_input_gain_db` は原音からbedへの実測差、`measured_ducking_db` はbedからduck後への実測差、`narration_over_ducked_bgm_db` は声がduck後BGMを何dB上回るかを表す。今回の実測は narration -18.70 dBFS / music gain -13.10 dB / ducked BGM -49.20 dBFS / measured ducking 6.10 dB / voice lead 30.50 dB、権利根拠は `self-generated/no external samples`。全閾値は `qa.json` の `audio_measurements.thresholds` と `checks` を正とする。
