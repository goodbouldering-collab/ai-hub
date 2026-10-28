import published from '../admin-workspace/published-worker.mjs';
import { resolve4, resolve6 } from 'node:dns/promises';
import { assertPublicAuditTarget, decodeDocumentBuffer, SeoLlmoAuditError, runSeoLlmoAudit, analyzeSeoLlmoDocument } from '../../api/_lib/seo-llmo-audit.mjs';
import { extractLocalProfile, PlacesError, runPlacesSearch } from '../../api/_lib/meo-places.mjs';

const headers = { 'cache-control': 'private, no-store, max-age=0', 'x-content-type-options': 'nosniff' };
const json = (body, status = 200, extra = {}) => Response.json(body, { status, headers: { ...headers, ...extra } });
const buckets = new Map();
export async function workerLookup(hostname) {
  const answers = await Promise.allSettled([resolve4(hostname), resolve6(hostname)]);
  return answers.flatMap((result, i) => result.status === 'fulfilled' ? result.value.map(address => ({ address, family: i ? 6 : 4 })) : []);
}

// Cloudflare node:http does not implement the pinned lookup option. Use its
// public Internet fetch transport, validate every redirect, and never forward
// caller headers, credentials, service bindings or private-network bindings.
export function publicDocumentFetcher(fetchImpl = fetch, lookup = workerLookup) {
  return async (input, options = {}) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), Math.max(1, Math.min(options.timeoutMs || 10_000, (options.deadlineAt || Date.now() + 10_000) - Date.now())));
    try {
      let url = input;
      for (let hop = 0; hop <= 4; hop++) {
        url = await assertPublicAuditTarget(url, lookup, options.deadlineAt);
        const response = await fetchImpl(url.href, { redirect: 'manual', signal: controller.signal,
          headers: { accept: options.accept || 'text/html', 'user-agent': 'AIClimb-Public-Site-Diagnosis/1.0' } });
        if ([301, 302, 303, 307, 308].includes(response.status)) {
          await response.body?.cancel();
          if (hop === 4 || !response.headers.get('location')) throw new Error('redirect_limit');
          url = new URL(response.headers.get('location'), url); continue;
        }
        const maxBytes = options.maxBytes || 1_250_000;
        if (Number(response.headers.get('content-length')) > maxBytes) { await response.body?.cancel(); throw new Error('too_large'); }
        const reader = response.body?.getReader(); const chunks = []; let size = 0;
        if (reader) {
          try {
            while (true) { const { done, value } = await reader.read(); if (done) break; size += value.byteLength; if (size > maxBytes) throw new Error('too_large'); chunks.push(value); }
          } finally { await reader.cancel().catch(() => {}); }
        }
        const contentType = response.headers.get('content-type') || '';
        return { body: decodeDocumentBuffer(Buffer.concat(chunks), contentType), finalUrl: url.href, contentType, status: response.status };
      }
    } catch (error) {
      if (error instanceof SeoLlmoAuditError) throw error;
      throw new SeoLlmoAuditError('request_failed', '公開ページを取得できませんでした。URLを確認して再度お試しください。', 422);
    } finally { clearTimeout(timer); }
  };
}

async function boundedBody(request) {
  if (Number(request.headers.get('content-length')) > 16_384) throw new PlacesError('too_large', '入力が大きすぎます。', 413);
  const reader = request.body?.getReader(); if (!reader) throw new SyntaxError();
  const parts = []; let size = 0;
  try {
    while (true) { const { done, value } = await reader.read(); if (done) break; size += value.byteLength; if (size > 16_384) throw new PlacesError('too_large', '入力が大きすぎます。', 413); parts.push(value); }
  } finally { await reader.cancel().catch(() => {}); }
  const input = JSON.parse(Buffer.concat(parts).toString('utf8'));
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new SyntaxError();
  return input;
}

export function createDiagnosisWorker({ previous = published, lookup = workerLookup, fetchImpl = fetch, audit = runSeoLlmoAudit } = {}) {
  return { async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (!['/api/seo-llmo-audit', '/api/meo-places'].includes(url.pathname)) return previous.fetch(request, env, ctx);
    if (url.pathname === '/api/meo-places' && request.method === 'GET') return json({ configured: Boolean(env.GOOGLE_PLACES_API_KEY), billingMode: 'ids-only' });
    if (request.method !== 'POST') return json({ message: 'POSTで診断してください。' }, 405, { allow: 'POST' });
    const origin = request.headers.get('origin');
    if (origin && origin !== url.origin) return json({ message: '診断ページから操作してください。' }, 403);
    const key = request.headers.get('cf-connecting-ip') || 'unknown'; const now = Date.now();
    if (buckets.size >= 5000) for (const [id, bucket] of buckets) if (bucket.until <= now) buckets.delete(id);
    let bucket = buckets.get(key);
    if (!bucket || bucket.until <= now) {
      if (buckets.size >= 5000 && !buckets.has(key)) return json({ message: '混雑しています。時間をおいてお試しください。' }, 429);
      bucket = { count: 0, until: now + 600_000 }; buckets.set(key, bucket);
    }
    if (++bucket.count > 20) return json({ message: '診断回数が多いため、10分ほど待って再度お試しください。' }, 429, { 'retry-after': '600' });
    try {
      const body = await boundedBody(request);
      if (url.pathname === '/api/meo-places') return json({ ok: true, result: await runPlacesSearch(body, { apiKey: env.GOOGLE_PLACES_API_KEY, fetchImpl }) });
      let profile;
      const getDocument = publicDocumentFetcher(fetchImpl, lookup);
      const report = await audit(body, { lookup, requestDocument: async (target, options) => {
        const result = await getDocument(target, options);
        if (!profile && options.accept?.startsWith('text/html')) profile = extractLocalProfile(result.body, analyzeSeoLlmoDocument(result.body, result.finalUrl));
        return result;
      } });
      return json({ ok: true, report: { ...report, localProfile: profile } });
    } catch (error) {
      if (error instanceof SyntaxError) return json({ message: '入力形式を確認してください。' }, 400);
      if (error instanceof PlacesError || error instanceof SeoLlmoAuditError) return json({ error: error.code, message: error.message }, error.status);
      return json({ message: '診断を完了できませんでした。時間をおいて再度お試しください。' }, 502);
    }
  } };
}
export default createDiagnosisWorker();
