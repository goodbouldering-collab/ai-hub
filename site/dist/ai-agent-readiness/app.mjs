import { QUESTIONS, scoreAssessment } from './scoring.mjs';

const byId = (id) => document.getElementById(id);

const elements = {
  intro: byId('assessment-intro'),
  start: byId('start-assessment'),
  form: byId('assessment-form'),
  progressLabel: byId('progress-label'),
  progress: byId('assessment-progress'),
  status: byId('assessment-status'),
  fieldset: byId('question-fieldset'),
  questionNumber: byId('question-number'),
  questionPrompt: byId('question-prompt'),
  questionContext: byId('question-context'),
  questionLearning: byId('question-learning-text'),
  options: byId('answer-options'),
  previous: byId('previous-question'),
  next: byId('next-question'),
  resultPanel: byId('result-panel'),
  resultHeading: byId('result-heading'),
  resultScore: byId('result-score'),
  resultLevel: byId('result-level'),
  resultSummary: byId('result-summary'),
  safetyGate: byId('safety-gate'),
  dimensionScores: byId('dimension-scores'),
  futureScores: byId('future-scores'),
  nextSteps: byId('next-steps'),
  course: byId('course-recommendation'),
  copy: byId('copy-result'),
  print: byId('print-result'),
  restart: byId('restart-assessment'),
  copyStatus: byId('copy-status'),
};

let currentIndex = 0;
let answers = Object.create(null);
let latestResult = null;

function itemName(item) {
  return item?.nameJa ?? item?.name ?? item?.label ?? '';
}

function itemPercent(item) {
  const value = Number(item?.percent ?? item?.percentage ?? item?.score ?? 0);
  return Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0));
}

function setStatus(message, visible = false) {
  if (!elements.status) return;
  elements.status.textContent = message;
  elements.status.classList.toggle('is-visible', visible);
}

function focusQuestion() {
  if (!elements.fieldset) return;
  elements.fieldset.tabIndex = -1;
  elements.fieldset.focus({ preventScroll: false });
}

function makeAnswerOption(question, option, optionIndex) {
  const label = document.createElement('label');
  label.className = 'answer-option';

  const input = document.createElement('input');
  input.type = 'radio';
  input.name = 'readiness-answer';
  input.id = `answer-${question.id}-${optionIndex}`;
  input.value = String(option.value);
  input.checked = Number(answers[question.id]) === Number(option.value);

  const marker = document.createElement('span');
  marker.className = 'answer-option__marker';
  marker.setAttribute('aria-hidden', 'true');
  marker.textContent = String(option.value);

  const copy = document.createElement('span');
  copy.className = 'answer-option__copy';
  copy.textContent = option.label;

  input.addEventListener('change', () => {
    answers[question.id] = Number(option.value);
    elements.fieldset?.removeAttribute('aria-invalid');
    setStatus(`質問 ${currentIndex + 1} に回答しました。`, false);
    updateProgress();
  });

  label.append(input, marker, copy);
  return label;
}

function updateProgress() {
  const answeredCount = Object.keys(answers).length;
  if (elements.progressLabel) {
    elements.progressLabel.textContent = `質問 ${currentIndex + 1} / ${QUESTIONS.length} ・ 回答済み ${answeredCount}`;
  }
  if (elements.progress) {
    elements.progress.max = QUESTIONS.length;
    elements.progress.value = answeredCount;
    elements.progress.textContent = `${answeredCount} / ${QUESTIONS.length}`;
    elements.progress.setAttribute('aria-label', `${QUESTIONS.length}問中${answeredCount}問回答済み`);
  }
}

function renderQuestion({ focus = true } = {}) {
  const question = QUESTIONS[currentIndex];
  if (!question || !elements.options) return;

  setStatus('', false);
  elements.fieldset?.removeAttribute('aria-invalid');
  elements.questionNumber.textContent = `Question ${String(currentIndex + 1).padStart(2, '0')}`;
  elements.questionPrompt.textContent = question.prompt ?? question.title ?? '';
  elements.questionContext.textContent = question.context ?? question.scenario ?? '';
  elements.questionLearning.textContent = question.learningPoint ?? 'AIを仕事で続けるために、目的・確認・安全・記録を一つずつ整えます。';
  elements.options.replaceChildren(
    ...(question.options ?? []).map((option, optionIndex) => makeAnswerOption(question, option, optionIndex)),
  );

  elements.previous.disabled = currentIndex === 0;
  elements.next.textContent = currentIndex === QUESTIONS.length - 1 ? '結果を見る' : '次へ';
  updateProgress();
  if (focus) focusQuestion();
}

function startAssessment() {
  elements.intro.hidden = true;
  elements.resultPanel.hidden = true;
  elements.form.hidden = false;
  currentIndex = 0;
  renderQuestion();
}

