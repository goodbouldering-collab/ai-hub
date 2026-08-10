# AI時代、経験者が再び強くなる理由 — Reel連携 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 公開済みAI相談ブログを根拠ある縦型Reelへ再編集し、同一MP4を記事冒頭へ埋め込み、Instagram投稿・ストーリーズ・店舗コメントとmyreel記録まで一貫して完成させる。

**Architecture:** `media/output/myreel/2026-08-10-ai-experience-3d-reality/` を独立した再生成可能なキャンペーン記録とする。既存の音声QA付きReelビルダーを、元記事の図版と5つの中心文へ差し替える。同一の `reel.mp4` と `cover.png` を `site/static/media/ai-experience-3d-20260810/` へ複製し、記事frontmatterだけでタイトル直下に縦型動画を出す。公開後URLと投稿結果はキャンペーンの `posting-manifest.json` に追記する。

**Tech Stack:** Python 3.12、edge-tts、Pillow、FFmpeg、静的サイト生成 `site/build_site.py`、Vercel、Instagram Web UI。

## Global Constraints

- 投稿先はAI相談の正式アカウント `@climbingconsul` だけにする。
- 記事URLは `https://ai-hub-jp.vercel.app/blog/2026-08-09-ai-experience-3d-reality.html` とする。
- 中央文は5場面・各3行以内、`narration` は中央文を改行・句読点以外で変えない。
- ナレーションは `ja-JP-NanamiNeural`、速度 `+0%` を保つ。
- BGMは外部サンプルなしの自作非ボーカル、ナレーション中のダッキングは5〜8dB、声はduck後BGMより8dB以上大きくする。
- 記事の順序は `タイトル → authorship_note → video → hero → 本文` とし、記事一覧だけに動画を置かない。
- Instagramの最終シェア、ストーリーズ、店舗コメントは、画面に見えるアカウント・URL・文面を確認してから行う。CAPTCHA、追加認証、警告、別アカウントでは停止する。

---

### Task 1: 再生成可能なReelキャンペーンを作る

**Files:**
- Create: `media/output/myreel/2026-08-10-ai-experience-3d-reality/build_reel.py`
- Create: `media/output/myreel/2026-08-10-ai-experience-3d-reality/test_build_reel.py`
- Create: `media/output/myreel/2026-08-10-ai-experience-3d-reality/source/*.png`
- Create: `media/output/myreel/2026-08-10-ai-experience-3d-reality/README.md`
- Create: `media/output/myreel/2026-08-10-ai-experience-3d-reality/captions.md`
- Create: `media/output/myreel/2026-08-10-ai-experience-3d-reality/tone.md`

**Interfaces:**
- Consumes: 既存テンプレート `media/output/myreel/2026-08-06-ai-work-design-future/build_reel.py`、記事図版 `site/static/img/blog-ai-experience-3d-*-20260809.png`。
- Produces: `reel.mp4`、`cover.png`、`qa.json`、`posting-manifest.json`、`story.md`、`review.html`。

- [ ] **Step 1: 記事との対応を固定する失敗テストを書く**

