# Blog Title Production Placement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the Vercel/Supabase boundary article with the approved production-ready, five-placement framing.

**Architecture:** The Markdown article remains the editorial source; `site/build_site.py` renders all public pages. The existing unittest gains a precise title-and-H2 contract, preventing the reader-facing structure from drifting.

**Tech Stack:** Markdown frontmatter, Python 3.12, unittest, static HTML generation, GitHub main deployment, Vercel.

## Global Constraints

- Final title is exactly `ウェブサイト公開から本格稼働へ：AIで作ったWebサービスの5つの置き場所`.
- Preserve article URL, date, authorship note, assets, official references, and factual safety boundaries.
- Use only the isolated worktree; do not include root-checkout changes.

## File Map

- `content/blog/2026-08-08-vercel-supabase-d1-r2-boundaries.md`: title, metadata, introduction, H2, FAQ, and CTA source.
- `tests/test_blog_authorship_note.py`: regression contract for the article.
- `site/dist/blog/2026-08-08-vercel-supabase-d1-r2-boundaries.html`: generated article.
- `site/dist/blog/index.html`, `site/dist/index.html`, `site/dist/sitemap.xml`: generated discovery output.

### Task 1: Create the editorial regression contract

- [ ] Set the test title constant to the approved final title.
- [ ] Add the four approved H2 headings as an ordered contract.
- [ ] Run `python -m unittest tests/test_blog_authorship_note.py` and observe the expected failure before editing the article.

### Task 2: Edit the article source

- [ ] Update frontmatter title, summary, and goal.
- [ ] Rewrite the opening to define the five placement decisions as the start of production readiness.
- [ ] Replace the four H2 headings with the approved headings.
- [ ] Align FAQ questions and CTA with long-term operation while retaining all specific-service comparisons and safety notes.
- [ ] Run the focused unittest and verify it passes.

### Task 3: Generate and publish

- [ ] Run `site/build_site.py` with the workspace Python.
- [ ] Confirm generated article, blog index, top page, and sitemap contain the final title.
- [ ] Review the scoped diff, run `git diff --check`, commit only the source, test, docs, and generated output.
- [ ] Push the scoped commit to main, wait for Vercel READY, and verify the canonical article on desktop and iPhone widths.
