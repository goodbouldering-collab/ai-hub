# Hero 60-Second Diagnosis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Move 「迷ったら60秒診断」 into the public AI相談 hero as the primary conversion path, use plain-language work-problem questions, and deploy the verified result to Vercel production.

**Architecture:** site/build_portal.py remains the single renderer for the public homepage and its inline CSS/JavaScript. The hero uses a progressively enhanced anchor: without JavaScript it leads to #packages; with JavaScript it opens the existing modal. The modal scores four work-outcome recommendations and always offers the existing free-consult booking URL plus the course list, so it never depends on the absent legacy .packages-grid filter.

**Tech Stack:** Python 3.12 static renderer, inline HTML/CSS/JavaScript, Python unittest, Git, GitHub, Vercel.

## Global Constraints

- Public-home source is site/build_portal.py; generated artifact is site/dist/index.html.
- Preserve the current regional kicker, hero headline, 6% proof, imagery, colors, course URLs, prices, Square routes, online salon, materials, and admin pages.
- Use the existing CONSULT_BOOK_URL for every diagnostic result primary reservation CTA; do not create a new URL or form.
- The exact primary hero CTA is 「迷ったら60秒診断をはじめる →」; the exact helper heading is 「何から始めるか、1分で見える。」.
- The hero must retain a no-JavaScript route to #packages, work at desktop and 390px iPhone width, have no horizontal overflow, and honor the existing reduced-motion behavior.
- Use test-first development. Build generated HTML before any test that reads site/dist/index.html.
- Only the isolated worktree C:\Project\AI相談\_worktrees\hero-60sec-diagnosis is editable; never stage unrelated files from the primary checkout.

---

## File Structure

- site/build_portal.py — renders the hero, embeds the diagnosis modal/logic, and owns public-home CSS.
- tests/test_hero_60sec_diagnosis.py — regression contract for rendered hero ordering, diagnostic content, working links, and accessible close behavior.
- site/dist/index.html — generated page; never hand-edit.

### Task 1: Add the failing diagnosis conversion contract

**Files:**
- Create: tests/test_hero_60sec_diagnosis.py
- Read: site/build_portal.py, site/dist/index.html

**Interfaces:**
- Consumes: generated site/dist/index.html and renderer source text.
- Produces: a deterministic unittest contract that Task 2 and Task 3 must make pass.

- [ ] **Step 1: Create the failing rendered-page test**

Create tests/test_hero_60sec_diagnosis.py with a helper that extracts the first .focus-hero section and asserts the desired conversion order.

~~~python
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "build_portal.py"
INDEX = ROOT / "site" / "dist" / "index.html"
BOOKING_URL = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"

class Hero60SecondDiagnosisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.index_html = INDEX.read_text(encoding="utf-8")
        start = cls.index_html.index("class='focus-hero'")
        cls.hero = cls.index_html[start:cls.index_html.index("</section>", start)]

    def test_hero_makes_the_diagnosis_the_first_conversion_action(self) -> None:
        primary = "迷ったら60秒診断をはじめる →"
        self.assertIn(primary, self.hero)
        self.assertIn("何から始めるか、1分で見える。", self.hero)
        self.assertIn("3問で完了。結果を見てから、予約するか決められます。", self.hero)
        self.assertRegex(
            self.hero,
            r"<a class='focus-btn primary hero-diagnose-button diagnose-open' href='#packages'>"
            + re.escape(primary) + r"</a>",
        )
        self.assertRegex(
            self.hero,
            re.escape(BOOKING_URL) + r"' target='_blank' rel='noopener'>無料相談の日程を選ぶ</a>",
        )
        self.assertLess(self.hero.index(primary), self.hero.index("無料相談の日程を選ぶ"))

    def test_diagnosis_uses_work_problem_copy_and_real_result_actions(self) -> None:
        expected = (
            "迷ったら60秒診断",
            "いまの仕事に合う入口を、3つの質問で整理します。",
            "いま一番近い悩みは？",
            "今日、どこまで進めたい？",
            "最初の一歩は、どう進めたい？",
            "まずは、任せたい仕事を一つ決める",
            "告知・集客の型を一つ作る",
            "重い事務を一つ軽くする",
            "サイト・業務改善の道筋を決める",
            "無料相談の日程を選ぶ",
            "講習・相談コースを見る",
        )
        for text in expected:
            with self.subTest(text=text):
                self.assertIn(text, self.index_html)
        self.assertIn("href='#packages'", self.index_html)
        self.assertIn(BOOKING_URL, self.index_html)

    def test_diagnosis_has_accessible_output_and_no_javascript_fallback(self) -> None:
        self.assertIn("aria-live='polite'", self.index_html)
        self.assertIn("aria-labelledby='diagnose-title'", self.index_html)
        self.assertRegex(
            self.hero,
            r"<a class='focus-btn primary hero-diagnose-button diagnose-open' href='#packages'>",
        )

    def test_legacy_duplicate_diagnosis_copy_is_not_rendered(self) -> None:
        self.assertNotIn("60秒診断｜無料相談・個別相談・講習・伴走のどれ？", self.index_html)
        self.assertEqual(self.index_html.count("迷ったら60秒診断"), 2)
