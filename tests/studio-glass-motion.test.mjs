import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../site/static/design-system/studio/studio.js', import.meta.url), 'utf8');

function events() {
  const listeners = new Map();
  return {
    addEventListener(name, listener) {
      if (!listeners.has(name)) listeners.set(name, []);
      listeners.get(name).push(listener);
    },
    emit(name, event = {}) { for (const listener of listeners.get(name) || []) listener(event); },
    listeners,
  };
}

function setup({ theme = true, fine = true, reduced = false, stack = true } = {}) {
  const styles = new Map(), attributes = new Map(), frames = new Map();
  let nextFrame = 1, rectReads = 0, queries = 0;
  const element = {
    ...events(),
    classList: { contains: name => stack && name === 'studio-art-stack' },
    style: { setProperty: (name, value) => styles.set(name, value), removeProperty: name => styles.delete(name) },
    setAttribute: (name, value) => attributes.set(name, value),
    getBoundingClientRect() { rectReads++; return { left: 10, top: 20, width: 200, height: 100 }; },
  };
  const reducedMedia = { ...events(), matches: reduced };
  const fineMedia = { ...events(), matches: fine };
  const document = {
    ...events(), hidden: false,
    // An article has studio-theme but deliberately does not have studio-home.
    body: { classList: { contains: name => theme && name === 'studio-theme' } },
    querySelector() { queries++; return null; },
    querySelectorAll(selector) { queries++; return selector.startsWith('.studio-art-stack,') ? [element] : []; },
  };
  vm.runInNewContext(source, {
    document, window: {},
    matchMedia: query => query.includes('reduced-motion') ? reducedMedia : fineMedia,
    requestAnimationFrame(callback) { const id = nextFrame++; frames.set(id, callback); return id; },
    cancelAnimationFrame: id => frames.delete(id),
  });
  return {
    element, document, styles, attributes, frames, reducedMedia, fineMedia,
    get rectReads() { return rectReads; }, get queries() { return queries; },
    move(x = 110, y = 70, pointerType = 'mouse') { element.emit('pointermove', { clientX: x, clientY: y, pointerType }); },
    flush() { const pending = [...frames.values()]; frames.clear(); pending.forEach(callback => callback()); },
  };
}

test('non-theme pages receive no DOM queries, attributes or event handlers', () => {
  const page = setup({ theme: false });
  assert.equal(page.queries, 0);
  assert.equal(page.attributes.size, 0);
  assert.equal(page.element.listeners.size, 0);
  assert.equal(page.frames.size, 0);
});

test('article pages activate glass motion and batch mouse movement using the latest point', () => {
  const page = setup();
  assert.equal(page.attributes.get('data-studio-glass'), '');
  page.move(20, 30); page.move(160, 45); page.move(210, 120);
  assert.equal(page.frames.size, 1);
  assert.equal(page.rectReads, 0);
  page.flush();
  assert.equal(page.rectReads, 1);
  assert.equal(page.styles.get('--glass-x'), '100%');
  assert.equal(page.styles.get('--glass-y'), '100%');
  assert.equal(page.styles.get('--art-x'), '6px');
  assert.equal(page.styles.get('--art-y'), '6px');
  assert.equal(page.frames.size, 0, 'No idle animation loop');
});

test('coordinates clamp to bounds and ordinary cards never get collage displacement', () => {
  const page = setup({ stack: false });
  page.move(-100, 900); page.flush();
  assert.equal(page.styles.get('--glass-x'), '0%');
  assert.equal(page.styles.get('--glass-y'), '100%');
  assert.equal(page.styles.has('--art-x'), false);
  assert.equal(page.styles.has('--art-y'), false);
});

for (const [label, options, pointerType] of [
  ['coarse pointer', { fine: false }, 'mouse'],
  ['reduced motion', { reduced: true }, 'mouse'],
  ['touch event', {}, 'touch'],
  ['pen event', {}, 'pen'],
]) {
  test(`${label} never schedules pointer animation`, () => {
    const page = setup(options);
    page.move(110, 70, pointerType);
    assert.equal(page.frames.size, 0);
    assert.equal(page.styles.size, 0);
    assert.equal(page.rectReads, 0);
  });
}

for (const resetEvent of ['pointerleave', 'visibilitychange', 'reduced-change', 'fine-change']) {
  test(`${resetEvent} clears displacement and cancels queued motion`, () => {
    const page = setup();
    page.move(210, 120); page.flush();
    assert.equal(page.styles.size, 4);
    page.move(10, 20);
    assert.equal(page.frames.size, 1);
    if (resetEvent === 'pointerleave') page.element.emit('pointerleave');
    if (resetEvent === 'visibilitychange') {
      page.document.hidden = true;
      page.document.emit('visibilitychange');
    }
    if (resetEvent === 'reduced-change') {
      page.reducedMedia.matches = true;
      page.reducedMedia.emit('change', { matches: true });
    }
    if (resetEvent === 'fine-change') {
      page.fineMedia.matches = false;
      page.fineMedia.emit('change', { matches: false });
    }
    assert.equal(page.frames.size, 0);
    assert.equal(page.styles.size, 0);
    page.flush();
    assert.equal(page.styles.size, 0);
    if (resetEvent !== 'pointerleave') {
      page.move();
      assert.equal(page.frames.size, 0);
    }
  });
}
