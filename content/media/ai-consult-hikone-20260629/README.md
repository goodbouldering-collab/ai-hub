# AI相談 彦根 実践AI講座 動画パッケージ

作成日: 2026-06-29

目的: AI相談 彦根のAI講座について、「なぜAI講座を行うのか」「彦根で事業を加速するには何を知るべきか」「講座で何が残るのか」を、トップページ・ブログ・SNSへ再利用できる事業資産としてまとめる。

## 公開アセット

- トップ掲載動画: `/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm`
- 字幕: `/media/ai-consult-hikone-20260629/ai-consult-hikone-captions.vtt`
- ナレーション原稿: `narration.txt` / `/media/ai-consult-hikone-20260629/ai-consult-hikone-narration.txt`
- 動画ポスター: `/media/ai-consult-hikone-20260629/ai-consult-hikone-poster.png`
- シーン画像: `/media/ai-consult-hikone-20260629/ai-consult-hikone-scene-01.png` から `06.png`
- ブログ記事: `/blog/2026-06-29-ai-consult-hikone-practical-ai-course.html`

## 元素材

- 絵コンテ: `storyboard.md`
- ナレーション原稿: `narration.txt`
- ブログ原稿: `content/blog/2026-06-29-ai-consult-hikone-practical-ai-course.md`

## 再生成コマンド

PowerShellで実行:

```powershell
.\scripts\synthesize_ai_consult_narration.ps1
node .\scripts\render_ai_consult_hikone_video.mjs
```

注意: この作業環境ではWindowsローカルTTSが `0x8004503A` で発話できず、外部TTSは明示承認が必要なため、現時点のWebMは字幕・テキスト入りの無音動画。音声WAVはTTS利用が許可された後に生成する。

その後、サイトを再ビルド:

```powershell
& 'C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' site\build_site.py
```

## 発信への転用

- YouTube: WebMを素材にし、必要ならMP4へ変換して公開する。
- SNS: シーン画像をカルーセル投稿に使う。
- note/ブログ: ブログ本文を長文版、各H2画像を見出し画像として使う。
- 講座案内: 価格、対象者、成果物、相談導線の説明として再利用する。