~~~

- [ ] **Step 2: Run the new test to prove it is red**

Run:

~~~powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_hero_60sec_diagnosis -v
~~~

Expected: the first test fails because the hero still begins with 「講習・個別相談を見る」; the content and keyboard contract tests fail because the old diagnosis data and behavior are still rendered.

- [ ] **Step 3: Commit the red test contract**

~~~powershell
git add tests/test_hero_60sec_diagnosis.py
git commit -m "test: define hero diagnosis conversion contract"
~~~

### Task 2: Move the primary diagnostic entry into the hero

**Files:**
- Modify: site/build_portal.py in _render_hero_focused and FOCUSED_PORTAL_CSS
- Modify: tests/test_hero_60sec_diagnosis.py
- Generated: site/dist/index.html

**Interfaces:**
- Consumes: .focus-actions, CONSULT_BOOK_URL, and the .diagnose-open click hook.
- Produces: one hero-owned progressive-enhancement trigger with class hero-diagnose-button diagnose-open, plus responsive helper styles.

- [ ] **Step 1: Extend the red test with hero-boundary and mobile-style assertions**

~~~python
    def test_hero_diagnosis_helper_stays_inside_the_action_group(self) -> None:
        self.assertIn("class='hero-diagnose-cta'", self.hero)
        self.assertIn(".hero-diagnose-cta {", self.source)
        self.assertIn(".hero-diagnose-cta .focus-btn { width:100%; }", self.source)
        self.assertNotIn("診断CTAをはじめる", self.index_html)
~~~

- [ ] **Step 2: Run the new assertion and confirm it fails**

~~~powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_hero_60sec_diagnosis.Hero60SecondDiagnosisTest.test_hero_diagnosis_helper_stays_inside_the_action_group -v
~~~

Expected: FAIL because hero-diagnose-cta has not yet been rendered or styled.

- [ ] **Step 3: Render the approved hero copy and direct booking CTA**

Replace the current .focus-actions markup in _render_hero_focused with this order while retaining the existing kicker, headline, advantage panel, and material link.

~~~python
"<p class='focus-lead'>告知・事務・集客に追われる方へ。AIが気になるけれど、何から始めるか迷う方へ。3つの質問で、いまの仕事に合う次の一歩を提案します。</p>"
"<div class='focus-actions'>"
"<div class='hero-diagnose-cta'><span class='hero-diagnose-eyebrow'>何から始めるか、1分で見える。</span>"
"<a class='focus-btn primary hero-diagnose-button diagnose-open' href='#packages'>迷ったら60秒診断をはじめる →</a>"
"<small>3問で完了。結果を見てから、予約するか決められます。</small></div>"
f"<a class='focus-btn secondary' href='{CONSULT_BOOK_URL}' target='_blank' rel='noopener'>無料相談の日程を選ぶ</a>"
"<a class='hero-text-link' href='/lectures/index.html'>受講資料 <span aria-hidden='true'>→</span></a></div>"
~~~