```python
def test_five_scenes_match_the_article_and_narration():
    expected = [
        ["ブログ", "AI時代、経験者が再び強くなる理由"],
        ["AIは", "仮説を速くつくれる"],
        ["現実で試し、", "確かめるのは人間"],
        ["経験は、AIの答えを", "使える形へ直す"],
        ["AIと人間と現実", "この往復が仕事を強くする"],
    ]
    self.assertEqual([beat["text"] for beat in self.module.BEATS], expected)
    for beat in self.module.BEATS:
        self.assertEqual(
            self.module.spoken_words("".join(beat["text"])),
            self.module.spoken_words(beat["narration"]),
        )
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `.& .\.venv\Scripts\python.exe -m unittest media\output\myreel\2026-08-10-ai-experience-3d-reality\test_build_reel.py -v`

Expected: FAIL because the campaign module is not present yet.

- [ ] **Step 3: 既存の音声QA付きビルダーを複製して最小限差し替える**

```python
BLOG_URL = "https://ai-hub-jp.vercel.app/blog/2026-08-09-ai-experience-3d-reality.html"
ACCOUNT = "@climbingconsul"
ARTICLE_TITLE = "AI時代、経験者が再び強くなる理由"
BEATS = [
    {"label": "記事紹介", "text": ["ブログ", "AI時代、経験者が再び強くなる理由"], "narration": "ブログ。AI時代、経験者が再び強くなる理由。", "duration_seconds": 4.6, "image": "blog-ai-experience-3d-hero-20260809.png"},
    {"label": "仮説", "text": ["AIは", "仮説を速くつくれる"], "narration": "AIは、仮説を速くつくれる。", "duration_seconds": 4.2, "image": "blog-ai-experience-3d-information-and-reality-20260809.png"},
    {"label": "現実", "text": ["現実で試し、", "確かめるのは人間"], "narration": "現実で試し、確かめるのは人間。", "duration_seconds": 4.8, "image": "blog-ai-experience-3d-reality-check-20260809.png"},
    {"label": "経験", "text": ["経験は、AIの答えを", "使える形へ直す"], "narration": "経験は、AIの答えを使える形へ直す。", "duration_seconds": 5.2, "image": "blog-ai-experience-3d-expert-judgment-20260809.png"},
    {"label": "往復", "text": ["AIと人間と現実", "この往復が仕事を強くする"], "narration": "AIと人間と現実。この往復が仕事を強くする。", "duration_seconds": 5.4, "image": "blog-ai-experience-3d-loop-20260809.png"},
]
```

- [ ] **Step 4: テストを通す**

Run: `.& .\.venv\Scripts\python.exe -m unittest media\output\myreel\2026-08-10-ai-experience-3d-reality\test_build_reel.py -v`

Expected: PASS; 5場面、中央文/音声の正規化一致、`+0%`、自作BGM・ダッキングの契約を確認。

- [ ] **Step 5: キャンペーンのソースと説明をコミットする**

```powershell
git add media/output/myreel/2026-08-10-ai-experience-3d-reality
git commit -m "feat: prepare AI experience Reel campaign"
```

### Task 2: 完成MP4を生成して記事冒頭へ接続する

**Files:**
- Modify: `content/blog/2026-08-09-ai-experience-3d-reality.md:3-15`
- Create: `site/static/media/ai-experience-3d-20260810/reel.mp4`
- Create: `site/static/media/ai-experience-3d-20260810/cover.png`
- Modify: `media/output/myreel/2026-08-10-ai-experience-3d-reality/test_build_reel.py`

**Interfaces:**
- Consumes: Task 1の `reel.mp4` と `cover.png`。
- Produces: 記事frontmatterの `video`、`video_poster`、`video_orientation` と、記事内埋め込みを検証するasset hashテスト。

- [ ] **Step 1: サイト用コピーと記事frontmatterの失敗テストを書く**

```python
pairs = (
    (reel_root / "reel.mp4", repo_root / "site/static/media/ai-experience-3d-20260810/reel.mp4"),
    (reel_root / "cover.png", repo_root / "site/static/media/ai-experience-3d-20260810/cover.png"),
)
self.assertIn("video: /media/ai-experience-3d-20260810/reel.mp4", article_source)
self.assertIn("video_orientation: portrait", article_source)
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `.& .\.venv\Scripts\python.exe -m unittest media\output\myreel\2026-08-10-ai-experience-3d-reality\test_build_reel.py -v`

Expected: FAIL because site media and frontmatter are absent.

- [ ] **Step 3: ビルド、同一ファイルコピー、frontmatter追加を行う**

```yaml
video: /media/ai-experience-3d-20260810/reel.mp4
video_poster: /media/ai-experience-3d-20260810/cover.png
video_label: AI時代、経験者が再び強くなる理由を約24秒・女性ナレーション・軽いBGMで整理する動画
video_caption: AIの仮説を現実で試し、経験としてAIへ戻す。この往復を約24秒で紹介します。
video_orientation: portrait
video_fullscreen_on_play: mobile
```

- [ ] **Step 4: ビルド・hash・静的生成を検証する**

Run: `.& .\.venv\Scripts\python.exe media\output\myreel\2026-08-10-ai-experience-3d-reality\build_reel.py; .& .\.venv\Scripts\python.exe -m unittest media\output\myreel\2026-08-10-ai-experience-3d-reality\test_build_reel.py -v; .& .\.venv\Scripts\python.exe site\build_site.py`

Expected: `qa.json` の全チェックが真、MP4/coverのSHA-256一致、生成HTMLにタイトル直下の縦型videoがある。

- [ ] **Step 5: 実装をコミットする**

```powershell
git add content/blog/2026-08-09-ai-experience-3d-reality.md site/static/media/ai-experience-3d-20260810 media/output/myreel/2026-08-10-ai-experience-3d-reality
git commit -m "feat: embed AI experience Reel in blog"
```

### Task 3: myblogとmyreelへ恒久の連携ルールを記録する

**Files:**
- Modify: `C:/Users/yui/.codex/skills/myblog/SKILL.md`
- Modify: `C:/Users/yui/.codex/skills/myblog/agents/openai.yaml`
- Modify: `C:/Users/yui/.codex/skills/myreel/SKILL.md`
- Modify: `C:/Users/yui/.codex/skills/myreel/agents/openai.yaml`

**Interfaces:**
- Consumes: Task 2の `video` frontmatter設計と `posting-manifest.json` 形式。
- Produces: 将来のmyblog→myreel実行で、記事冒頭MP4と公開記録を必須にする指示。

- [ ] **Step 1: 連携文言の検証条件を決める**

