# Designer Reel Copy and Hero Price Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the AI-and-design Reel with the approved five-screen designer-focused message, force the correct `ひとがになう` TTS reading, and change the homepage hero price to `5,500円から` in production.

**Architecture:** Keep `build_reel.py` as the single source for visual copy, narration, TTS input, generated review assets, and the blog video copy. Add one optional TTS-only field so pronunciation can differ from the human-readable transcript without weakening the text/narration alignment checks. Keep `site/build_portal.py` as the homepage source and regenerate tracked `site/dist` output through `site/build_site.py`.

**Tech Stack:** Python 3.12, Pillow 11.3, edge-tts 7.2.8, FFmpeg, unittest, static HTML generation, Vercel.

## Global Constraints

- Reel output stays 1080×1920, H.264/yuv420p, AAC/48kHz, 30fps, female `ja-JP-NanamiNeural`, normal rate `+0%`, and at most three centered lines per screen.
- Use exactly five screens and the five user-approved copy blocks from the design spec.
- The third screen remains human-readable as `人が担う`; only the TTS input uses `ひとがになう`.
- Homepage hero text changes only from `相談5,500円/回` to `5,500円から`; other prices remain unchanged.
- Instagram remains unpublished until the regenerated package is shown and approved; destination is `@climbingconsul`; do not post to Threads.
- Do not include unrelated working-tree files in any commit.
- Use `C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` with dependencies installed into the worktree-local `.python-deps` directory.
- Use `C:\Project\グッぼる\media\output\myreel\2026-07-03-finger-training-reframe\pydeps\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe` for FFmpeg media inspection.

## File Map

- `media/output/myreel/2026-08-06-ai-work-design-future/build_reel.py`: source of five scenes, narration, TTS override, caption, Story, comment, rendering, and QA metadata.
- `media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py`: Reel contract and generated-asset tests.
- `media/output/myreel/2026-08-06-ai-work-design-future/*`: regenerated frames, audio, video, QA, preview, and posting-review files.
- `site/static/video/blog-ai-work-design-future-20260806.mp4`: blog copy of the regenerated Reel.
- `site/static/img/blog-ai-work-design-reel-cover-20260806.png`: blog copy of the regenerated cover.
- `content/blog/2026-08-06-ai-work-design-future.md`: video label and caption duration text.
- `tests/test_rendered_salon.py`: generated homepage price contract.
- `site/build_portal.py`: homepage hero price source.
- `site/dist/index.html`: tracked generated homepage.

---

### Task 1: Lock the approved Reel contract with failing tests

**Files:**
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py:23-53`
- Test: `media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py`

**Interfaces:**
- Consumes: existing `BEATS`, `TOTAL_SECONDS`, `VOICE_RATE`, `spoken_words()`, and `tts_text()`.
- Produces: required `tts_input(beat: dict[str, object]) -> str` behavior and the exact five-screen contract.

- [ ] **Step 1: Replace the six-screen assertions with the approved five-screen contract**

```python
def test_five_scenes_use_approved_designer_copy_at_normal_speed(self) -> None:
    expected = [
        ["AIでデザイナーは", "いらなくなる？"],
        ["AIなら", "ロゴもサイトも", "すぐ作れる"],
        ["人が担うのは", "お客様の話を聞き", "何を作るか決めること"],
        ["デザインを頼む人は", "サイトや資料も", "まとめて頼みたい"],
        ["AIはデザイナーの", "仕事を広げる", "最強の武器になる"],
    ]
    self.assertEqual([beat["text"] for beat in self.module.BEATS], expected)
    self.assertEqual(len(self.module.BEATS), 5)
    self.assertEqual(self.module.VOICE_RATE, "+0%")
    self.assertTrue(all(len(beat["text"]) <= 3 for beat in self.module.BEATS))
    for beat in self.module.BEATS:
        self.assertEqual(
            self.module.spoken_words("".join(beat["text"])),
            self.module.spoken_words(beat["narration"]),
        )

def test_third_scene_uses_hito_pronunciation_only_for_tts(self) -> None:
    beat = self.module.BEATS[2]
    self.assertEqual(beat["text"][0], "人が担うのは")
    self.assertIn("人が担う", beat["narration"])
    self.assertTrue(self.module.tts_input(beat).startswith("ひとがになうのは"))
    self.assertNotIn("にんがになう", self.module.tts_input(beat))
```

- [ ] **Step 2: Prepare the declared Python dependencies inside the worktree**

```powershell
$python='C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -m pip install --disable-pip-version-check --target '.python-deps' -r requirements.txt -r 'media/output/myreel/2026-08-06-ai-work-design-future/requirements.txt'
$env:PYTHONPATH=(Join-Path (Get-Location) '.python-deps')
```

Expected: Pillow 11.3.0, edge-tts 7.2.8, PyYAML, requests, and the root project dependencies import from `.python-deps`.

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```powershell
$env:PYTHONPATH=(Join-Path (Get-Location) '.python-deps')
& $python -m unittest 'media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py'
```

Expected: FAIL because six scenes still exist and `tts_input` is not defined.

### Task 2: Implement the five scenes and pronunciation-safe TTS input

**Files:**
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/build_reel.py:67-143,176-179,482-497,771-935,939-end`
- Test: `media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py`