Add narrowly scoped CSS near the existing .focus-actions rules.

~~~css
.hero-diagnose-cta { display:flex; flex-direction:column; gap:6px; min-width:min(100%,310px); }
.hero-diagnose-eyebrow { color:var(--focus-blue); font-size:13px; font-weight:900; line-height:1.35; }
.hero-diagnose-cta small { color:var(--focus-muted); font-size:12px; font-weight:700; line-height:1.5; }
.hero-diagnose-button { cursor:pointer; }
@media (max-width:680px) {
  .hero-diagnose-cta { width:100%; }
  .hero-diagnose-cta .focus-btn { width:100%; }
}
~~~

- [ ] **Step 4: Regenerate and run the Task 1/2 contract**

~~~powershell
$env:AIWATCH_PORTFOLIO_NO_FETCH = '1'
& '.\.venv\Scripts\python.exe' site\build_portal.py
& '.\.venv\Scripts\python.exe' -m unittest tests.test_hero_60sec_diagnosis.Hero60SecondDiagnosisTest.test_hero_makes_the_diagnosis_the_first_conversion_action tests.test_hero_60sec_diagnosis.Hero60SecondDiagnosisTest.test_hero_diagnosis_helper_stays_inside_the_action_group -v
~~~

Expected: both hero-specific assertions pass. Do not run the still-red future diagnosis-content assertion in this step.

- [ ] **Step 5: Keep the partial feature uncommitted and continue immediately to Task 3**

The test module intentionally includes the remaining red diagnosis behavior contract. Do not create a commit with a failing full test module; the green commit is made after Task 3.

### Task 3: Rewrite diagnosis questions, results, and close behavior

**Files:**
- Modify: site/build_portal.py in HEADER_JS, _render_diagnose_modal, _render_compact_course_cards, and _render_focused_main
- Modify: tests/test_hero_60sec_diagnosis.py
- Generated: site/dist/index.html

**Interfaces:**
- Consumes: CONSULT_BOOK_URL, #packages, .diagnose-open, .diagnose-close, and .diagnose-body.
- Produces: start, promotion, office, and flow result keys; a lastTrigger reference for focus restoration; one rendered diagnosis opener in the hero.

- [ ] **Step 1: Add red expectations for all four results and close behavior**

~~~python
    def test_result_actions_do_not_use_the_removed_card_filter(self) -> None:
        self.assertNotIn("data-focus-level", self.index_html)
        self.assertNotIn("この講座を見る →", self.index_html)
        self.assertRegex(
            self.index_html,
            re.escape(BOOKING_URL) + r'" target="_blank" rel="noopener" data-close-diag>無料相談の日程を選ぶ</a>',
        )
        self.assertIn('href="#packages" data-close-diag>講習・相談コースを見る</a>', self.index_html)
~~~

- [ ] **Step 2: Run the targeted assertion and confirm it fails**

~~~powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_hero_60sec_diagnosis.Hero60SecondDiagnosisTest.test_result_actions_do_not_use_the_removed_card_filter -v
~~~

Expected: FAIL because the old result output still emits data-focus-level, 「この講座を見る →」, and does not contain the two approved result actions.

- [ ] **Step 3: Replace the diagnostic data and result actions**

Use these question and result key structures inside the existing diagnosis IIFE. Each answer must increment one of start, promotion, office, or flow; retain the existing three-step progress rendering.

