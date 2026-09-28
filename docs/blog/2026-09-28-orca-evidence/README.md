# Orca article: evidence revision

Purpose: explain Orca's concrete benefit to readers new to agent development, using a short story and verifiable quantities.

Published route: https://aiclimb.aiclimb.workers.dev/blog/2026-09-28-orca-ade-ai-manager

Final title: 3つのAIを同時に動かし、良い案を選ぶ。Orca ADEのすごさを実例で見る

The title describes the official parallel-agent workflow. It does not promise measured acceleration. The 33-repository installation is operator experience; the approximately 15-session workload is a separate user's report; UI repair examples are explanatory, not claimed experiments.

## Sources checked on 2026-09-28

- Local operator RESULT.md (dated 2026-09-27) and orca-repos-live.json: 33 registered repositories, no new clones or worktrees during installation; Codex connection test only. Hashes and aggregate counts are in data.json. Original files and private repository identities remain outside the published article.
- https://www.reddit.com/r/ClaudeCode/comments/1vwjgyv/orca_ade_is_incredible/ : trader_tick reports 2 computers, 5 repositories, 2–6 sessions per repository, approximately 15 sessions. The author says they use Docker containers; not evidence for worktree throughput. No average or speed inference.
- https://www.onorca.dev/docs/recipes/parallel-agents : three agents on separate worktrees, compare changes and choose a result. No measured speed comparison adopted.
- https://www.onorca.dev/docs/model/worktrees : per-task branches and files; not a security sandbox claim.
- https://www.onorca.dev/docs/browser/design-mode : HTML, computed CSS, cropped image, plus source file/line when available.
- https://www.onorca.dev/docs/review/diff-viewer : review code changes before shipping.
- https://www.onorca.dev/docs/mobile : connected desktop required, beta companion.
- https://www.onorca.dev/docs and /docs/install : overview and reader's next action.

## Assets and reproducibility

Four charts/diagrams use scripts/plot_orca_evidence.py, data.json, matplotlib 3.10.8, and Windows Meiryo. The 0–40 count axis starts at zero; the session range is 2–6; 15 same-color dots do not imply a repository allocation. SVG exports are retained under charts/. Site PNGs are in site/static/img/ with -evidence-20260928 names.

Hero: generated with the built-in image generator, concept illustration, not product UI or official logo. Brief: premium magazine, midnight navy, ivory architecture, amber and turquoise; one brief, three separate workbenches, three alternatives at a human review desk; elegant orca sculpture; only ORCA ADE lettering; no robots, childish mascot, fake statistics, or provider logos. Original generated PNG was copied, not altered.

Reviewed all five images at full size. No overlapping labels or clipped text. Captions and alt text reproduce the key numbers for mobile/accessibility. Browser PC/mobile layout verification remains separately recorded in the delivery record; image inspection is not a substitute.

## Release boundary

Builder: scripts/build_orca_evidence_release.py
Baseline: canonical .orca-simple-release-20260928/public, committed source cdb995efb4d98294f47f6736103363eade6edefd, Cloudflare version 74f5ef00-805b-42a7-860b-e1f36adb78d7.
Changes: existing article and its two index cards, five new image assets. 523 prior files retained unchanged. Existing sitemap route retained once. Deployment retains deployment/ai-news/published-worker.mjs.