function renderScoreList(container, scores, className) {
  if (!container) return;
  const fragment = document.createDocumentFragment();

  for (const item of scores ?? []) {
    const percent = itemPercent(item);
    const row = document.createElement('div');
    row.className = `score-row ${className}`;

    const heading = document.createElement('div');
    heading.className = 'score-row__heading';
    const label = document.createElement('span');
    label.textContent = itemName(item);
    const value = document.createElement('strong');
    value.textContent = `${Math.round(percent)}%`;
    heading.append(label, value);

    const meter = document.createElement('div');
    meter.className = 'score-meter';
    meter.setAttribute('role', 'progressbar');
    meter.setAttribute('aria-label', itemName(item));
    meter.setAttribute('aria-valuemin', '0');
    meter.setAttribute('aria-valuemax', '100');
    meter.setAttribute('aria-valuenow', String(Math.round(percent)));
    const fill = document.createElement('span');
    fill.style.setProperty('--score-percent', `${percent}%`);
    meter.append(fill);

    row.append(heading, meter);
    fragment.append(row);
  }

  container.replaceChildren(fragment);
}

function renderGate(result) {
  const gate = result?.gate ?? {};
  const applied = Boolean(gate.applied ?? gate.isApplied);
  const requirementsMet = gate.requirementsMet
    ?? !(Array.isArray(gate.reasons) && gate.reasons.length > 0);
  const unrestricted = result?.unrestrictedLevel ?? result?.rawLevel;
  const finalLevel = result?.level;
  const heading = document.createElement('strong');
  const detail = document.createElement('p');

  elements.safetyGate.classList.toggle('safety-gate--applied', !requirementsMet);
  elements.safetyGate.classList.toggle('safety-gate--clear', requirementsMet);

  if (applied) {
    heading.textContent = `安全ゲート：Level ${unrestricted?.id ?? '—'} から Level ${finalLevel?.id ?? '—'} に調整`;
    detail.textContent = gate.message
      ?? (Array.isArray(gate.reasons) ? gate.reasons.join(' ') : '')
      ?? '検証・安全・運用を整えてから、自動化の範囲を広げましょう。';
  } else if (!requirementsMet) {
    heading.textContent = '安全基準を先に整えましょう（今回のLevel変更はありません）';
    detail.textContent = gate.message
      || (Array.isArray(gate.reasons) ? gate.reasons.join(' ') : '')
      || '検証・安全・運用を整えてから、自動化の範囲を広げましょう。';
  } else {
    heading.textContent = '安全ゲート：今回のレベル調整はありません';
    detail.textContent = '得点が高くても、確認・権限・停止手順は毎回必要です。安全に任せる力を継続して磨きましょう。';
  }

  elements.safetyGate.replaceChildren(heading, detail);
}

function renderNextSteps(result) {
  const target = result?.next90DayTarget ?? result?.ninetyDayTarget ?? {};
  const priority = target.dimensionName ?? itemName(result?.lowestDimension) ?? '優先領域';
  const title = document.createElement('p');
  title.className = 'next-steps__focus';
  title.textContent = target.title ?? target.label ?? `${priority}を一段上げる`;
  const selectionNote = document.createElement('p');
  selectionNote.className = 'next-steps__selection';
  selectionNote.textContent = target.selectionNote ?? '';

  const list = document.createElement('ol');
  const action = document.createElement('li');
  action.innerHTML = '<strong>まず実行</strong>';
  action.append(document.createTextNode(target.action ?? target.steps?.[0] ?? '小さな業務を一つ選び、AIを使う範囲と人が確認する点を決める。'));
  const measure = document.createElement('li');
  measure.innerHTML = '<strong>できた証拠</strong>';
  measure.append(document.createTextNode(target.measure ?? target.steps?.[1] ?? '時間と品質の変化を記録し、第三者と確認する。'));
  list.append(action, measure);

  elements.nextSteps.replaceChildren(...[title, selectionNote, list].filter((node) => node.textContent));
}

function renderCourse(result) {
  const course = result?.course ?? result?.recommendedCourse;
  if (!course) {
    elements.course.replaceChildren();
    return;
  }

  const copy = document.createElement('div');
  const eyebrow = document.createElement('p');
  eyebrow.className = 'eyebrow';
  eyebrow.textContent = 'OPTIONAL SUPPORT FROM AI相談';
  const title = document.createElement('h3');
  title.textContent = course.title ?? course.name ?? 'おすすめの学び';
  const meta = document.createElement('p');
  meta.className = 'course-recommendation__meta';
  meta.textContent = [course.duration, course.price].filter(Boolean).join(' ・ ');
  const description = document.createElement('p');
  description.textContent = course.description ?? course.summary ?? '';
  const disclosure = document.createElement('p');
  disclosure.className = 'course-recommendation__disclosure';
  disclosure.textContent = 'AI相談が提供する自社サービスです。これは弱点別の個別処方ではなく、レベル別の標準案です。購入は任意で、上の90日行動は無料でも実践できます。点数だけで受講の必要性を判断するものではありません。';
  copy.append(eyebrow, title, meta, description, disclosure);

  const link = document.createElement('a');
  link.className = 'button button--course';
  const courseUrl = course.url ?? '/#packages';
  link.href = courseUrl;
  link.textContent = course.cta ?? '詳しく見る';
  if (/^https?:\/\//i.test(courseUrl)) {
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  }

  elements.course.replaceChildren(copy, link);
}