~~~javascript
var QUESTIONS = [
  { q: 'いま一番近い悩みは？', a: [
    { label: 'AIを使う前に、何から頼めるか知りたい', key: 'start' },
    { label: '告知や集客を、もっと伝わる形にしたい', key: 'promotion' },
    { label: '事務や返信にかかる時間を減らしたい', key: 'office' },
    { label: 'サイト・予約・業務の流れを整えたい', key: 'flow' }
  ]},
  { q: '今日、どこまで進めたい？', a: [
    { label: 'まず話して、優先順位を決めたい', key: 'start' },
    { label: '投稿文や画像などを一つ作りたい', key: 'promotion' },
    { label: '自分用の手順にして残したい', key: 'office' },
    { label: '関係者と進め方を決めたい', key: 'flow' }
  ]},
  { q: '最初の一歩は、どう進めたい？', a: [
    { label: '無料相談で入口を整理したい', key: 'start' },
    { label: '講習で作りながら学びたい', key: 'promotion' },
    { label: '対面・オンラインで相談したい', key: 'office' },
    { label: '長く使える仕組みにしたい', key: 'flow' }
  ]}
];
var RESULT = {
  start: { title: 'まずは、任せたい仕事を一つ決める', desc: '今の課題を聞き、AIに頼む最初の仕事と進め方を一緒に整理します。' },
  promotion: { title: '告知・集客の型を一つ作る', desc: '誰に何を伝えるかを決め、投稿文・画像・次回の告知手順まで形にします。' },
  office: { title: '重い事務を一つ軽くする', desc: '返信、要約、報告、引き継ぎなどから一つ選び、確認できる手順にします。' },
  flow: { title: 'サイト・業務改善の道筋を決める', desc: '予約、問い合わせ、更新、業務の流れを整理し、残すものと直す順番を決めます。' }
};
var CONSULT_BOOK_URL = __CONSULT_BOOK_URL__;
~~~

Render every result with these exact actions.

~~~javascript
'<a class="btn btn-primary" href="' + CONSULT_BOOK_URL + '" target="_blank" rel="noopener" data-close-diag>無料相談の日程を選ぶ</a>' +
'<a class="btn btn-secondary" href="#packages" data-close-diag>講習・相談コースを見る</a>'
~~~

Change only the closing line of the existing HEADER_JS assignment, which currently ends with the script close and a triple quote. Keep the opening assignment and all JavaScript braces unchanged; append this exact replacement call to the closing line so the placeholder becomes a JSON string.

