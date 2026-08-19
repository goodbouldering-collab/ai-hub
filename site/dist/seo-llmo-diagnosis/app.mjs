const root = document.querySelector('main[data-audit-endpoint]');
const form = document.getElementById('seo-audit-form');
const status = document.getElementById('audit-form-status');
const submit = document.getElementById('run-audit');
const results = document.getElementById('audit-results');
const codexButton = document.getElementById('run-codex-diagnosis');
const codexStatus = document.getElementById('codex-diagnosis-status');
const codexResult = document.getElementById('codex-diagnosis-result');

let latestReport = null;

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;');

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { accept: 'application/json', ...(options.headers || {}) } });
  let payload = {};
  try { payload = await response.json(); } catch {}
  if (!response.ok) {
    const error = new Error(payload.message || payload.error || `通信に失敗しました（${response.status}）`);
    error.status = response.status;
    error.code = payload.error || '';
    throw error;
  }
  return payload;
}

function setBusy(busy) {
  submit.disabled = busy;
  submit.setAttribute('aria-busy', String(busy));
  submit.querySelector('span').textContent = busy ? '公開ページを確認しています…' : '無料で診断する';
}

function categoryMarkup(category) {
  const percent = Math.round((category.score / category.maxScore) * 100);
  return `<article class="audit-category">
    <div><span>${escapeHtml(category.name)}</span><strong>${category.score}<small> / ${category.maxScore}</small></strong></div>
    <div class="audit-meter" role="meter" aria-label="${escapeHtml(category.name)}" aria-valuemin="0" aria-valuemax="${category.maxScore}" aria-valuenow="${category.score}"><i style="width:${percent}%"></i></div>
    <p>${category.passed} / ${category.total}項目を確認</p>
  </article>`;
}

function priorityMarkup(priority, index) {
  const labels = { high: '最優先', medium: '次に改善', low: '余力があれば' };
  return `<article class="audit-priority audit-priority--${escapeHtml(priority.priority)}">
    <div class="audit-priority__number">${String(index + 1).padStart(2, '0')}</div>
    <div><p><span>${escapeHtml(labels[priority.priority] || '改善')}</span>${escapeHtml(priority.evidence)}</p>
    <h4>${escapeHtml(priority.title)}</h4><p>${escapeHtml(priority.reason)}</p><div class="audit-priority__action"><b>次の一手</b><span>${escapeHtml(priority.action)}</span></div></div>
  </article>`;
}

function checkMarkup(item) {
  return `<li class="${item.passed ? 'is-pass' : 'is-missing'}"><span aria-hidden="true">${item.passed ? '✓' : '!'}</span><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(item.evidence)}</small></div></li>`;
}

function renderReport(report) {
  latestReport = report;
  document.getElementById('audit-score').textContent = report.score;
  document.getElementById('audit-score-ring').style.setProperty('--score', `${report.score * 3.6}deg`);
  document.getElementById('audit-level').textContent = report.level.label;
  document.getElementById('audit-result-summary').textContent = report.page.title
    ? `「${report.page.title}」を、公開HTML・robots.txt・sitemap.xmlから確認しました。`
    : '公開HTML・robots.txt・sitemap.xmlから確認できる範囲を整理しました。';
  document.getElementById('audit-categories').innerHTML = report.categories.map(categoryMarkup).join('');
  document.getElementById('audit-priority-list').innerHTML = report.priorities.length
    ? report.priorities.map(priorityMarkup).join('')
    : '<p class="audit-all-clear">主要な準備項目を確認できました。Search Console、実際の問い合わせ、競合との差を次に確認してください。</p>';
  document.getElementById('audit-check-list').innerHTML = `<ul>${report.checks.map(checkMarkup).join('')}</ul>`;
  results.hidden = false;
  codexResult.hidden = true;
  codexResult.innerHTML = '';
  codexStatus.textContent = '';
  results.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  document.getElementById('audit-result-title').focus({ preventScroll: true });
}

function resultText(report) {
  const lines = [
    'SEO・LLMO診断',
    `対象: ${report.auditedUrl}`,
    `準備度: ${report.score}/100（${report.level.label}）`,
    '',
    '4領域:',
    ...report.categories.map((category) => `- ${category.name}: ${category.score}/${category.maxScore}`),
    '',
    '優先して直すこと:',
    ...(report.priorities.length ? report.priorities.slice(0, 3).map((item, index) => `${index + 1}. ${item.title}\n   ${item.action}`) : ['- 主要項目は確認済み。実データと競合を確認する']),
    '',
    report.disclaimer,
  ];
  return lines.join('\n');
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  const payload = {
    url: String(data.get('url') || '').trim(),
    context: {
      audience: String(data.get('audience') || '').trim(),
      problem: String(data.get('problem') || '').trim(),
      desiredAction: String(data.get('desiredAction') || '').trim(),
      isLocalBusiness: data.get('isLocalBusiness') === 'true',
    },
  };
  setBusy(true);
  status.classList.remove('is-error');
  status.textContent = '公開HTML、robots.txt、sitemap.xmlを確認しています。';
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 28_000);
    const response = await fetchJson(root.dataset.auditEndpoint, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    }).finally(() => clearTimeout(timer));
    status.textContent = '診断できました。優先順位を確認してください。';
    renderReport(response.report);
  } catch (error) {
    status.classList.add('is-error');
    status.textContent = error.name === 'AbortError'
      ? '診断に時間がかかっています。URLを確認して、もう一度お試しください。'
      : error.message;
  } finally {
    setBusy(false);
  }
});

