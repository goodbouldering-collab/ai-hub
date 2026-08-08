# AI時代のワークデザイン：ブログ・Reel・MyBlog標準化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AI相談の記事を、タイトル直下の制作注釈と約29秒の女性ナレーション・BGM付きReelで完成させ、同じ安全な制作ルールを全事業向けMyBlogへ標準化する。

> 実行状態メモ（2026-08-07）: 以下のチェックボックスは実装時の計画構造を保持する履歴であり、完了判定の正ではない。現行状態は `.superpowers/sdd/2026-08-06-ai-work-design-blog-reel-myblog/final-review-fix-report.md`、Reelの `qa.json` / `posting-manifest.json`、およびGitコミットを正とする。

**Architecture:** 記事の制作注釈はMarkdown本文ではなくfrontmatterの`authorship_note`として保持し、AI相談の静的レンダラーがブログヘッダー直後に描画する。Reelは各場面の`text`・`narration`・`duration`を単一の`BEATS`構造に集約し、同じデータから映像、音声、BGM、QA、投稿セットを生成する。全事業向けの恒久ルールはインストール済み`myblog`スキルとそのエージェントメタデータに追加する。

**Tech Stack:** Python 3.12、unittest、Markdown静的サイトビルド、Pillow、edge-tts、FFmpeg、JSON、YAML

## Global Constraints

- 既存の記事本文、H2、事例、FAQ、CTA、参考資料、画像、URLスラッグ、Reel既存5場面の中央テキストは変更しない。
- 記事タイトルは `AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」` に統一する。
- `authorship_note` はブログタイトルとメタ情報の直後、動画・本文より前に表示する。経験を確認できない場合は、確認・編集の実態に合わせた安全な文面を使う。
- ブログ連動Reelは依頼時だけ制作し、中央テキストの語句を女性ナレーションが省略せず読む。画面文を速読させない。
- BGMは再生成できるオリジナル合成音のみ。女性ナレーション中はBGMを約6dB下げ、声が聞き取りにくくならないようにする。
- 本番デプロイ、CMS公開、Instagram投稿、ストーリー、ブランドコメントは、完成版の最終確認まで実行しない。
- `C:\Project\_shared` は大規模な未コミット変更があるため、この作業では共有Blog App Serverプロンプトを編集しない。全事業への標準化はインストール済み`myblog`スキルで行う。

---

## File Structure

- `content/blog/2026-08-06-ai-work-design-future.md` — AI相談の記事frontmatter。最終タイトル、制作注釈、動画説明を保持する。
- `site/build_site.py` — `authorship_note`をブログのヘッダー直後にエスケープして出力する唯一のレンダリング責務を持つ。
- `tests/test_blog_authorship_note.py` — 注釈の表示順、エスケープ、非ブログへの非漏出を検証する。
- `media/output/myreel/2026-08-06-ai-work-design-future/build_reel.py` — 6場面のデータ、可変尺映像、女性ナレーション、オリジナルBGM、ダッキング、QAを生成する。
- `media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py` — 画面文・読み上げ・尺・BGMの契約を検証する。
- `media/output/myreel/2026-08-06-ai-work-design-future/{narration.md,captions.md,README.md,qa.json,posting-manifest.json,pre-post-confirmation.md}` — 再生成後の監査・レビュー・投稿境界を記録する。
- `site/static/video/blog-ai-work-design-future-20260806.mp4` / `site/static/img/blog-ai-work-design-reel-cover-20260806.png` — 記事上部の本番用動画と表紙コピー。
- `C:\Users\yui\.codex\skills\myblog\SKILL.md` — 全事業向け記事注釈と、依頼時だけのブログ連動Reel音声ルールを定義する。
- `C:\Users\yui\.codex\skills\myblog\agents\openai.yaml` — MyBlogの説明と開始プロンプトをスキル本体と同期する。

## Task 1: タイトル直下の制作注釈をレンダリングする

**Files:**
- Create: `tests/test_blog_authorship_note.py`
- Modify: `site/build_site.py:CONTENT_CSS` and `render_content_page`
- Modify: `content/blog/2026-08-06-ai-work-design-future.md`