~~~python
</script>""".replace("__CONSULT_BOOK_URL__", json.dumps(CONSULT_BOOK_URL))
~~~

When rendering choices, use data-key rather than data-lv and increment scores with that same attribute.

~~~javascript
Q.a.forEach(function(opt){ h += '<button class="diag-opt" data-key="' + opt.key + '">' + opt.label + '</button>'; });
if (opt) { scores[opt.getAttribute('data-key')]++; step++; render(); return; }
~~~

- [ ] **Step 4: Implement progressive enhancement and keyboard closure**

~~~javascript
var lastTrigger = null;
function open(trigger) {
  lastTrigger = trigger || document.activeElement;
  step = 0;
  scores = { start: 0, promotion: 0, office: 0, flow: 0 };
  render();
  modal.classList.add('open');
  modal.querySelector('.diagnose-close').focus();
}
function close() {
  modal.classList.remove('open');
  if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
}
document.addEventListener('click', function(e) {
  var dOpen = e.target.closest('.diagnose-open');
  if (dOpen) { e.preventDefault(); open(dOpen); return; }
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape' && modal.classList.contains('open')) close();
});
~~~

Set the modal title to 「迷ったら60秒診断」, add the approved helper text, and add aria-live='polite' to .diagnose-body.

- [ ] **Step 5: Remove duplicate and dead conversion paths**

Delete the package-row diagnosis button/copy and the course-quick-actions diagnosis button. Remove focusLevel, .packages-grid access, data-focus-level, and the old beginner/intermediate/implementation/advanced diagnostic result data. Keep the course-list anchor and material link intact.

- [ ] **Step 6: Rebuild and run the focused contracts**

~~~powershell
$env:AIWATCH_PORTFOLIO_NO_FETCH = '1'
& '.\.venv\Scripts\python.exe' site\build_portal.py
& '.\.venv\Scripts\python.exe' -m unittest tests.test_hero_60sec_diagnosis tests.test_hero_text_readability tests.test_course_material_mapping -v
~~~

Expected: all diagnosis, hero readability, and course-material tests pass; built site/dist/index.html has one hero opener and the two valid result actions.

- [ ] **Step 7: Commit the diagnostic behavior update**

~~~powershell
git add site/build_portal.py tests/test_hero_60sec_diagnosis.py site/dist/index.html
git commit -m "feat: route diagnosis results to next actions"
~~~

### Task 4: Verify, release, and prove production behavior

**Files:**
- Verify: site/build_portal.py, site/build_site.py, site/dist/index.html, tests/test_hero_60sec_diagnosis.py
- No hand edits to generated HTML

**Interfaces:**
- Consumes: the completed static renderer and Git-connected Vercel project.
- Produces: a production https://aiclimb.vercel.app homepage with evidence for desktop, iPhone, diagnosis, and real booking links.

- [ ] **Step 1: Rebuild all static output and run every automated check**

~~~powershell
$env:AIWATCH_PORTFOLIO_NO_FETCH = '1'
& '.\.venv\Scripts\python.exe' site\build_portal.py
& '.\.venv\Scripts\python.exe' site\build_site.py
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
git diff --check
~~~

Expected: every unittest passes, both builders exit with code 0, and git diff --check has no output.

- [ ] **Step 2: Browser-verify desktop and iPhone before release**

Serve site/dist locally and inspect at 1440px and 390px.

At both widths verify:

1. The diagnosis CTA is the first action, fully visible, readable, and has no horizontal overflow.
2. Clicking it opens the modal; three answers lead to a result with 「無料相談の日程を選ぶ」 and 「講習・相談コースを見る」.
3. Esc, the close button, and the backdrop close the modal; keyboard focus returns to the hero opener.
4. The booking action retains CONSULT_BOOK_URL; the no-JavaScript href remains #packages in page HTML.
5. Existing header, mobile menu, hero imagery, and course/material links remain usable.

- [ ] **Step 3: Commit all release artifacts**

~~~powershell
git add site/build_portal.py tests/test_hero_60sec_diagnosis.py site/dist/index.html docs/superpowers/plans/2026-08-08-hero-60sec-diagnosis.md
git commit -m "feat: add hero 60-second diagnosis"
~~~

- [ ] **Step 4: Rebase safely onto the latest remote main and push**

~~~powershell
git fetch origin main
git rebase origin/main
git push origin HEAD:main
~~~

Expected: a fast-forward-compatible main update with no unrelated files. If a rebase conflict appears, stop, preserve the conflict details, and resolve only the diagnosis files before continuing.

- [ ] **Step 5: Wait for Vercel and verify production**

After the Git-connected deployment reports READY, inspect https://aiclimb.vercel.app/?v=hero60sec in a browser at 1440px and 390px and repeat the Step 2 checks. Confirm the live HTML contains 「迷ったら60秒診断をはじめる →」 and the real Square booking URL.

## Plan Self-Review

- **Spec coverage:** Task 2 covers hero copy, CTA order, direct booking, no-JavaScript fallback, and mobile layout. Task 3 covers plain-language questions, four results, real result actions, CTA de-duplication, keyboard closure, and focus restoration. Task 4 covers building, PC/iPhone validation, Git release, and Vercel production proof.
- **Placeholder scan:** Each task supplies exact filenames, copy, commands, expected behavior, and code shapes. No deferred implementation markers or unspecified links remain.
- **Interface consistency:** The diagnostic opener uses hero-diagnose-button diagnose-open throughout; results use start, promotion, office, and flow; every booking action uses CONSULT_BOOK_URL; every fallback/course action uses #packages.

## Execution Handoff

The user explicitly requested deployment through production, and the active collaboration policy does not permit unsolicited subagent delegation. Execute this plan inline with superpowers:executing-plans, stopping only for a genuine safety or production blocker.