**Interfaces:**
- Consumes: each beat dictionary with `text`, `narration`, optional `tts_narration`, `duration_seconds`, `image`, and `accent`.
- Produces: `tts_input(beat: dict[str, object]) -> str`, five-scene metadata, revised posting copy, and dynamic duration labels.

- [ ] **Step 1: Replace `BEATS` with the approved copy and add the TTS-only reading**

```python
BEATS = [
    {"label": "AIとデザイナー", "text": ["AIでデザイナーは", "いらなくなる？"], "narration": "AIでデザイナーは、いらなくなる？", "duration_seconds": 4.0, "image": "blog-ai-work-design-hero-20260806.webp", "accent": COLORS["deep"]},
    {"label": "AIが作れるもの", "text": ["AIなら", "ロゴもサイトも", "すぐ作れる"], "narration": "AIなら、ロゴもサイトも、すぐ作れる", "duration_seconds": 4.4, "image": "blog-ai-work-design-speed-20260806.webp", "accent": COLORS["blue"]},
    {"label": "人の仕事", "text": ["人が担うのは", "お客様の話を聞き", "何を作るか決めること"], "narration": "人が担うのは、お客様の話を聞き、何を作るか決めること", "tts_narration": "ひとがになうのは、お客様の話を聞き、何を作るか決めること", "duration_seconds": 6.0, "image": "blog-ai-work-design-system-20260806.webp", "accent": COLORS["rose"]},
    {"label": "お客様の期待", "text": ["デザインを頼む人は", "サイトや資料も", "まとめて頼みたい"], "narration": "デザインを頼む人は、サイトや資料も、まとめて頼みたい", "duration_seconds": 5.6, "image": "blog-ai-work-design-experience-20260806.webp", "accent": COLORS["lilac"]},
    {"label": "デザイナーの武器", "text": ["AIはデザイナーの", "仕事を広げる", "最強の武器になる"], "narration": "AIはデザイナーの、仕事を広げる、最強の武器になる", "duration_seconds": 5.4, "image": "blog-ai-work-design-three-lanes-20260806.webp", "accent": COLORS["deep"]},
]
```

- [ ] **Step 2: Add `tts_input()` and use it in voice generation**

```python
def tts_input(beat: dict[str, object]) -> str:
    return tts_text(str(beat.get("tts_narration", beat["narration"])))

# in generate_voice_raw()
text = tts_input(beat)
```

- [ ] **Step 3: Make scene-count and duration checks dynamic and rewrite posting copy**

Use `len(BEATS) == 5`, name the QA check `five_scenes`, calculate labels from `TOTAL_SECONDS`, and use these exact publication constants:

```python
CAPTION = f"""AIでデザイナーはいらなくなる？
私は、むしろ仕事が広がると思っています。

AIなら、ロゴもWebサイトも資料も、これまでより早く形にできます。
でも、お客様の話を聞き、何を作るかを決めるのは人です。

デザインを頼める人には、サイトや資料もまとめて相談したい。
そう考えるお客様は、これから増えていくはずです。

だからAIは、デザイナーの仕事を奪う敵ではありません。
仕事を広げる、最強の武器になります。

詳しい考え方は、AI相談のブログにまとめました。
{BLOG_URL}

#AI活用 #デザイン #Web制作 #資料作成 #仕事術 #AI相談"""

STORY_COPY = "AIでデザイナーはいらなくなる？\n答えは逆。AIは仕事を広げる武器になります。"
STORY_LINK_LABEL = "詳細はこちら"
BRAND_COMMENT = "ロゴだけでなく、サイトや資料までまとめて相談できると、お客様の手間も減ります。AIを使ったクリエイティブの相談は、気軽にDMしてください。"
```

Set the storyboard title to `AIとデザインの未来｜約25秒リール（5場面）` and the Story preview lines to `AIでデザイナーは / いらなくなる？ / 答えは逆。`.

- [ ] **Step 4: Run focused tests and verify GREEN for source contracts**

Run the Task 1 command.

Expected: source-contract tests pass; generated-asset checks may still fail until Task 3 regenerates outputs.

### Task 3: Regenerate and verify all Reel and blog video assets

