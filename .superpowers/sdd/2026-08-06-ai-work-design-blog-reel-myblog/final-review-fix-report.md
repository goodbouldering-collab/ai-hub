# 最終レビュー修正レポート

実施日: 2026-08-07

対象タイトル: **AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」**

状態: ローカル修正・再生成・検証・実装コミット完了。`review_ready_waiting_final_approval` / `未投稿`。

## 変更と理由

1. 未追跡だった記事WebP 5点を、既存Reel `source/` とSHA-256が一致する承認済み実体としてGitへ収録した。画像の作り直しは行っていない。
2. `tests/test_blog_authorship_note.py` を拡張し、全ブログソースの `/img/` 参照が実在・Git追跡済みであること、対象WebPの形式・1672×941寸法・期待SHA-256、実記事レンダリングの `title → note → video → hero → body` 順を検証した。既存のescaping、blog限定性、本文SHA、hero metadata保全テストは維持した。
3. `build_reel.py` を単一生成元として、原BGM、入力gain後 `music-bed.wav`、生成済みナレーションでsidechainした `ducked-background-music.wav` を作り、FFmpeg `volumedetect` で同じナレーション実音区間を実測するQAを追加した。権利根拠は `self-generated/no external samples`。
4. `qa.json` と `posting-manifest.json` に、ナレーション -18.80 dBFS、原BGM -30.00 dBFS、gain後bed -43.10 dBFS、duck後BGM -49.30 dBFS、BGM入力gain -13.10 dB、実測ducking 6.20 dB、声優位 30.50 dB、閾値と全合否を同値で保存した。
5. campaign 5資料と旧統合設計を、最終タイトル、約28.8秒、6場面、`review_ready_waiting_final_approval`、`未投稿` に統一した。旧5場面/15秒およびhero→video固定は `superseded` と明示し、現行仕様を参照させた。
6. ローカルカスタムスキル `C:\Users\yui\.codex\skills\myblog\SKILL.md` と `agents\openai.yaml` を同期更新した。全事業共通は「title→note後にプロジェクト承認済み媒体順」、今回のAI相談記事は `title → note → video → hero → body`。事業分離、未確認のfirst-hand表現禁止、明示依頼時だけのReel、女性音声、中央テキスト全文読み上げ、自作/保有original BGM権利、低音量・ducking、最終公開承認ゲートは維持した。
7. 記事本文、H2、slug、既存の本文画像URLは変更していない。本文SHAテストは `1d5651056547a7beb4b5c1c2625be3abe33af4663f71d6678b08eb829fd9e2f6` のまま通過した。

## TDD Red確認

```powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_blog_authorship_note -v
```

結果: 5 WebPが未追跡のため `test_every_blog_img_reference_exists_and_is_git_tracked` が意図どおりFAIL。

```powershell
& '.\.venv\Scripts\python.exe' media\output\myreel\2026-08-06-ai-work-design-future\test_build_reel.py -v
```

結果: 旧 `qa.json` に `audio_measurements` がないため意図どおりERROR。その後、最小実装・再生成でGreenへ移行した。

## 最終コマンドと結果

```powershell
& '.\.venv\Scripts\python.exe' media\output\myreel\2026-08-06-ai-work-design-future\build_reel.py
```

結果: exit 0。1080×1920、30fps、H.264/AAC、28.8秒、6場面、通常速度 `+0%`、全QA check true。Reelとサイト動画を再生成。

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' media\output\myreel\2026-08-06-ai-work-design-future\test_build_reel.py -v
```

結果: 58 tests OK、Reel 8 tests OK。

```powershell
& '.\.venv\Scripts\python.exe' site\build_site.py
```

結果: exit 0。14 blog posts、7 lectures、2 slides、sitemap/robotsを生成。`dist root is locked; reusing folder after clearing contents` 警告は出たが、対象記事を含む生成は完了した。

```powershell
& 'C:\Users\yui\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'C:\Users\yui\.codex\skills\myblog'
```

実際はプロジェクトPythonを明示して実行:

```powershell
& '.\.venv\Scripts\python.exe' -X utf8 'C:\Users\yui\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'C:\Users\yui\.codex\skills\myblog'
```

結果: `Skill is valid!`。追加の読み取り検査も `myblog_forward_pressure_read_check=PASS`。

```powershell
& $ffmpeg -hide_banner -v error -i 'media\output\myreel\2026-08-06-ai-work-design-future\reel.mp4' -map 0 -f null NUL
& $ffmpeg -hide_banner -v error -i 'site\static\video\blog-ai-work-design-future-20260806.mp4' -map 0 -f null NUL
```

結果: package/siteとも全編decode PASS。

```powershell
Get-FileHash -Algorithm SHA256 <package reel>,<site reel>,<package cover>,<site cover>,<5 WebP>
```

結果:

- package Reel = site Reel: `412395ee1f1efc705c9c72aa81224835460d520719ea15425797011229842bbf`
- package cover = site cover: `95ff0dc6105df5f181cd4c742159a75a9aebd2461f5b29b398149f68417d2fac`
- hero: `9272401fd416b6aa79f639b5c612db44a7d6f71fbdc77f200bab9ead2a31bb0b`
- speed: `5f75e67c3f96f514b5a77eaf23474149f562e8678dfcd62ce7431ddfb885a7d9`
- system: `ad3fbd4f9bea514b7a73ea4c747e1972e71737912208e9a1ddb4c45f0c150ab1`
- experience: `0de5d77048546638eec258b6e5c709ab1025d4c602597b4b53e1d6a872160935`
- three-lanes: `07af19a77327c18e5a558052d48e893e937192ee7b4e4dcf37924aa2a2c3c662`

```powershell
git diff --check
git diff --cached --check
```

結果: PASS。初回cached検査でcampaign資料のMarkdown改行用末尾空白を検出し、空行へ修正後に再検査PASS。

## ローカルブラウザQA

対象: `http://127.0.0.1:4011/blog/2026-08-06-ai-work-design-future.html`

- 1440×1100: 正確なタイトル、`title → note → video → hero → body`、横overflowなし、console error/warningなし。
- 390×844: 同じ表示順、横overflowなし、注釈可読、ハンバーガーは `aria-expanded false → true`、menu `aria-hidden false` / visibleを確認。
- PC/390pxとも画像5点は `complete=true`、`naturalWidth=1672`、`naturalHeight=941`。Pillowで全5点をWebPとしてdecode済み。
- PC/390pxとも動画 `readyState=4`。CDPの実再生で `play()` 成功、約0.56秒進行、`paused=false` を確認後に停止。

## コミットとGit状態

実装コミット:

```text
53b5388 fix: complete work design review assets and audio qa
```

実装コミット直後の `git status --short`:

```text
 M outputs/agents_status.json
```

`outputs/agents_status.json` はビルドによる他自動更新のため、変更・stage・commit対象から除外した。

## 残る懸念・公開境界

- 外部公開、Vercel deploy/push、Instagram Reel、draft、Story、commentは一切実行していない。現行状態は `review_ready_waiting_final_approval` / `未投稿`。
- MyBlogスキル2ファイルはユーザーレベルのGit外資産で、このリポジトリコミットには含まれない。現物更新と `quick_validate.py` は完了済み。
- 静的ビルド時にdist root lockの警告が残ったが、対象記事生成、全テスト、ローカルブラウザ表示、FFmpeg decode、hash一致は通過した。
