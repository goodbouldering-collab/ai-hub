import test from 'node:test';
import assert from 'node:assert/strict';
import current from '../deployment/admin-workspace/published-worker.mjs';
import workflows from '../deployment/my-workflows/published-worker.mjs';
import news from '../deployment/ai-news/published-worker.mjs';
import profile from '../deployment/profile/published-worker.mjs';

const origin = 'https://aiclimb.aiclimb.workers.dev';
for (const [name, worker] of Object.entries({ current, workflows, news, profile })) {
  test(`${name}: article generation uses only OpenAI and rejects incomplete results`, async t => {
    const env = { ADMIN_PASS: 'test-password', ADMIN_SESSION_SECRET: 'test-session-secret',
      ADMIN_LOGIN_LIMITER: { limit: async () => ({ success: true }) }, OPENAI_API_KEY: 'test-openai' };
    const login = await worker.fetch(new Request(origin + '/admin/login', { method: 'POST',
      headers: { origin, 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ password: env.ADMIN_PASS }) }), env);
    assert.equal(login.status, 303);
    const cookie = login.headers.get('set-cookie').split(';')[0];
    const request = () => new Request(origin + '/api/admin/generate-articles', { method: 'POST',
      headers: { origin, cookie, 'content-type': 'application/json' }, body: JSON.stringify({ theme: 'test', count: 1 }) });
    let calls = 0;
    let completed = true;
    t.mock.method(globalThis, 'fetch', async (url, options) => {
      calls++;
      assert.equal(url, 'https://api.openai.com/v1/responses');
      assert.equal(options.headers.Authorization, 'Bearer test-openai');
      const input = JSON.parse(options.body);
      assert.equal(input.store, false);
      assert.ok(input.instructions);
      assert.ok(input.input);
      return Response.json({ status: completed ? 'completed' : 'incomplete', output: [
        { type: 'reasoning', summary: [] },
        { type: 'message', content: [{ type: 'output_text', text: JSON.stringify([
          { title: 'テスト', html: '<h2>見出し</h2><p>本文</p><script>bad()</script>', summary: '要約' },
        ]) }] },
      ] });
    });
    const response = await worker.fetch(request(), env);
    assert.equal(response.status, 200);
    assert.doesNotMatch((await response.json()).drafts[0].html, /script|bad/);
    completed = false;
    assert.equal((await worker.fetch(request(), env)).status, 502);
    delete env.OPENAI_API_KEY;
    assert.equal((await worker.fetch(request(), env)).status, 503);
    assert.equal(calls, 2);
    const ping = await (await worker.fetch(new Request(origin + '/api/admin/ping', { headers: { cookie } }), env)).json();
    assert.ok(!Object.hasOwn(ping.env, 'hasAnthropic'));
  });
}
