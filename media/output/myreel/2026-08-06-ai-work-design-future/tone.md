# トーンとデザインの根拠

確認日: 2026-08-06

- 投稿先はAI相談の公式Instagram `@climbingconsul`。Feed／Reels／Storiesを使用し、Threadsは使用しない。
- 公式プロフィールの公開文面は、事業、実践、プラグマティズムを率直に伝える調子だった。
- 公開グリッドは個人・事業の実写が混在し、AI相談として統一された最新ビジュアル体系は確認できなかった。
- そのためデザインは、AI相談公式サイトの最新Clear Sky Roseを基準にした。
- 既存のAI相談向けリール資産の読みやすい型を継承し、デザイナー向けの約25秒／5場面へ更新した。
- 音声は `Microsoft Nanami Neural（日本語・女性）`。親しみやすさと信頼感を保ち、通常速度で画面中央の全文を読む。
- BGMは外部音源やサンプルを使わずPython標準ライブラリだけで合成し、ナレーション中は約6dBダッキングする。
- FFmpeg `volumedetect` で生成済みナレーション、原BGM、入力ゲイン後bed、duck後BGMのナレーション区間RMSを実測する。今回の結果は narration -19.00 dBFS / music gain -13.20 dB / ducked BGM -49.30 dBFS / measured ducking 6.10 dB / voice lead 30.30 dB。
- 権利根拠は `self-generated/no external samples`。閾値判定は `qa.json` と `posting-manifest.json` に同値で保存する。
- 難しいAI用語を避け、「AIでデザイナーはいらなくなる？」という身近な疑問から始めた。
- ロボット、サイバー空間、別事業の配色・写真・ロゴは使っていない。
