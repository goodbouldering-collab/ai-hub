# Design QA — AI相談 彦根 consultation-first redesign

- source visual truth path: `C:\Users\yui\.codex\generated_images\019f51d4-0896-7f61-aca9-9ae0b2572283\exec-704c125e-a617-461b-93bf-ba586d8577d4.png`
- implementation screenshot path: `C:\VSCode\Project\ai-hub\tmp\design-qa-20260712\home-desktop-final.png`
- mobile screenshot path: `C:\VSCode\Project\ai-hub\tmp\design-qa-20260712\home-mobile.png`
- viewport: desktop 1280 x 720 browser viewport; mobile 390 x 844 override
- state: public homepage, initial loaded state

## Full-view comparison evidence

The selected direction and implementation were opened together for comparison. The implementation preserves the target's split hero, blue/white palette, compact four-item navigation, two-action hero, local workshop photograph, outcome-first content, three learning paths, selected proof, instructor, three-step flow, FAQ, and final consultation CTA. Existing resources remain available as secondary links rather than homepage inventory.

## Focused region comparison evidence

The hero was checked separately at desktop and mobile widths because typography, photo crop, and CTA hierarchy are the fidelity-critical surfaces. The mobile view has no horizontal overflow, keeps both primary actions visible, and uses the same workshop asset without stretching. The mobile menu opens successfully. Browser console warnings/errors: none on the public homepage.

## Required fidelity surfaces

- Fonts and typography: Noto Sans JP/Inter system retained; display hierarchy and short Japanese line lengths match the chosen direction. The final desktop heading keeps the outcome sentence together; mobile is allowed to wrap safely.
- Spacing and layout rhythm: split hero, generous white space, four-outcome band, three-path and three-proof grids match the target hierarchy. Mobile collapses to one column without clipping.
- Colors and tokens: deep blue `#075fc8`, white, pale blue, near-black, and restrained borders are consistent across public and admin source.
- Image quality and asset fidelity: the supplied Hikone workshop photo is used directly. Existing real project imagery and speaker portrait are reused; no placeholder or CSS-drawn imagery was substituted.
- Copy and content: copy is shorter than the old site and keeps consultation, courses, outcomes, proof, flow, FAQ, and booking as the only primary story.

## Comparison history

1. P1: the original homepage exposed Red Cross, materials, metrics, and service-map choices above the booking path. Fixed by replacing the public composition with consultation-first sections while keeping old resources on their existing routes.
2. P2: the first implementation inherited an orange navigation CTA and wrapped the desktop outcome headline too early. Fixed with the scoped blue CTA override and a desktop no-wrap outcome line, with a mobile wrap exception.
3. P2: mobile navigation and overflow required explicit verification. Confirmed menu open state and `scrollWidth == clientWidth` at the mobile breakpoint.

## Findings

No actionable P0/P1/P2 visual mismatches remain on the selected public-homepage target. The protected cloud admin page is not part of the selected visual mock; its source was aligned to the same tokens and reduced to three primary work entries. Its authenticated production rendering must be checked separately after deployment.

## Primary interactions tested

- Desktop and mobile homepage rendering
- Mobile menu open state
- Local anchor/navigation structure
- Local reference link scan across 81 HTML files
- Browser console error/warning check on the public homepage

## Follow-up polish

- P3: replace selected-work generic project imagery with dedicated screenshots when fresh captures are available.
- P3: authenticated admin page can receive a second visual pass using real operational data after production access.

final result: passed
