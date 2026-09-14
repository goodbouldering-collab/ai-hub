const routes = new Map([
  ['/api/admin/command-center-market', ['GET', '/api/v1/market']],
  ['/api/admin/command-center-screen', ['POST', '/api/v1/screens']],
  ['/api/admin/command-center-security', ['GET', '/api/v1/securities/']],
  ['/api/admin/command-center-market-sources', ['GET', '/api/v1/sources/status']],
]);
const statuses = new Set(['research_candidate', 'watch', 'deprioritize', 'insufficient_data']);
const headers = { 'cache-control': 'private, no-store', 'x-content-type-options': 'nosniff' };
const reply = (body, status = 200) => Response.json(body, { status, headers });
export const isMarketCompassRoute = path => routes.has(path);

async function withinDeadline(promise, signal) {
  signal.throwIfAborted();
  let abort;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      abort = () => reject(new Error('deadline'));
      signal.addEventListener('abort', abort, { once: true });
    })]);
  } finally { signal.removeEventListener('abort', abort); }
}

async function boundedText(body, limit, signal) {
  const reader = body?.getReader();
  if (!reader) throw new Error('empty_body');
  const abort = () => { void reader.cancel().catch(() => {}); };
  signal.addEventListener('abort', abort, { once: true });
  const chunks = [];
  let size = 0;
  try {
    while (true) {
      signal.throwIfAborted();
      const { done, value } = await withinDeadline(reader.read(), signal);
      signal.throwIfAborted();
      if (done) break;
      size += value.byteLength;
      if (size > limit) throw new Error('oversized_body');
      chunks.push(value);
    }
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } finally {
    signal.removeEventListener('abort', abort);
    void reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

function symbols(value) {
  if (!Array.isArray(value) || value.length < 1 || value.length > 24 || value.some(s => typeof s !== 'string' || !/^\d{4}$/.test(s))) throw new Error('invalid_symbols');
  return [...new Set(value)];
}

// Called only after the existing admin session has been checked.
// The binding selects the private Worker; no caller URL or headers are forwarded.
export async function marketCompass(request, env, { timeoutMs = 7500 } = {}) {
  const url = new URL(request.url);
  const route = routes.get(url.pathname);
  if (!route) return null;
  const [method, basePath] = route;
  if (request.method !== method) return new Response(null, { status: 405, headers: { ...headers, allow: method } });
  if (method === 'POST' && request.headers.get('origin') !== url.origin) return reply({ error: 'Origin rejected' }, 403);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let targetPath = basePath;
  let body;
  try {
    try {
      if (method === 'POST') {
        if ((request.headers.get('content-type') || '').split(';')[0].trim().toLowerCase() !== 'application/json') return reply({ error: 'invalid_request' }, 400);
        const input = JSON.parse(await boundedText(request.body, 32768, controller.signal));
        const clean = { symbols: symbols(input?.symbols) };
        if (input.filters !== undefined) {
          if (!input.filters || typeof input.filters !== 'object' || Array.isArray(input.filters)) throw new Error('invalid_filters');
          const overall = input.filters.overall;
          if (overall !== undefined) {
            if (!Array.isArray(overall) || overall.some(s => !statuses.has(s))) throw new Error('invalid_filters');
            clean.filters = { overall: [...new Set(overall)] };
          }
        }
        body = JSON.stringify(clean);
      } else if (basePath.endsWith('/securities/')) {
        targetPath += symbols([url.searchParams.get('symbol')])[0];
      } else if (basePath.endsWith('/market') && url.searchParams.has('symbols')) {
        targetPath += '?' + new URLSearchParams({ symbols: symbols(url.searchParams.get('symbols').split(',').map(s => s.trim())).join(',') });
      }
    } catch { return reply({ error: 'invalid_request' }, 400); }
    const token = env.MARKET_COMPASS_SERVICE_TOKEN?.trim();
    if (!token || typeof env.MARKET_COMPASS?.fetch !== 'function') return reply({ error: 'market_compass_unavailable' }, 503);
    const upstream = await withinDeadline(env.MARKET_COMPASS.fetch(new Request('https://market-compass.internal' + targetPath, {
      method, body, redirect: 'manual', signal: controller.signal,
      headers: { accept: 'application/json', ...(body ? { 'content-type': 'application/json' } : {}), 'x-market-compass-service-token': token },
    })), controller.signal);
    if (!upstream.ok || !(upstream.headers.get('content-type') || '').toLowerCase().startsWith('application/json')) {
      void upstream.body?.cancel().catch(() => {});
      return reply({ error: 'market_compass_unavailable' }, 503);
    }
    const text = await boundedText(upstream.body, 2 * 1024 * 1024, controller.signal);
    const payload = JSON.parse(text);
    if (!payload || typeof payload !== 'object' || Array.isArray(payload) || JSON.stringify(payload).includes(token)) throw new Error('invalid_response');
    return reply(payload);
  } catch { return reply({ error: 'market_compass_unavailable' }, 503); }
  finally { clearTimeout(timer); }
}
