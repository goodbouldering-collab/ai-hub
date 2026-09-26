# AI相談: minimal photographic banners and focused navigation

Audience: independent shop owners and creative freelancers. AI helps make daily work lighter while the person keeps control.

The final 18 banners use sparse, photographic creative workspaces: one main tool or work product, restrained natural light, grey and wood tones, generous negative space. Each image has a different composition. Image provenance is in `minimal-images-20260926.json`. The earlier image manifest records a superseded draft. Factual portraits, blog photographs, Instagram images and portfolio screenshots remain unchanged.

Public: remove the secondary hero comparison block; purpose filters retain all six courses; shared native search dialog supports keyboard shortcuts. Admin: searchable task hub at exact `/admin`, while original blog editors and publishing forms stay available at their original routes. No auth, API or payment logic changes.

Validation on 2026-09-26: 9 Python tests and 25 Node tests passed. Candidate generation preserves all public links/forms and verifies unchanged baseline assets and runtime modules. Wrangler dry-run compilation passed. Native desktop/mobile browser verification is recorded separately in the delivery evidence before release.

Build the candidate using `scripts/build_focused_ux_release.py`; set `UX_RELEASE` to its directory for `tests/focused-ux.test.mjs`. The original pinned public release and authentication runtime are immutable inputs; only owned artwork, presentation CSS/JS, public HTML decoration, admin presentation and the login stylesheet version may change.