```text
MyBlog: 「公開済みmyreelと同一の完成MP4を、著者注記の直後に埋め込む」
MyReel: 「元記事URL、site_media_url、Instagram Reel URL、Story、コメント、検証結果をposting-manifestへ残す」
```

- [ ] **Step 2: 既存skillに連携文言がないことを確認する**

Run: `rg -n "同一の完成MP4|site_media_url|Instagram Reel URL" C:\Users\yui\.codex\skills\myblog C:\Users\yui\.codex\skills\myreel`

Expected: no matching contract before this change.

- [ ] **Step 3: 人に渡せる説明、ワークフロー、agent metadataを同時に更新する**

```yaml
default_prompt: "Use $myblog and $myreel to publish a blog-linked Reel, embed the same verified MP4 directly below the article authorship note, and record the public Reel, Story, comment, site-media URL, and QA results."
```

- [ ] **Step 4: YAMLと4ファイルの文言を再読して検証する**

Run: `Get-Content C:\Users\yui\.codex\skills\myblog\agents\openai.yaml; Get-Content C:\Users\yui\.codex\skills\myreel\agents\openai.yaml; rg -n "同一の完成MP4|posting-manifest|site_media_url|著者注記" C:\Users\yui\.codex\skills\myblog\SKILL.md C:\Users\yui\.codex\skills\myreel\SKILL.md`

Expected: 両skillの説明と実行手順が同じ連携を示し、YAMLは有効なインデントを保つ。

### Task 4: 本番公開、Instagram投稿、公開結果の記録を確認する

**Files:**
- Modify: `media/output/myreel/2026-08-10-ai-experience-3d-reality/posting-manifest.json`
- Modify: `media/output/myreel/2026-08-10-ai-experience-3d-reality/README.md`

**Interfaces:**
- Consumes: Task 2のデプロイ済み記事MP4と、正しいInstagramアカウントでのReel投稿結果。
- Produces: 本番URL、Instagram Reel URL、ストーリーズ・コメントの結果を含む最終myreel記録。

- [ ] **Step 1: 本番公開前にローカル表示を確認する**

Run: `.& .\.venv\Scripts\python.exe site\build_site.py; rg -n "ai-experience-3d-20260810/reel.mp4|article-video--portrait" site\dist\blog\2026-08-09-ai-experience-3d-reality.html`

Expected: HTMLが `authorship_note` の次、heroの前に同一MP4を含む。

- [ ] **Step 2: 関連ファイルだけをpushしてVercel本番を確認する**

```powershell
git push origin HEAD:main
```

Expected: Vercel READY、記事URL・MP4・coverがHTTP 200、PCと390pxで動画とCTAにオーバーフローがない。

- [ ] **Step 3: Instagramの最終投稿画面で対象を再確認する**

```text
Account: @climbingconsul
Video: media/output/myreel/2026-08-10-ai-experience-3d-reality/reel.mp4
Caption final URL: https://ai-hub-jp.vercel.app/blog/2026-08-09-ai-experience-3d-reality.html
```

Expected: 警告・CAPTCHA・追加認証がなく、最終シェア前でアカウント、動画、本文が一致する。

- [ ] **Step 4: Reel、ストーリーズ、店舗コメントを直接公開する**

Run: Instagram UIでReelを公開後、同じReelをストーリーズへ共有し、リンクラベル `詳細はこちら` を下部中央に設定して共有する。続けて同Reelへ店舗コメントを投稿する。

Expected: Reel公開URL、Story共有完了、コメント表示を確認する。Chromeがストーリー機能を提供しない場合は、Reel公開URL、正確なStory文、リンクURL、ラベル、下部中央配置、コメントをモバイル手順として記録し、未完了を明示する。

- [ ] **Step 5: myreel記録を最終化してコミットする**

```json
{
  "publication": {
    "instagram_reel_url": "<verified public URL>",
    "account": "@climbingconsul",
    "article_url": "https://ai-hub-jp.vercel.app/blog/2026-08-09-ai-experience-3d-reality.html",
    "site_media_url": "https://ai-hub-jp.vercel.app/media/ai-experience-3d-20260810/reel.mp4"
  }
}
```

Run: `git add media/output/myreel/2026-08-10-ai-experience-3d-reality; git commit -m "docs: record AI experience Reel publication"; git push origin HEAD:main`

Expected: public Reel URL and every completed/unavailable social action are distinguishable in the durable record.

## Plan Self-Review

- Spec coverage: Task 1 covers branded video and narration/BGM constraints; Task 2 covers identical MP4 embedding; Task 3 makes the requested behavior permanent in both custom skills; Task 4 covers production, Instagram, Story, comment, and record.
- Placeholder scan: No execution requirement is left as TBD/TODO. The final public Reel URL is intentionally an observed value, never guessed.
- Interface consistency: Task 1 produces the exact package consumed by Task 2; Task 2 exposes the site media path recorded by Task 4; Task 3 codifies the same `posting-manifest` contract.