**Interfaces:**
- Consumes: blog frontmatter field `authorship_note: str`
- Produces: `_render_blog_authorship_note(meta: dict, kind: str) -> str`, which returns escaped HTML only for `kind == "blog"`

- [ ] **Step 1: Write the failing behavior test**

```python
def test_blog_note_is_between_header_and_video(self) -> None:
    note = "AIを思考整理の補助に使い、運営者自身の経験と考えをもとに丁寧にまとめた記事です。"
    page = self.builder.render_content_page(
        "題名", {"authorship_note": note, "video": "/video/example.mp4"},
        "<p>本文</p>", "<nav></nav>", kind="blog",
    )
    self.assertLess(page.index("</header>"), page.index(note))
    self.assertLess(page.index(note), page.index("article-video"))
    self.assertLess(page.index("article-video"), page.index("<p>本文</p>"))
```

Add cases that assert `<` in a note becomes `&lt;`, and that a `kind="lecture"` page does not contain the note.

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_blog_authorship_note -v
```

Expected: FAIL because `_render_blog_authorship_note` is not present and the note is not emitted before the video.

- [ ] **Step 3: Implement the minimal renderer and styling**

Add this helper before `render_content_page`:

```python
def _render_blog_authorship_note(meta: dict, kind: str) -> str:
    if kind != "blog":
        return ""
    note = str(meta.get("authorship_note") or "").strip()
    if not note:
        return ""
    return (
        "<aside class='blog-authorship-note' role='note'>"
        "<span class='blog-authorship-note__label'>この記事について</span>"
        f"<p>{html.escape(note)}</p></aside>"
    )
```

Append its result immediately after `parts.append("</header>")`. Add `.blog-authorship-note` rules to `CONTENT_CSS` with a light primary-background panel, readable contrast, `max-width: 920px`, and a compact mobile layout. Add the selected `authorship_note` plus the final title and約29秒の動画ラベル・キャプション to the article frontmatter.

- [ ] **Step 4: Run focused tests and build**

Run:

```powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_blog_authorship_note -v
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site/build_site.py
```

Expected: PASS; generated `site/dist/blog/2026-08-06-ai-work-design-future.html` contains the note after `</header>` and before `article-video`.

- [ ] **Step 5: Commit the testable site change**

```powershell
git add tests/test_blog_authorship_note.py site/build_site.py content/blog/2026-08-06-ai-work-design-future.md site/dist
git commit -m "feat: add blog authorship note"
```

## Task 2: Reelの全文読み上げ、内容紹介、BGMを再生成する

**Files:**
- Create: `media/output/myreel/2026-08-06-ai-work-design-future/test_build_reel.py`
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/build_reel.py`
- Modify or regenerate: all review assets in `media/output/myreel/2026-08-06-ai-work-design-future/`
- Modify or regenerate: `site/static/video/blog-ai-work-design-future-20260806.mp4`, `site/static/img/blog-ai-work-design-reel-cover-20260806.png`

**Interfaces:**
- Consumes: each `BEATS` item with `label: str`, `text: list[str]`, `narration: str`, `duration_seconds: float`, `image: str`, and `accent: str`
- Produces: `scene_starts() -> list[float]`, `spoken_words(text: str) -> str`, `create_background_music() -> Path`, `reel.mp4`, `narration.m4a`, `background-music.wav`, and `qa.json`

- [ ] **Step 1: Write the failing Reel contract test**

```python
def test_six_scenes_read_all_center_text_without_time_compression(self) -> None:
    self.assertEqual(len(self.module.BEATS), 6)
    self.assertAlmostEqual(sum(beat["duration_seconds"] for beat in self.module.BEATS), 28.8)
    for beat in self.module.BEATS:
        self.assertEqual(
            self.module.spoken_words("".join(beat["text"])),
            self.module.spoken_words(beat["narration"]),
        )
    self.assertEqual(self.module.VOICE_RATE, "+0%")
```

Add a second case asserting `create_background_music` exists and every beat has at most three center-text lines.

- [ ] **Step 2: Run the Reel contract test to verify it fails**

Run:

```powershell
& '.\.venv\Scripts\python.exe' media\output\myreel\2026-08-06-ai-work-design-future\test_build_reel.py -v
```

