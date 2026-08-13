import test from 'node:test';
import assert from 'node:assert/strict';

import {
  COURSE_ROUTES,
  DIMENSIONS,
  FUTURE_INDICATORS,
  LEVELS,
  QUESTIONS,
  levelForScore,
  scoreAssessment,
} from '../site/static/ai-agent-readiness/scoring.mjs';

const answersAt = (score) => Object.fromEntries(QUESTIONS.map((question) => [question.id, score]));

test('the schema contains 20 evidence-based questions worth exactly 100 points', () => {
  assert.equal(QUESTIONS.length, 20);
  assert.equal(new Set(QUESTIONS.map(({ id }) => id)).size, 20);
  assert.equal(DIMENSIONS.length, 8);
  assert.equal(FUTURE_INDICATORS.length, 5);
  assert.equal(LEVELS.length, 5);

  const coveredIds = DIMENSIONS.flatMap(({ questionIds }) => questionIds);
  assert.deepEqual([...coveredIds].sort(), QUESTIONS.map(({ id }) => id).sort());
  assert.equal(new Set(coveredIds).size, 20);

  for (const question of QUESTIONS) {
    assert.equal(question.options.length, 4, question.id);
    assert.deepEqual(question.options.map(({ value }) => value), [0, 2, 4, 5], question.id);
    assert.ok(question.options.every(({ label }) => label.length >= 8), question.id);
  }
});

test('score boundaries map to five transparent readiness levels', () => {
  assert.equal(levelForScore(0).id, 1);
  assert.equal(levelForScore(24).id, 1);
  assert.equal(levelForScore(25).id, 2);
  assert.equal(levelForScore(44).id, 2);
  assert.equal(levelForScore(45).id, 3);
  assert.equal(levelForScore(64).id, 3);
  assert.equal(levelForScore(65).id, 4);
  assert.equal(levelForScore(84).id, 4);
  assert.equal(levelForScore(85).id, 5);
  assert.equal(levelForScore(100).id, 5);
  assert.equal(LEVELS[1].nameEn, 'Guided AI User');
  assert.equal(FUTURE_INDICATORS.find(({ id }) => id === 'multimodalTooling').nameEn, 'Tool-using Agent & Multimodal');
});

test('all-zero and all-five answers produce valid 0 and 100 point results', () => {
  const minimum = scoreAssessment(answersAt(0));
  assert.equal(minimum.complete, true);
  assert.equal(minimum.rawScore, 0);
  assert.equal(minimum.level.id, 1);
  assert.equal(minimum.course.id, 'ai-consult-entry');
  assert.equal(minimum.gate.applied, false);
  assert.equal(minimum.gate.requirementsMet, false);
  assert.match(minimum.gate.message, /検証|安全/);

  const maximum = scoreAssessment(answersAt(5));
  assert.equal(maximum.complete, true);
  assert.equal(maximum.rawScore, 100);
  assert.equal(maximum.level.id, 5);
  assert.equal(maximum.course.id, 'ai-support');
  assert.equal(maximum.dimensionScores.length, 8);
  assert.ok(maximum.dimensionScores.every(({ percent }) => percent === 100));
  assert.equal(maximum.futureScores.length, 5);
  assert.ok(maximum.futureScores.every(({ percent }) => percent === 100));
  assert.equal(maximum.gate.applied, false);
  assert.equal(maximum.gate.requirementsMet, true);
  assert.equal(maximum.next90DayTarget.dimensionId, 'capstone');
  assert.match(maximum.next90DayTarget.title, /維持|証明/);
  assert.doesNotMatch(maximum.next90DayTarget.title, /一段上げる/);
  assert.match(maximum.consultationMemo, /案内（任意）/);
  assert.doesNotMatch(maximum.consultationMemo, /推奨:/);
});

test('verification or safety gaps cap the level without hiding the raw score', () => {
  const answers = answersAt(5);
  for (const id of ['Q10', 'Q11', 'Q12', 'Q13', 'Q14']) answers[id] = 0;

  const result = scoreAssessment(answers);
  assert.equal(result.rawScore, 75);
  assert.equal(result.unrestrictedLevel.id, 4);
  assert.equal(result.level.id, 3);
  assert.equal(result.gate.applied, true);
  assert.equal(result.gate.maxLevel, 3);
  assert.match(result.gate.message, /検証|安全/);
});

test('weak build and recovery practice prevents an orchestrator result', () => {
  const answers = answersAt(5);
  answers.Q17 = 2;
  answers.Q18 = 2;

  const result = scoreAssessment(answers);
  assert.equal(result.rawScore, 94);
  assert.equal(result.unrestrictedLevel.id, 5);
  assert.equal(result.level.id, 4);
  assert.equal(result.gate.maxLevel, 4);
});

test('an orchestrator result requires every readiness dimension to reach 60 percent', () => {
  const answers = answersAt(5);
  answers.Q15 = 0;
  answers.Q16 = 0;

  const result = scoreAssessment(answers);
  assert.equal(result.rawScore, 90);
  assert.equal(result.unrestrictedLevel.id, 5);
  assert.equal(result.level.id, 4);
  assert.equal(result.gate.maxLevel, 4);
  assert.match(result.gate.message, /全8領域|60%/);
});

test('top evidence can come from a safe exercise and does not require a real incident', () => {
  const topLabels = QUESTIONS.map(({ options }) => options.at(-1).label).join('\n');
  assert.doesNotMatch(topLabels, /事故寸前|事故に応じ|障害から復旧した経験/);
  assert.match(topLabels, /演習|レビュー/);
});

test('equal lowest dimensions disclose the deterministic learning priority', () => {
  const result = scoreAssessment(answersAt(2));
  assert.equal(result.lowestDimensions.length, 8);
  assert.match(result.next90DayTarget.selectionNote, /同率/);
  assert.match(result.next90DayTarget.selectionNote, /人間中心/);
});

test('incomplete answers are reported and never receive a level', () => {
  const result = scoreAssessment({ Q01: 5 });
  assert.equal(result.complete, false);
  assert.equal(result.answeredCount, 1);
  assert.equal(result.missingQuestionIds.length, 19);
  assert.equal(result.level, null);
});

test('course routes match live AI consultation offers and avoid direct high-price checkout', () => {
  assert.equal(
    COURSE_ROUTES['ai-consult-entry'].url,
    'https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE',
  );
  assert.equal(COURSE_ROUTES['ai-agent-course'].url, 'https://goodbouldering.com/?pid=188553378');
  assert.equal(
    COURSE_ROUTES['ai-coding'].url,
    'https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH',
  );
  assert.equal(COURSE_ROUTES['ai-support'].url, '/#packages');
  assert.notEqual(COURSE_ROUTES['ai-support'].url, '/api/stripe/monthly-support');
});
