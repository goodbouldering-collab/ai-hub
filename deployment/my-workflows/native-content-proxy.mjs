// Copy this module with the native Studio assets. Authentication is supplied by
// each site's existing admin boundary; an Origin header is never authentication.
const UPSTREAM = 'https://business-content-app-server.aiclimb.workers.dev';
const PREFIX = '/api/content-studio';
const MAX_AGE = 365 * 24 * 60 * 60;
const encoder = new TextEncoder();
const routes = new Map([
  ['/api/profiles', 'GET'], ['/api/health', 'GET'], ['/api/key/verify', 'POST'],
  ['/api/blog/research', 'POST'], ['/api/blog/research-status', 'GET'],
  ['/api/blog/plan', 'POST'], ['/api/blog/draft', 'POST'], ['/api/blog/image', 'POST'],
  ['/api/reel/generate', 'POST'], ['/api/reel/video', 'POST'],
  ['/api/reel/video-status', 'GET'], ['/api/reel/video-content', 'GET'],
]);
const json = (data, status = 200, headers = {}) => Response.json(data, {
  status, headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', ...headers },
});
const encode = bytes => btoa(String.fromCharCode(...bytes)).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
const decode = text => Uint8Array.from(atob(text.replaceAll('-', '+').replaceAll('_', '/')), c => c.charCodeAt(0));
const validKey = key => typeof key === 'string' && /^sk-[A-Za-z0-9_-]{17,509}$/.test(key);

async function readBody(request, limit) {
  if (Number(request.headers.get('content-length')) > limit) throw new Error('body');
  const reader = request.body?.getReader();
  if (!reader) return {};
  const chunks = []; let size = 0; let timer;
  const deadline = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('timeout')), 10000); });
  try {
    for (;;) {
      const { value, done } = await Promise.race([reader.read(), deadline]);
      if (done) break;
      size += value.byteLength;
      if (size > limit) throw new Error('body');
      chunks.push(value);
    }
  } catch (error) { void reader.cancel().catch(() => {}); throw error; }
  finally { clearTimeout(timer); reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  const body = JSON.parse(new TextDecoder().decode(bytes) || '{}');
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new Error('object required');
  return body;
}