Expected: FAIL because the current script has 5 scenes, `BEAT_SECONDS = 3`, paraphrased `VOICE_BEATS`, and no BGM generator.

- [ ] **Step 3: Implement the single-source Reel data model and audio mix**

Replace fixed `BEAT_SECONDS`, `TOTAL_SECONDS`, and separate `VOICE_BEATS` with six `BEATS` entries. Use these exact scene durations: `5.4`, `4.0`, `4.6`, `4.2`, `5.0`, and `5.6` seconds. Set `VOICE_RATE = "+0%"`.

Implement `spoken_words` as punctuation-insensitive comparison:

```python
def spoken_words(text: str) -> str:
    return re.sub(r"[\s、。・！？!?]", "", text)
```

Generate `background-music.wav` with only Python standard-library `math`, `struct`, and `wave`: 48kHz stereo, gentle 92 BPM pad/pulse, 0.35-second fade-in, 0.8-second fade-out, no external samples. Use per-scene start times in the FFmpeg concat list and narration delays. Mix it with narration using a sidechain compressor plus a low bed volume so the music ducks by about 6dB while narration is active.

Update `inspect_video` and `write_text_assets` to record six scenes, the exact text/narration mapping, `background-music.wav`, `music_ducking_db: 6`, the approximately29-second duration contract, and the requirement that publication remains blocked.

- [ ] **Step 4: Render and verify the Reel**

Run:

```powershell
& '.\.venv\Scripts\python.exe' media\output\myreel\2026-08-06-ai-work-design-future\test_build_reel.py -v
& '.\.venv\Scripts\python.exe' media\output\myreel\2026-08-06-ai-work-design-future\build_reel.py
```

Expected: contract test PASS; `qa.json` reports 1080×1920, 30fps, H.264, AAC, audio present, 6 scenes, about 28.8 seconds, BGM source present, no narration speed-up, and text/narration alignment.

- [ ] **Step 5: Inspect the generated visual and audio artifacts**

Run:

```powershell
& 'C:\Project\グッぼる\media\output\myreel\2026-07-03-finger-training-reframe\pydeps\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe' -hide_banner -i media\output\myreel\2026-08-06-ai-work-design-future\reel.mp4 -f null NUL
Get-FileHash media\output\myreel\2026-08-06-ai-work-design-future\reel.mp4, site\static\video\blog-ai-work-design-future-20260806.mp4 -Algorithm SHA256
```

Open `storyboard.png`, `cover.png`, and a frame from each scene. Confirm the title-introduction card fits within the center card and all 6 cards retain safe margins.

- [ ] **Step 6: Commit the regenerated media package**

```powershell
git add media/output/myreel/2026-08-06-ai-work-design-future site/static/video/blog-ai-work-design-future-20260806.mp4 site/static/img/blog-ai-work-design-reel-cover-20260806.png
git commit -m "feat: add narrated work-design reel"
```

## Task 3: MyBlogを全事業向けに標準化する

**Files:**
- Modify: `C:\Users\yui\.codex\skills\myblog\SKILL.md`
- Modify: `C:\Users\yui\.codex\skills\myblog\agents\openai.yaml`
- Modify: `docs/superpowers/specs/2026-08-06-ai-work-design-reel-audio-design.md`

**Interfaces:**
- Consumes: verified first-hand operator context, article source/frontmatter, and an explicit request for a blog-linked Reel
- Produces: factual `authorship_note` copy, title-adjacent preview check, and an approval-gated Reel package with `text`, matching female narration, original light BGM, content introduction, QA, caption, and CTA

- [ ] **Step 1: Preserve baseline behavior evidence**

Record that the no-skill baseline did not require literal center-text narration, an introductory scene, a factual-note fallback, or a no-speed-up rule. Keep this evidence in the implementation notes; do not confuse it with the post-change validation.

- [ ] **Step 2: Update the MyBlog workflow minimally**

In `SKILL.md`, update the one-paragraph user-facing description and add requirements to the source-writing, preview, final-review, and final-report stages:

```markdown
- Every new or materially revised article must include a factual `authorship_note` directly below the title and before any video or body content.
- Use the first-hand wording only when experience and editorial ownership are verified; otherwise use the reviewed-and-edited wording.
- When the user explicitly requests a blog-linked Reel, add a short content-introduction scene, have a natural female narration read each center-text message in full, use original low-level BGM with voice ducking, extend duration rather than speeding the narration, and include script-to-screen and audio QA in the review pack.
```

In `agents/openai.yaml`, keep the prompt quoted and include `$myblog`, the title-adjacent factual note, and the conditional Reel-audio contract.

- [ ] **Step 3: Validate the installed skill**

Run:

```powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -X utf8 'C:\Users\yui\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'C:\Users\yui\.codex\skills\myblog'
```

Expected: `Skill is valid!`.

- [ ] **Step 4: Run forward pressure tests with fresh agents**

Ask fresh evaluators to create (a) a business-neutral authorship-note policy and (b) a requested blog-linked Reel plan after reading the updated MyBlog skill. Success requires a factual fallback note, title-adjacent placement before media, a conditional Reel trigger, a content-introduction scene, full center-text reading, low original BGM with ducking, no narration speed-up, review artifacts, and a final publication approval gate.

- [ ] **Step 5: Commit the in-repository design evidence only**

```powershell
git add docs/superpowers/specs/2026-08-06-ai-work-design-reel-audio-design.md docs/superpowers/plans/2026-08-06-ai-work-design-blog-reel-myblog.md
git commit -m "docs: record myblog reel standard"
```

## Task 4: Build、ブラウザ確認、最終レビューを作る

**Files:**
- Modify or regenerate: `site/dist/blog/2026-08-06-ai-work-design-future.html`, `site/dist/blog/index.html`, `site/dist/index.html`, `site/dist/sitemap.xml`
- Verify: `content/campaigns/2026-08-06-ai-work-design-future/`, Reel review assets, final article route

**Interfaces:**
- Consumes: generated static site, Reel artifact, and source/article tests
- Produces: a review-ready article and Reel package, not a public publication

- [ ] **Step 1: Run all relevant automated checks**

Run:

```powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest discover -s tests -v
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site/build_site.py
git diff --check
```

Expected: all tests pass, site build succeeds, and no whitespace errors occur.

- [ ] **Step 2: Run desktop and mobile browser QA**

At a local static preview, inspect `blog/2026-08-06-ai-work-design-future.html` at 1440px and 390px. Check that the title, metadata, note, portrait video, hero image, and first paragraph appear in that order; there is no horizontal overflow; video controls work; and the note remains legible.

- [ ] **Step 3: Reconcile generated files and review package**

Confirm the article frontmatter, output HTML, Reel `captions.md`, `README.md`, `posting-manifest.json`, `qa.json`, and `pre-post-confirmation.md` all use the final title, about29-second duration, 6-scene wording, and `review_ready_waiting_final_approval` state.

- [ ] **Step 4: Present final review assets and request publishing approval**

Show the local Reel, the article source/preview, exact caption, and remaining publication checklist. Ask for one explicit approval covering Vercel production deployment and direct Instagram Reel publication. Do not create a draft. After a published Reel, ask separately before Story and brand comment.

## Plan Self-Review

- Spec coverage: Task 1 covers placement and factual article note; Task 2 covers content introduction, full central-text narration, light original BGM, no speed-up, regenerated assets, and QA; Task 3 covers global MyBlog adoption and validation; Task 4 covers build, visual QA, approval, and publication boundary.
- Placeholder scan: all tasks name concrete files, commands, expected behavior, and test contracts. The FFmpeg inspection command uses the exact fallback binary already referenced by the existing Reel builder.
- Interface consistency: `authorship_note` is the sole article field; `BEATS` is the sole Reel scene source; `spoken_words`, `scene_starts`, and `create_background_music` are consumed by the Reel test and generator with the same names.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-06-ai-work-design-blog-reel-myblog.md`.

1. **Subagent-Driven** — a fresh subagent completes each task with separate review gates.
2. **Inline Execution** — execute the approved tasks in this session with checkpoints.

The user has already approved implementation and this change shares generated media assets, so proceed with **Inline Execution** while retaining the fresh-agent forward tests required for the MyBlog skill update.