**Files:**
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/frames/*.png`
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/voice/*.mp3`
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/{reel.mp4,cover.png,storyboard.png,preview.gif,story-preview.png,narration.m4a,background-music.wav,music-bed.wav,ducked-background-music.wav,README.md,captions.md,narration.md,pre-post-confirmation.md,posting-manifest.json,qa.json,story.md,review.html}`
- Modify: `site/static/video/blog-ai-work-design-future-20260806.mp4`
- Modify: `site/static/img/blog-ai-work-design-reel-cover-20260806.png`
- Modify: `content/blog/2026-08-06-ai-work-design-future.md:14-15`

**Interfaces:**
- Consumes: approved five-scene `BEATS` and `tts_input()`.
- Produces: synchronized Reel package, blog video, cover, QA JSON, and review assets.

- [ ] **Step 1: Run the generator with declared Python dependencies and FFmpeg access**

```powershell
$env:PYTHONPATH=(Join-Path (Get-Location) '.python-deps')
& $python 'media/output/myreel/2026-08-06-ai-work-design-future/build_reel.py'
```

Expected: five raw voice clips, five frames, final Reel, and all text/QA assets regenerate without speed-up.

- [ ] **Step 2: Update the blog video label to the generated duration**

Set the frontmatter to these exact values while leaving the blog argument unchanged:

```yaml
video_label: AIでデザイナーの仕事がどう広がるかを約25秒・女性ナレーション・軽いBGMで整理する動画
video_caption: ロゴ、サイト、資料へ。AIがデザイナーの仕事を広げる理由を、女性ナレーションと軽いBGMで伝える約25秒リールです。
```

- [ ] **Step 3: Run Reel tests and media inspection**

```powershell
& $python -m unittest 'media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py'
& $ffmpeg -hide_banner -i 'media/output/myreel/2026-08-06-ai-work-design-future/reel.mp4' -f null NUL
```

Expected: 8 tests pass; video reports 25.4 seconds, 1080×1920, H.264/yuv420p, 30fps, AAC/48kHz, five scenes, and all audio QA checks true.

- [ ] **Step 4: Commit the Reel revision**

```powershell
git add -- 'media/output/myreel/2026-08-06-ai-work-design-future' 'site/static/video/blog-ai-work-design-future-20260806.mp4' 'site/static/img/blog-ai-work-design-reel-cover-20260806.png' 'content/blog/2026-08-06-ai-work-design-future.md'
git commit -m 'feat: simplify AI designer reel message'
```

### Task 4: Change the homepage hero price with TDD

**Files:**
- Modify: `tests/test_rendered_salon.py:74-75`
- Modify: `site/build_portal.py:14548`
- Modify: `site/dist/index.html`

**Interfaces:**
- Consumes: `build_portal.render_home()` output used by `tests/test_rendered_salon.py`.
- Produces: hero HTML containing `<strong>5,500円から</strong>` and no `相談5,500円/回`.

- [ ] **Step 1: Change the rendered-home test first**

```python
self.assertIn("<strong>5,500円から</strong>", hero)
self.assertNotIn("相談5,500円/回", hero)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
& $python -m unittest tests.test_rendered_salon
```

Expected: FAIL because the source still renders `相談5,500円/回`.

- [ ] **Step 3: Apply the one-line source change**

```python
"<div class='hero-advantage-copy'><small><strong>5,500円から</strong><span>始めるなら今。</span></small>..."
```

- [ ] **Step 4: Rebuild the site and verify GREEN**

```powershell
& $python site/build_site.py
& $python -m unittest tests.test_rendered_salon
```

Expected: build exits 0 and the focused test passes.

- [ ] **Step 5: Commit the price revision**

```powershell
git add -- tests/test_rendered_salon.py site/build_portal.py site/dist/index.html
git commit -m 'fix: clarify homepage consultation price'
```

### Task 5: Full verification, production deployment, and browser QA

**Files:**
- Verify only; do not add unrelated files.

**Interfaces:**
- Consumes: committed Reel and homepage changes.
- Produces: pushed branch/main deployment evidence and production browser proof.

- [ ] **Step 1: Run the complete verification suite**

```powershell
& $python -m unittest discover -s tests -p 'test_*.py'
& $python -m unittest 'media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py'
npx.cmd tsc --noEmit
git diff --check origin/main...HEAD
```

Expected: 63 or more site tests pass, 8 Reel tests pass, TypeScript exits 0, and diff check is clean.

- [ ] **Step 2: Review generated visuals**

Open `storyboard.png`, `story-preview.png`, and the final Reel. Confirm all five screens are legible, no text clips at 1080×1920, and the third narration audibly says `ひとがになう`.

- [ ] **Step 3: Push and deploy production**

Run:

```powershell
git push -u origin codex/reel-copy-price-20260808
gh pr create --base main --head codex/reel-copy-price-20260808 --title "AIデザイナーReelと料金表記を改善" --body "承認済みの5画面Reelへ再生成し、トップ料金を5,500円からへ変更します。"
gh pr checks --watch
gh pr merge --squash --delete-branch
vercel.cmd ls --yes
```

Expected: pull request checks pass, the pull request is merged to `main`, and the newest production deployment for project `prj_e7vh73eF0KZpm8C49esnILvHO98o` reports READY.

- [ ] **Step 4: Verify production HTTP and rendered UI**

Check:

- `https://aiclimb.vercel.app/` contains visible `5,500円から` and not `相談5,500円/回`.
- `https://aiclimb.vercel.app/blog/2026-08-06-ai-work-design-future.html` loads the revised video.
- PC width and iPhone width show readable navigation, hero price, portrait video, and no horizontal overflow.
- Browser console has no new errors and the video resource returns 200 with the regenerated file hash.

- [ ] **Step 5: Present the regenerated Instagram set for approval**

Show the final Reel, five overlays, caption, Story text, `詳細はこちら` link placement, brand comment, final blog URL, and `@climbingconsul`. Do not publish until the user explicitly approves this regenerated set.
