import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {test} from 'node:test';

const home = readFileSync(new URL('../cloudflare-runtime/public/index.html', import.meta.url), 'utf8');
const start = home.indexOf("var modal = document.getElementById('diagnoseModal');");
const source = home.slice(start, home.indexOf('})();', start));

function fixture() {
  const events = {}, modalEvents = {}, classes = new Set();
  const body = {innerHTML: ''};
  let focus = '';
  const trigger = {focus: () => {focus = 'trigger';}};
  const close = {focus: () => {focus = 'close';}};
  const modal = {
    querySelector: selector => selector === '.diagnose-body' ? body : close,
    classList: {add: c => classes.add(c), remove: c => classes.delete(c), contains: c => classes.has(c)},
    addEventListener: (name, fn) => {modalEvents[name] = fn;},
  };
  const document = {getElementById: () => modal, activeElement: trigger, contains: () => true,
    addEventListener: (name, fn) => {events[name] = fn;}};
  vm.runInNewContext('(function(){' + source + '})();', {document});
  return {body, classes, get focus() {return focus;},
    open: () => events.click({preventDefault() {}, target: {closest: s => s === '.diagnose-open' ? trigger : null}}),
    answer: key => modalEvents.click({target: {closest: s => s === '.diag-opt' ? {getAttribute: () => key} : null}}),
    click: selector => modalEvents.click({target: {closest: s => s === selector ? {} : null}}),
    escape: () => events.keydown({key: 'Escape'}),
  };
}

test('hero entry opens the original menu flow in the requested position', () => {
  const hero = home.match(/<div class='hero-diagnose-cta'>.*?<\/small><\/div>/s)?.[0];
  assert.match(hero, /<button type='button' class='focus-btn primary diagnose-open' aria-haspopup='dialog' aria-controls='diagnoseModal'>メニュー選択フロー<\/button>/);
  assert.doesNotMatch(hero, /href='#contact'/);
  const f = fixture(); f.open();
  assert.ok(f.classes.has('open'));
  assert.match(f.body.innerHTML, /STEP 1 \/ 3/);
  assert.equal(f.focus, 'close');
});

test('all 64 combinations finish with a working destination and course link', () => {
  for (const first of ['start', 'promotion', 'office', 'flow'])
    for (const second of ['start', 'promotion', 'office', 'flow'])
      for (const final of ['free', 'promotion', 'start', 'flow']) {
        const f = fixture(); f.open();
        f.answer(first); f.answer(second); f.answer(final);
        assert.match(f.body.innerHTML, /class="diag-result"/);
        assert.match(f.body.innerHTML, /href="https:\/\/(book.squareup.com|goodbouldering.com)\//);
        assert.match(f.body.innerHTML, /href="#packages"/);
        assert.doesNotMatch(f.body.innerHTML, /undefined/);
      }
});

test('restart, Escape, close button, and reopen preserve usable state', () => {
  const f = fixture(); f.open(); f.answer('start');
  f.escape(); assert.ok(!f.classes.has('open')); assert.equal(f.focus, 'trigger');
  f.open(); assert.match(f.body.innerHTML, /STEP 1 \/ 3/);
  f.answer('start'); f.answer('start'); f.answer('free');
  f.click('.diag-restart'); assert.match(f.body.innerHTML, /STEP 1 \/ 3/);
  f.click('.diagnose-close'); assert.ok(!f.classes.has('open'));
});