document.getElementById('copy-audit-result')?.addEventListener('click', async () => {
  const copyStatus = document.getElementById('audit-copy-status');
  if (!latestReport) return;
  try {
    await navigator.clipboard.writeText(resultText(latestReport));
    copyStatus.textContent = '結果をコピーしました。相談や改善メモに貼り付けられます。';
  } catch {
    copyStatus.textContent = 'コピーできませんでした。印刷をご利用ください。';
  }
});

document.getElementById('print-audit-result')?.addEventListener('click', () => window.print());

async function relayRoundTrip(method, path, body = {}) {
  const queued = await fetchJson(root.dataset.relayEndpoint, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ action: 'request', method, path, body }),
  });
  for (let attempt = 0; attempt < 50; attempt += 1) {
    await sleep(1_500);
    const result = await fetchJson(`${root.dataset.relayEndpoint}?requestId=${encodeURIComponent(queued.id)}`);
    if (result.status !== 'completed') continue;
    if (Number(result.statusCode) >= 400) throw new Error(result.response?.error || 'PC bridgeで診断を開始できませんでした。');
    return result.response;
  }
  throw new Error('PC bridgeからの応答がありません。接続状態を確認してください。');
}

function codexMarkup(result) {
  const priorities = Array.isArray(result.priorities) ? result.priorities : [];
  const quickWins = Array.isArray(result.quickWins) ? result.quickWins : [];
  const cautions = Array.isArray(result.cautions) ? result.cautions : [];
  const limitations = Array.isArray(result.limitations) ? result.limitations : [];
  const impactLabels = { high: '影響：大', medium: '影響：中', low: '影響：小' };
  return `<div class="codex-result__head"><span>CODEX REVIEW</span><h4>${escapeHtml(result.overallAssessment || result.summary || '改善計画')}</h4><p>${escapeHtml(result.summary || '')}</p></div>
    <div class="codex-result__grid"><section><h5>優先改善</h5>${priorities.length ? `<ol>${priorities.map((item) => `<li><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.action)}</span><small>${escapeHtml(item.reason)}</small>${item.evidence ? `<small>証拠：${escapeHtml(item.evidence)}</small>` : ''}${item.impact ? `<small>${escapeHtml(impactLabels[item.impact] || `影響：${item.impact}`)}</small>` : ''}</li>`).join('')}</ol>` : '<p>追加の優先改善はありません。</p>'}</section>
    <section><h5>すぐできること</h5>${quickWins.length ? `<ul>${quickWins.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : '<p>公開診断の優先項目から進めてください。</p>'}</section></div>
    ${cautions.length ? `<div class="codex-result__cautions"><h5>確認が必要</h5><ul>${cautions.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div>` : ''}
    ${limitations.length ? `<div class="codex-result__cautions"><h5>この診断で未確認の範囲</h5><ul>${limitations.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div>` : ''}`;
}

codexButton?.addEventListener('click', async () => {
  if (!latestReport) return;
  codexButton.disabled = true;
  codexResult.hidden = true;
  codexStatus.classList.remove('is-error');
  codexStatus.textContent = '管理者ログインとPC bridgeの接続を確認しています…';
  try {
    const connection = await fetchJson(root.dataset.relayEndpoint);
    if (!connection.connected) throw new Error('PC bridgeが未接続です。接続画面を開き、このPCで npm.cmd run bridge を起動してください。');
    if (!connection.paired) throw new Error('PC bridgeとのペアリングが必要です。接続画面で6桁コードを入力してください。');
    codexStatus.textContent = 'Codex App Serverへ固定診断を渡しています…';
    const started = await relayRoundTrip('POST', '/v1/seo-diagnoses', {
      targetUrl: latestReport.auditedUrl,
      context: latestReport.context,
      auditReport: latestReport,
    });
    let run = started;
    for (let attempt = 0; attempt < 120; attempt += 1) {
      if (['completed', 'failed', 'interrupted'].includes(run.status)) break;
      codexStatus.textContent = run.stage || 'Codexが改善計画を整理しています…';
      await sleep(2_000);
      run = await relayRoundTrip('GET', `/v1/seo-diagnoses/${encodeURIComponent(started.id)}`);
    }
    if (run.status !== 'completed') throw new Error(run.error || 'Codex診断を完了できませんでした。');
    const structured = run.result || {};
    codexResult.innerHTML = codexMarkup(structured);
    codexResult.hidden = false;
    codexStatus.textContent = 'Codexの深掘り診断が完了しました。修正や公開はまだ行っていません。';
  } catch (error) {
    codexStatus.classList.add('is-error');
    codexStatus.textContent = error.status === 401
      ? 'この機能は管理者専用です。管理画面へログインし、PC bridgeを接続してください。'
      : error.message;
  } finally {
    codexButton.disabled = false;
  }
});

const mobileToggle = document.querySelector('[aria-controls="generated-mobile-nav"], #mobile-toggle');
const mobileNav = mobileToggle ? document.getElementById(mobileToggle.getAttribute('aria-controls')) : null;
mobileToggle?.addEventListener('click', () => {
  const open = mobileToggle.getAttribute('aria-expanded') !== 'true';
  mobileToggle.setAttribute('aria-expanded', String(open));
  mobileToggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
  mobileNav?.setAttribute('aria-hidden', String(!open));
  mobileNav?.classList.toggle('open', open);
});