function renderResult(result) {
  const level = result.level ?? {};
  const rawScore = Number(result.rawScore ?? result.score ?? 0);
  elements.resultScore.textContent = String(Math.max(0, Math.min(100, rawScore)));
  elements.resultLevel.textContent = `Level ${level.id ?? '—'} · ${level.nameEn ?? level.label ?? ''} / ${level.nameJa ?? level.name ?? ''}`;
  elements.resultSummary.textContent = level.description ?? level.summary ?? '';
  renderGate(result);
  renderScoreList(elements.dimensionScores, result.dimensionScores ?? result.dimensions, 'score-row--dimension');
  renderScoreList(elements.futureScores, result.futureScores ?? result.futureIndicators, 'score-row--future');
  renderNextSteps(result);
  renderCourse(result);

  elements.form.hidden = true;
  elements.resultPanel.hidden = false;
  elements.copyStatus.textContent = '';
  elements.resultHeading.tabIndex = -1;
  elements.resultHeading.focus({ preventScroll: false });
}

function showMissingAnswer() {
  elements.fieldset?.setAttribute('aria-invalid', 'true');
  setStatus('この質問の回答を選んでから進んでください。', true);
  elements.options?.querySelector('input')?.focus();
}

function goNext() {
  const question = QUESTIONS[currentIndex];
  if (answers[question.id] == null) {
    showMissingAnswer();
    return;
  }

  if (currentIndex < QUESTIONS.length - 1) {
    currentIndex += 1;
    renderQuestion();
    return;
  }

  const result = scoreAssessment(answers);
  if (!result?.complete) {
    const firstMissingId = result?.missingQuestionIds?.[0];
    const missingIndex = QUESTIONS.findIndex((item) => item.id === firstMissingId);
    if (missingIndex >= 0) currentIndex = missingIndex;
    renderQuestion();
    showMissingAnswer();
    return;
  }

  latestResult = result;
  renderResult(result);
}

function goPrevious() {
  if (currentIndex === 0) return;
  currentIndex -= 1;
  renderQuestion();
}

function consultationMemo() {
  return latestResult?.consultationMemo
    ?? latestResult?.consultationData?.text
    ?? `AI Agent Readiness Compass\n現在地: ${latestResult?.rawScore ?? 0}点`;
}

function legacyCopy(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', '');
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.append(textarea);
  textarea.select();
  const copied = document.execCommand?.('copy') ?? false;
  textarea.remove();
  if (!copied) throw new Error('copy failed');
}

async function copyResult() {
  try {
    const text = consultationMemo();
    if (navigator.clipboard?.writeText && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      legacyCopy(text);
    }
    elements.copyStatus.textContent = '相談メモをコピーしました。AI相談やご自身の学習記録に貼り付けられます。';
  } catch {
    elements.copyStatus.textContent = '自動コピーできませんでした。印刷機能から保存するか、画面の結果を選択してコピーしてください。';
  }
}

function restartAssessment() {
  answers = Object.create(null);
  latestResult = null;
  currentIndex = 0;
  elements.resultPanel.hidden = true;
  elements.form.hidden = false;
  elements.copyStatus.textContent = '';
  renderQuestion();
}

function loadVideo(button) {
  const videoId = button.dataset.videoId ?? '';
  if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return;
  const card = button.closest('.video-card');
  const slot = card?.querySelector('.video-player-slot');
  if (!slot) return;

  const iframe = document.createElement('iframe');
  iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`;
  iframe.title = `${card.querySelector('h3')?.textContent ?? 'YouTube動画'}を再生`;
  iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
  iframe.referrerPolicy = 'strict-origin-when-cross-origin';
  iframe.allowFullscreen = true;
  iframe.loading = 'lazy';
  slot.replaceChildren(iframe);
  button.hidden = true;
  slot.setAttribute('aria-label', '動画を読み込みました');
  iframe.focus();
}

function bindEvents() {
  elements.start?.addEventListener('click', startAssessment);
  elements.previous?.addEventListener('click', goPrevious);
  elements.next?.addEventListener('click', goNext);
  elements.form?.addEventListener('submit', (event) => {
    event.preventDefault();
    goNext();
  });
  elements.copy?.addEventListener('click', copyResult);
  elements.print?.addEventListener('click', () => window.print());
  elements.restart?.addEventListener('click', restartAssessment);
  document.querySelectorAll('[data-video-consent][data-video-id]').forEach((button) => {
    button.addEventListener('click', () => loadVideo(button), { once: true });
  });
}

if (QUESTIONS.length > 0 && elements.form && elements.resultPanel) {
  bindEvents();
}
