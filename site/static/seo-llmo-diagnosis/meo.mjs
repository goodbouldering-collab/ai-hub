const panel = document.getElementById('meo-panel');
const form = document.getElementById('meo-form');
const status = document.getElementById('meo-status');
const candidates = document.getElementById('meo-candidates');
const result = document.getElementById('meo-result');
const find = document.getElementById('meo-find');
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let revision = 0; let active; let configured = false; let latest = null;
const attribution = data => `<p class="meo-attribution"><span translate="no">Google Maps</span>${(data.attributions || []).map(a => ` · <a href="${escape(a.uri)}" target="_blank" rel="noopener noreferrer">${escape(a.provider)}</a>`).join('')}</p>`;
function reset() {
  revision++; active?.abort(); candidates.hidden = true; result.hidden = true;
  candidates.innerHTML = ''; result.innerHTML = ''; status.textContent = ''; latest = null;
  if (find) find.disabled = !configured;
}
export function resetMeo() {
  reset(); form?.reset();
  if (panel) { document.getElementById('meo-profile-source').textContent = '店舗名・地域・業種を直接入力しても調べられます。'; document.getElementById('meo-branches').hidden = true; }
}
export function setLocalProfile(profile) {
  if (!form || !profile) return; reset();
  for (const name of ['storeName', 'area', 'keyword']) form.elements.namedItem(name).value = profile[name] || '';
  document.getElementById('meo-profile-source').textContent = `${profile.source}。店舗名・地域・業種を確認し、違っていたら修正してください。`;
  const branches = document.getElementById('meo-branches');
  branches.hidden = !(profile.alternatives?.length > 1);
  branches.replaceChildren();
  if (!branches.hidden) {
    const label = document.createElement('label'); label.textContent = '複数の店舗情報がありました：';
    const select = document.createElement('select'); select.setAttribute('aria-label', 'サイト内の店舗を選ぶ');
    for (const [i, item] of profile.alternatives.entries()) { const option = document.createElement('option'); option.value = i; option.textContent = `${item.storeName} / ${item.area}`; select.append(option); }
    select.addEventListener('change', () => { const item = profile.alternatives[Number(select.value)]; reset(); for (const name of ['storeName','area','keyword']) form.elements.namedItem(name).value = item[name] || ''; });
    label.append(select); branches.append(label);
  }
}
export function meoResultText() {
  if (!latest) return '';
  return `\nPlaces検索の参考順位: ${latest.rank === null ? `取得した${latest.examined}件に対象なし（順位未確認）` : latest.rank + '番目'}\n検索語: ${latest.query}\n確認日時: ${latest.checkedAt}\n${latest.disclaimer}\nGoogle Maps: ${latest.mapsUrl}`;
}
async function request(body) {
  active = new AbortController(); const timer = setTimeout(() => active.abort(), 22_000);
  try {
    const response = await fetch('/api/meo-places', { method: 'POST', headers: {'content-type':'application/json'}, body: JSON.stringify(body), signal: active.signal });
    const data = await response.json(); if (!response.ok) throw new Error(data.message || '店舗検索を完了できませんでした。'); return data.result;
  } finally { clearTimeout(timer); }
}
form?.addEventListener('input', reset);
form?.addEventListener('submit', async event => {
  event.preventDefault(); if (!form.reportValidity()) return; reset();
  const current = revision; const values = Object.fromEntries(new FormData(form));
  find.disabled = true; status.textContent = '店舗候補を探しています…';
  try {
    const data = await request({action:'candidates', ...values}); if (revision !== current) return;
    if (!data.candidates.length) { status.textContent = '候補が見つかりません。店舗名・地域を具体的にして再検索してください。'; return; }
    status.textContent = '各候補をGoogle Mapsで開き、店舗名と住所が一致するものを選んでください。';
    candidates.innerHTML = `<h3>対象店舗を確認</h3><p>候補の番号は検索順位ではありません。${data.hasMore ? '最初の5候補です。対象がなければ店舗名・地域を詳しくしてください。' : ''}</p><div class="meo-candidate-list">${data.candidates.map((c,i) => `<article><a href="${escape(c.mapsUrl)}" target="_blank" rel="noopener noreferrer">候補${i+1}をGoogle Mapsで確認 ↗</a><button type="button" class="audit-button audit-button--secondary" data-place="${escape(c.id)}">この店舗で参考順位を調べる</button></article>`).join('')}</div>${attribution(data)}`;
    candidates.hidden = false;
    for (const button of candidates.querySelectorAll('[data-place]')) button.addEventListener('click', () => rank(values, button.dataset.place));
  } catch (error) { if (revision === current) status.textContent = error.name === 'AbortError' ? '検索に時間がかかっています。再度お試しください。' : error.message; }
  finally { if (revision === current) find.disabled = !configured; }
});
async function rank(values, placeId) {
  const current = ++revision; active?.abort(); latest = null; result.hidden = true;
  candidates.querySelectorAll('button').forEach(b => {b.disabled = true;}); find.disabled = true;
  status.textContent = '地域と業種で検索しています…';
  try {
    const data = await request({action:'rank', ...values, placeId, confirmed:true}); if (revision !== current) return;
    latest = data;
    result.innerHTML = `<p class="audit-eyebrow">Places検索の参考順位</p><h3>${data.rank === null ? '取得した結果に対象店舗がありません' : `<strong>${data.rank}</strong> 番目`}</h3><p>検索語：<b>${escape(data.query)}</b></p><p>${data.rank === null ? `${data.examined}件を確認しました。順位は未確認です。${data.hasMore ? '続きの検索結果は取得していません。' : ''}` : `取得した${data.examined}件内での位置です。`}</p><p>確認：${escape(new Date(data.checkedAt).toLocaleString('ja-JP'))}</p><p>${escape(data.disclaimer)}</p><a href="${escape(data.mapsUrl)}" target="_blank" rel="noopener noreferrer">確認した店舗を開く ↗</a> · <a href="${escape(data.searchUrl)}" target="_blank" rel="noopener noreferrer">Google Mapsでも検索する ↗</a>${attribution(data)}`;
    result.hidden = false; status.textContent = '検索条件と確認日時を添えて表示しました。';
    result.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'center'});
  } catch (error) { if (revision === current) status.textContent = error.name === 'AbortError' ? '検索に時間がかかっています。再度お試しください。' : error.message; }
  finally { if (revision === current) {find.disabled = !configured; candidates.querySelectorAll('button').forEach(b => {b.disabled = false;});} }
}
if (panel) fetch('/api/meo-places').then(async response => {
  if (!response.ok) throw new Error(); const data = await response.json(); configured = data.configured === true; find.disabled = !configured;
  document.getElementById('meo-connection').textContent = configured ? '店舗検索を利用できます。' : '店舗検索は準備中です。運営者によるGoogle Places APIの接続が必要です。サイト診断は利用できます。';
}).catch(() => { document.getElementById('meo-connection').textContent = '店舗検索への接続を確認できません。ページを開き直してください。'; });