export function createNativeContentProxy({ profileId, clientOrigin, authorize, secret, serverKey = () => '', pathPrefix = PREFIX }) {
  if (!/^[a-z0-9-]+$/.test(profileId) || new URL(clientOrigin).protocol !== 'https:' || typeof authorize !== 'function' || typeof secret !== 'function') throw new Error('Native Studio configuration required');
  const cookieName = '__Host-content-studio-' + profileId;
  const context = request => encoder.encode(profileId + ':' + new URL(request.url).origin);
  async function encryptionKey(env) {
    const value = secret(env);
    if (typeof value !== 'string' || value.length < 32) throw new Error('encryption secret required');
    const digest = await crypto.subtle.digest('SHA-256', encoder.encode('content-studio:v1:' + profileId + ':' + value));
    return crypto.subtle.importKey('raw', digest, 'AES-GCM', false, ['encrypt', 'decrypt']);
  }
  async function savedKey(request, env) {
    try {
      const value = (request.headers.get('cookie') || '').split(';').map(s => s.trim()).find(s => s.startsWith(cookieName + '='))?.slice(cookieName.length + 1);
      if (!value || value.length > 2048) return '';
      const [iv, ciphertext] = value.split('.');
      const raw = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: decode(iv), additionalData: context(request) }, await encryptionKey(env), decode(ciphertext));
      const data = JSON.parse(new TextDecoder().decode(raw));
      return data.expires > Date.now() && validKey(data.key) ? data.key : '';
    } catch { return ''; }
  }
  async function keyCookie(key, request, env) {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv, additionalData: context(request) }, await encryptionKey(env), encoder.encode(JSON.stringify({ key, expires: Date.now() + MAX_AGE * 1000 })));
    return `${cookieName}=${encode(iv)}.${encode(new Uint8Array(encrypted))}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${MAX_AGE}`;
  }
  async function upstream(path, key, method, body) {
    const response = await fetch(UPSTREAM + path, {
      method, redirect: 'manual', signal: AbortSignal.timeout(120000),
      headers: { 'Content-Type': 'application/json', Origin: clientOrigin, 'X-Content-Studio-Embed': '1', ...(key ? { 'X-OpenAI-API-Key': key } : {}) },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (response.status >= 300 && response.status < 400) { void response.body?.cancel().catch(() => {}); throw new Error('redirect rejected'); }
    return response;
  }
  return async function handleNativeContent(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith(pathPrefix + '/')) return null;
    if (url.protocol !== 'https:' || request.headers.get('sec-fetch-site') === 'cross-site' || (request.headers.has('origin') && request.headers.get('origin') !== url.origin) || (request.method !== 'GET' && request.headers.get('origin') !== url.origin)) return json({ ok: false, error: '同じ事業の管理画面を開き直してください。' }, 403);
    let authenticated = false;
    try { authenticated = await authorize(request, env); } catch { /* fail closed */ }
    if (authenticated !== true) return json({ ok: false, error: '管理画面へログインしてください。' }, 401);
    const path = url.pathname.slice(pathPrefix.length);
    if (path === '/api/key/clear' && request.method === 'POST') return json({ ok: true }, 200, { 'Set-Cookie': `${cookieName}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0` });
    if (path === '/api/key/save' && request.method === 'POST') {
      try { await encryptionKey(env); } catch { return json({ ok: false, error: 'この管理画面の暗号化設定が未完了です。' }, 503); }
      let key;
      try { key = (await readBody(request, 2048)).key?.trim(); } catch { return json({ ok: false, error: '入力形式を確認してください。' }, 400); }
      if (!validKey(key)) return json({ ok: false, error: 'OpenAI APIキーの形式を確認してください。' }, 400);
      try {
        const response = await upstream('/api/key/verify', key, 'POST', {});
        if (!response.ok || (await response.json()).valid !== true) return json({ ok: false, error: 'APIキーを検証できませんでした。既存の保存内容は変更していません。' }, 422);
        return json({ ok: true, saved: true, retentionDays: 365 }, 200, { 'Set-Cookie': await keyCookie(key, request, env) });
      } catch { return json({ ok: false, error: '検証先に接続できませんでした。既存の保存内容は変更していません。' }, 502); }
    }
    if (!routes.has(path)) return json({ ok: false, error: 'Not found' }, 404);
    if (request.method !== routes.get(path)) return json({ ok: false, error: 'Method not allowed' }, 405);
    const stored = await savedKey(request, env);
    const fallback = serverKey(env);
    const key = stored || (validKey(fallback) ? fallback : '');
    if (path === '/api/health') return json({ ok: true, profileId, mode: key ? 'live' : 'mock', savedKeyConfigured: Boolean(stored), openaiConfigured: Boolean(!stored && key), secureKeyStorage: true, keyRetentionDays: 365 });
    if (!key && path !== '/api/profiles') return json({ ok: false, error: 'OpenAI APIキーを入力し「検証して保存」を押してください。' }, 409);
    let body;
    if (request.method === 'POST') {
      try { body = await readBody(request, 1024 * 1024); } catch { return json({ ok: false, error: '入力は1MiB以内のJSONにしてください。' }, 400); }
      if (body.profileId && body.profileId !== profileId) return json({ ok: false, error: 'この管理画面の事業だけを選択できます。' }, 403);
      body.profileId = profileId;
    }
    try {
      const response = await upstream(path + url.search, key, request.method, body);
      if (!response.ok) { void response.body?.cancel().catch(() => {}); return json({ ok: false, error: '生成APIの処理に失敗しました。キーの有効性・利用上限と入力内容を確認してください。' }, response.status); }
      if (path === '/api/profiles') {
        const data = await response.json();
        return json({ ok: true, profiles: (data.profiles || []).filter(p => p.id === profileId) });
      }
      return new Response(response.body, { status: response.status, headers: { 'Content-Type': response.headers.get('content-type') || 'application/json', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });
    } catch { return json({ ok: false, error: '生成APIに接続できませんでした。時間をおいて再試行してください。' }, 502); }
  };
}
