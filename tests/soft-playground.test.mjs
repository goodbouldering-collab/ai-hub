import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const projectRoot = fileURLToPath(new URL('../', import.meta.url));
const source = readFileSync(new URL('../site/static/design-system/studio/soft-playground.js', import.meta.url), 'utf8');

function element(dataset = {}, textContent = '') {
  const listeners = new Map();
  return {
    dataset, textContent, hidden: false, tabIndex: 0, focused: false,
    attributes: new Map(), listeners,
    setAttribute(name, value) { this.attributes.set(name, value); },
    addEventListener(name, fn) {
      if (!listeners.has(name)) listeners.set(name, []);
      listeners.get(name).push(fn);
    },
    emit(name, event = {}) { for (const fn of listeners.get(name) || []) fn(event); },
    focus() { this.focused = true; },
  };
}

function setup({ absent = false, incomplete = false } = {}) {
  const names = ['announce', 'office', 'website'];
  const tabs = names.map((name, i) => element({ spTab: name }, ['告知', '事務', 'サイト制作'][i]));
  const panels = names.map(name => {
    const panel = element({ spPanel: name });
    panel.examples = ['manual', 'ai'].map(mode => element({ spMode: mode }));
    panel.querySelectorAll = () => panel.examples;
    panel.querySelector = selector => panel.examples.find(example => selector.includes(`"${example.dataset.spMode}"`));
    return panel;
  });
  if (incomplete) panels[1].examples.pop();
  const modes = ['manual', 'ai'].map(value => Object.assign(element(), { value, checked: value === 'ai' }));
  const controls = element(); controls.hidden = true;
  const status = element();
  const root = element();
  root.querySelector = selector => selector === '[data-sp-controls]' ? controls : selector === '[data-sp-status]' ? status : null;
  root.querySelectorAll = selector => selector === '[data-sp-tab]' ? tabs : selector === '[data-sp-panel]' ? panels : modes;
  const context = { document: { getElementById: () => absent ? null : root } };
  const run = () => vm.runInNewContext(source, context);
  run();
  return { root, tabs, panels, modes, controls, status, run };
}

function assertSelected(page, scenario, mode) {
  assert.equal(page.panels.filter(panel => !panel.hidden).length, 1);
  for (const panel of page.panels) {
    assert.equal(panel.hidden, panel.dataset.spPanel !== scenario);
    assert.deepEqual(panel.examples.filter(example => !example.hidden).map(example => example.dataset.spMode), [mode]);
  }
  assert.equal(page.tabs.filter(tab => tab.tabIndex === 0).length, 1);
  for (const tab of page.tabs) {
    assert.equal(tab.attributes.get('aria-selected'), String(tab.dataset.spTab === scenario));
    assert.equal(tab.tabIndex, tab.dataset.spTab === scenario ? 0 : -1);
  }
  assert.equal(page.root.dataset.spMode, mode);
  assert.equal(page.modes.find(input => input.checked).value, mode);
}

test('progressive enhancement selects one example and wires accessible panels', () => {
  const page = setup();
  assertSelected(page, 'announce', 'ai');
  assert.equal(page.controls.hidden, false);
  assert.equal(page.root.dataset.softReady, 'true');
  assert.equal(page.status.textContent, '', 'No unsolicited announcement on load');
  page.panels.forEach(panel => {
    assert.equal(panel.attributes.get('role'), 'tabpanel');
    assert.equal(panel.attributes.get('aria-labelledby'), `studio-playground-tab-${panel.dataset.spPanel}`);
    assert.equal(panel.tabIndex, 0);
  });
});

test('touch/click and native radio changes cover all six workflow examples', () => {
  const page = setup();
  for (const tab of page.tabs) {
    tab.emit('click');
    for (const input of page.modes) {
      input.checked = true;
      input.emit('change');
      assertSelected(page, tab.dataset.spTab, input.value);
      assert.match(page.status.textContent, new RegExp(tab.textContent));
      assert.match(page.status.textContent, input.value === 'ai' ? /AIと進める/ : /手作業で進める/);
    }
  }
});

test('switching task keeps the chosen workflow and unchecked radio events do nothing', () => {
  const page = setup();
  page.modes[0].checked = true;
  page.modes[0].emit('change');
  page.tabs[2].emit('click');
  assertSelected(page, 'website', 'manual');
  page.modes[1].emit('change');
  assertSelected(page, 'website', 'manual');
});

test('arrow keys wrap, Home/End select and move focus, other keys keep native behavior', () => {
  const page = setup();
  let prevented = 0;
  const key = (index, value) => page.tabs[index].emit('keydown', { key: value, preventDefault() { prevented++; } });
  key(0, 'ArrowLeft');
  assertSelected(page, 'website', 'ai');
  assert.equal(page.tabs[2].focused, true);
  key(2, 'ArrowRight');
  assertSelected(page, 'announce', 'ai');
  key(0, 'End');
  assertSelected(page, 'website', 'ai');
  key(2, 'Home');
  assertSelected(page, 'announce', 'ai');
  key(0, 'Tab'); key(0, 'ArrowDown');
  assert.equal(prevented, 4);
  assertSelected(page, 'announce', 'ai');
});

