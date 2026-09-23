# AI相談: small-business artwork and focused navigation (2026-09-24)

Audience: independent shop owners and creative freelancers. Message: AI helps make daily work lighter, while the person keeps control.

18 presentation images were individually generated with the built-in image tool and encoded as WebP. Scenes: maker atelier, florist orders, illustrator desk, website assembly, workshop delivery, maker exchange, bakery website, preparing a question, comparing prototypes, retaining methods, workspace entrance, product-photo review, cafe planning, furniture reference search, ceramics bookings, creative pinboard, climbing history, and booking-tool implementation. Shared prompt and source IDs: `makers-images-20260924.json`. Factual portraits, editorial photographs and portfolio screenshots are retained.

Public: remove the secondary hero comparison block; purpose filters retain all six courses; shared native search dialog with keyboard shortcut. Admin: searchable task hub at exact `/admin`, while existing blog editors and publishing forms remain available at their original routes. No auth/API/payment logic changes.

Verification:
- `python -m unittest discover -s tests -p test_focused_ux.py` (4)
- `python -m unittest discover -s tests -p test_art_direction.py` (3)
- `python -m unittest discover -s tests -p test_compact_home.py` (2)
- `node --test tests/soft-playground.test.mjs tests/studio-glass-motion.test.mjs` (20)
- `npm install --prefix tmp/dom-test jsdom --no-save --ignore-scripts --no-audit --no-fund`
- Build the candidate with `scripts/build_focused_ux_release.py`; set `UX_RELEASE` to it if not `tmp/makers-release`.
- `node --test tests/focused-ux.test.mjs` (5; JSDOM does not prove native dialog layout/focus trapping).
- Wrangler dry-run compilation succeeds. Builder checks every public link/form and baseline hashes, and permits only the two presentation runtime modules to change.

Real desktop/mobile visual QA is required before production release. IAB currently fails with `registered runtime ownership is missing`; alternative test Chrome approval requested. JEV source transmission was rejected by automatic review, so external review was not performed; local regression/review used instead.