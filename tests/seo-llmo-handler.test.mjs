import test from 'node:test';
import assert from 'node:assert/strict';

import { SeoLlmoAuditError } from '../api/_lib/seo-llmo-audit.mjs';
import { createSeoLlmoAuditHandler } from '../api/_lib/seo-llmo-handler.mjs';

const responseDouble = () => ({
  statusCode: 0,
  headers: {},
  payload: null,
  setHeader(name, value) { this.headers[String(name).toLowerCase()] = value; },
  status(code) { this.statusCode = code; return this; },
  json(payload) { this.payload = payload; return this; },
});

test('public audit handler accepts only a bounded POST and returns no-store JSON', async () => {
  const seen = [];
  const handler = createSeoLlmoAuditHandler({
    audit: async (input) => { seen.push(input); return { score: 72, targetUrl: input.url }; },
    now: () => 1000,
  });
  const response = responseDouble();
  await handler({
    method: 'POST',
    headers: { 'content-length': '120', 'x-forwarded-for': '203.0.113.41' },
    body: { url: 'https://example.com/', context: { audience: '地域事業者' } },
    socket: {},
  }, response);

  assert.equal(response.statusCode, 200);
  assert.equal(response.headers['cache-control'], 'private, no-store, max-age=0');
  assert.deepEqual(response.payload, { ok: true, report: { score: 72, targetUrl: 'https://example.com/' } });
  assert.deepEqual(seen, [{ url: 'https://example.com/', context: { audience: '地域事業者' } }]);
});

test('public audit handler rejects wrong methods, oversized bodies, and safe validation errors', async () => {
  const handler = createSeoLlmoAuditHandler({
    audit: async () => { throw new SeoLlmoAuditError('host_not_public', '公開URLだけ診断できます。', 400); },
    now: () => 2000,
  });

  const wrongMethod = responseDouble();
  await handler({ method: 'GET', headers: {}, socket: {} }, wrongMethod);
  assert.equal(wrongMethod.statusCode, 405);
  assert.equal(wrongMethod.headers.allow, 'POST');

  const oversized = responseDouble();
  await handler({ method: 'POST', headers: { 'content-length': '20000', 'x-forwarded-for': '203.0.113.42' }, body: {}, socket: {} }, oversized);
  assert.equal(oversized.statusCode, 413);

  const undeclaredOversized = responseDouble();
  await handler({ method: 'POST', headers: { 'x-forwarded-for': '203.0.113.44' }, body: { url: 'https://example.com/', context: { problem: 'a'.repeat(17_000) } }, socket: {} }, undeclaredOversized);
  assert.equal(undeclaredOversized.statusCode, 413);

  const invalid = responseDouble();
  await handler({ method: 'POST', headers: { 'x-forwarded-for': '203.0.113.43' }, body: { url: 'http://localhost' }, socket: {} }, invalid);
  assert.equal(invalid.statusCode, 400);
  assert.deepEqual(invalid.payload, { error: 'host_not_public', message: '公開URLだけ診断できます。' });
});

test('public audit handler returns a retry window after the per-instance request limit', async () => {
  const handler = createSeoLlmoAuditHandler({
    audit: async () => ({ score: 50 }),
    now: () => 3_000,
  });
  let lastResponse;
  for (let index = 0; index < 13; index += 1) {
    lastResponse = responseDouble();
    await handler({
      method: 'POST',
      headers: { 'x-forwarded-for': '203.0.113.199' },
      body: { url: 'https://example.com/' },
      socket: {},
    }, lastResponse);
  }

  assert.equal(lastResponse.statusCode, 429);
  assert.equal(lastResponse.headers['retry-after'], '600');
});