test('repeated script evaluation does not reset state or duplicate handlers', () => {
  const page = setup();
  page.tabs[1].emit('click');
  page.run(); page.run();
  assertSelected(page, 'office', 'ai');
  assert.equal(page.tabs[1].listeners.get('click').length, 1);
  assert.equal(page.tabs[1].listeners.get('keydown').length, 1);
  assert.equal(page.modes[0].listeners.get('change').length, 1);
});

test('unrelated and incomplete pages stay readable without partially hidden content', () => {
  assert.doesNotThrow(() => setup({ absent: true }));
  const page = setup({ incomplete: true });
  assert.equal(page.controls.hidden, true);
  assert.equal(page.root.dataset.softReady, undefined);
  assert.equal(page.tabs.every(tab => tab.listeners.size === 0), true);
  assert.equal(page.panels.every(panel => !panel.hidden && panel.examples.every(example => !example.hidden)), true);
});

function python(program, input) {
  const result = spawnSync(process.env.PYTHON || 'python', ['-B', '-c', program], {
    cwd: projectRoot, input, encoding: 'utf8',
    env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONDONTWRITEBYTECODE: '1' },
  });
  assert.ifError(result.error);
  return result;
}

const fixture = '<!doctype html><html><head><title>AI相談</title></head><body><main><section id="ai-news"><p>既存のお知らせ</p><section><p>nested</p></section></section><div class="diagnosis-guide-row"><section><div>実力診断</div></section><section><div>サイト診断</div></section></div><section id="existing"><h2>既存の料金</h2><a href="/booking?plan=1&amp;people=2">相談する</a></section></main></body></html>';

test('decorator preserves existing HTML, inserts after both diagnoses, and is idempotent', () => {
  const result = python('import sys; from core.soft_studio import decorate_soft_playground; once=decorate_soft_playground(sys.stdin.read()); assert decorate_soft_playground(once)==once; sys.stdout.write(once)', fixture);
  assert.equal(result.status, 0, result.stderr);
  const html = result.stdout.replace(/\r\n/g, '\n');
  assert.match(html, /<div>サイト診断<\/div><\/section><\/div>\n<section id="studio-playground"/);
  assert.equal((html.match(/id="studio-playground"/g) || []).length, 1);
  assert.equal((html.match(/id="soft-playground-style"/g) || []).length, 1);
  assert.equal((html.match(/id="soft-playground-script"/g) || []).length, 1);
  assert.match(html, /<section id="existing"><h2>既存の料金<\/h2><a href="\/booking\?plan=1&amp;people=2">相談する<\/a><\/section>/);
  assert.match(html, /<div class="soft-playground__controls" data-sp-controls hidden>/);
  assert.equal((html.match(/data-sp-mode="(?:manual|ai)"/g) || []).length, 6);
  assert.doesNotMatch(html, /data-sp-(?:panel|mode)="[^"]*"[^>]*\bhidden/);
  assert.doesNotMatch(html, /<(?:form|iframe)\b/);
  assert.equal((html.match(/<button type="button" role="tab"/g) || []).length, 3);
  assert.match(html, /架空のサンプルです。ここではAIへの入力・送信・生成は行いません。/);
});

test('decorator fails closed when the homepage insertion anchor is missing', () => {
  const result = python('import sys; from core.soft_studio import decorate_soft_playground; decorate_soft_playground(sys.stdin.read())', '<html><head></head><body><p>既存ページ</p></body></html>');
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /requires the homepage diagnosis-guide-row/);
});

test('shared theme and playground keep stable tag order across repeated home decoration', () => {
  const ownedImages = '<figure id="restored-hero-image"><img src="/old-hero.webp" alt="old"></figure>'
    + Array.from({ length: 6 }, (_, index) => `<article class="compact-course-card"><img class="compact-course-visual" src="/course-${index}.webp" alt="old"><h3>講習${index}</h3></article>`).join('')
    + Array.from({ length: 3 }, (_, index) => `<img class="focus-step-visual" src="/step-${index}.webp" alt="old">`).join('');
  const input = fixture.replace('<main>', `<main>${ownedImages}`);
  const result = python('import sys; from core.studio_design import decorate_html; once=decorate_html(sys.stdin.read(), home=True); twice=decorate_html(once, home=True); assert twice==once, "Integrated home decoration changed on its second pass"; assert decorate_html(twice, home=True)==twice; sys.stdout.write(twice)', input);
  assert.equal(result.status, 0, result.stderr);
  const html = result.stdout;
  assert.ok(html.indexOf('id="studio-editorial"') < html.indexOf('id="soft-playground-style"'));
  for (const id of ['studio-design', 'studio-motion', 'studio-editorial', 'soft-playground-style', 'soft-playground-script', 'studio-playground']) {
    assert.equal((html.match(new RegExp(`id="${id}"`, 'g')) || []).length, 1, `${id} remains unique`);
  }
});
