import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const [app, css, renderer] = await Promise.all([
  readFile(new URL('../site/static/ai-agent-readiness/app.mjs', import.meta.url), 'utf8'),
  readFile(new URL('../site/static/ai-agent-readiness/styles.css', import.meta.url), 'utf8'),
  readFile(new URL('../site/ai_agent_readiness.py', import.meta.url), 'utf8'),
]);

test('assessment UI uses the tested scoring source and all core result actions', () => {
  assert.match(app, /from ['"]\.\/scoring\.mjs['"]/);
  assert.match(app, /QUESTIONS/);
  assert.match(app, /scoreAssessment/);
  assert.match(app, /clipboard/);
  assert.match(app, /window\.print/);
  assert.match(app, /restart-assessment/);
  assert.match(app, /assessment-progress/);
});

test('each question shows its practical learning criterion before the answer choices', () => {
  assert.match(renderer, /id='question-learning'/);
  assert.match(renderer, /この問いで身につく基準/);
  assert.match(app, /learningPoint/);
  assert.match(css, /question-learning/);
});

test('answers remain in memory and are not transmitted or persisted silently', () => {
  assert.doesNotMatch(app, /\blocalStorage\b/);
  assert.doesNotMatch(app, /\bsessionStorage\b/);
  assert.doesNotMatch(app, /\bfetch\s*\(/);
  assert.doesNotMatch(app, /sendBeacon/);
});

test('YouTube loads only after consent and only with a validated video id', () => {
  assert.match(app, /youtube-nocookie\.com\/embed\//);
  assert.match(app, /\{11\}/);
  assert.match(app, /data-video-consent/);
  assert.doesNotMatch(renderer, /i\.ytimg\.com/);
  assert.doesNotMatch(renderer, /<iframe/);
  assert.match(app, /iframe\.focus\(\)/);
  assert.match(app, /動画を読み込みました/);
});

test('a safety shortfall is displayed even when the numeric level is not capped', () => {
  assert.match(app, /requirementsMet/);
  assert.match(app, /安全基準を先に整えましょう/);
});

test('the result explains how an equal lowest score was prioritized', () => {
  assert.match(app, /selectionNote/);
});

test('styles cover keyboard focus, mobile, reduced motion, printing, and overflow', () => {
  assert.match(css, /:focus-visible/);
  assert.match(css, /@media\s*\([^)]*max-width/);
  assert.match(css, /prefers-reduced-motion:\s*reduce/);
  assert.match(css, /@media\s+print/);
  assert.match(css, /overflow-wrap/);
  assert.match(css, /min-width:\s*0/);
});
