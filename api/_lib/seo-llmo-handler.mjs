import { SeoLlmoAuditError, runSeoLlmoAudit } from './seo-llmo-audit.mjs';

const buckets = new Map();
const WINDOW_MS = 10 * 60 * 1000;
const REQUEST_LIMIT = 12;
const MAX_BUCKETS = 5_000;

const clientKey = (req) => {
  const forwarded = String(req.headers?.['x-forwarded-for'] || '').split(',')[0].trim();
  return forwarded || req.socket?.remoteAddress || 'unknown';
};

const allowRequest = (key, now = Date.now()) => {
  if (buckets.size >= MAX_BUCKETS && !buckets.has(key)) {
    for (const [bucketKey, bucket] of buckets) {
      if (bucket.resetAt <= now) buckets.delete(bucketKey);
    }
    while (buckets.size >= MAX_BUCKETS) buckets.delete(buckets.keys().next().value);
  }
  const current = buckets.get(key);
  if (!current || current.resetAt <= now) {
    buckets.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return true;
  }
  current.count += 1;
  return current.count <= REQUEST_LIMIT;
};

const send = (res, status, payload) => {
  res.setHeader('Cache-Control', 'private, no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.status(status).json(payload);
};

const parseBody = (req) => {
  if (typeof req.body === 'string') return JSON.parse(req.body || '{}');
  return req.body || {};
};

export function createSeoLlmoAuditHandler(options = {}) {
  const audit = options.audit ?? runSeoLlmoAudit;
  const now = options.now ?? Date.now;
  return async function seoLlmoAuditHandler(req, res) {
    if (String(req.method || 'GET').toUpperCase() !== 'POST') {
      res.setHeader('Allow', 'POST');
      send(res, 405, { error: 'method_not_allowed', message: 'POSTで診断してください。' });
      return;
    }
    const declared = Number(req.headers?.['content-length'] || 0);
    if (declared > 16_384) {
      send(res, 413, { error: 'request_too_large', message: '入力が大きすぎます。' });
      return;
    }
    if (!allowRequest(clientKey(req), Number(now()))) {
      res.setHeader('Retry-After', String(Math.ceil(WINDOW_MS / 1000)));
      send(res, 429, { error: 'rate_limited', message: '短時間の診断回数が多いため、少し待ってから再度お試しください。' });
      return;
    }
    try {
      const serializedBody = typeof req.body === 'string' ? req.body : JSON.stringify(req.body ?? {});
      if (Buffer.byteLength(serializedBody, 'utf8') > 16_384) {
        send(res, 413, { error: 'request_too_large', message: '入力が大きすぎます。' });
        return;
      }
      const body = parseBody(req);
      const report = await audit({ url: body.url, context: body.context || {} });
      send(res, 200, { ok: true, report });
    } catch (error) {
      if (error instanceof SyntaxError) {
        send(res, 400, { error: 'invalid_json', message: '入力形式を確認してください。' });
        return;
      }
      if (error instanceof SeoLlmoAuditError) {
        send(res, error.status, { error: error.code, message: error.message });
        return;
      }
      send(res, 502, { error: 'audit_failed', message: 'ページを診断できませんでした。時間をおいて再度お試しください。' });
    }
  };
}
