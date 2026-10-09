import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './worker.mjs';
import bundled from './published-worker.mjs';

for (const [label, target] of [['source', worker], ['bundle', bundled]]) test(`AI相談 ${label}: published login authorizes encrypted key save and both workflows`, async t => {
  const origin = 'https://aiclimb.aiclimb.workers.dev';
  const env = { ADMIN_PASS: 'synthetic-password', ADMIN_SESSION_SECRET: 'synthetic-independent-secret-at-least-32-characters', ADMIN_LOGIN_LIMITER: { limit: async () => ({ success: true }) } };
  const key = 'sk-synthetic-test-key-not-a-real-credential';
  const request = (path, cookie = '', body) => new Request(origin + '/api/content-studio/api/' + path, {
    method: body ? 'POST' : 'GET', headers: { origin, cookie, 'content-type': 'application/json' },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  t.mock.method(globalThis, 'fetch', async () => Response.json({ ok: true, valid: true }));
  assert.equal((await target.fetch(request('key/save', '', { key }), env)).status, 401);
  const login = await target.fetch(new Request(origin + '/admin/login', { method: 'POST', headers: { origin, 'content-type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ password: env.ADMIN_PASS }) }), env);
  assert.equal(login.status, 303);
  const admin = login.headers.get('set-cookie').split(';')[0];
  const saved = await target.fetch(request('key/save', admin, { key }), env);
  assert.equal(saved.status, 200);
  const cookie = saved.headers.get('set-cookie').split(';')[0];
  const both = admin + '; ' + cookie;
  const health = await (await target.fetch(request('health', both), env)).json();
  assert.equal(health.savedKeyConfigured, true);
  assert.equal(health.profileId, 'ai-hub');
  for (const route of ['blog/plan', 'reel/generate']) assert.equal((await target.fetch(request(route, both, {}), env)).status, 200);
  assert.equal((await target.fetch(request('health', cookie), env)).status, 401);
  for (const name of ['blog.html', 'reel.html']) {
    assert.equal((await target.fetch(new Request(origin + '/admin/apps/' + name), env)).status, 303);
    const ui = await target.fetch(new Request(origin + '/admin/apps/' + name, { headers: { cookie: admin } }), env);
    assert.equal(ui.status, 200);
    assert.match(await ui.text(), /365日間/);
  }
  env.ASSETS = { fetch: async () => new Response('unchanged public asset') };
  assert.equal(await (await target.fetch(new Request(origin + '/blog/example.html'), env)).text(), 'unchanged public asset');
});
