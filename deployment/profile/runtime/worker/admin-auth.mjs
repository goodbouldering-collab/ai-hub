import { createHash, createHmac, timingSafeEqual } from 'node:crypto';
import { loginPage } from './login-page.mjs';
import adminAssets from './admin-assets.generated.mjs';
import { readGroups } from './groups.mjs';
import { updateGroup } from './groups-write.mjs';
import { reorderGroups } from './groups-reorder.mjs';
import { createGroup } from './groups-create.mjs';
import { articleAI } from './articles-ai.mjs';
import { publishArticle } from './article-publish.mjs';
import { unpublishArticle } from './article-unpublish.mjs';
import { generateImage, imageConfiguration } from './image-r2.mjs';
import { isMarketCompassRoute, marketCompass } from './market-compass.mjs';

const COOKIE = 'ai_hub_admin_session';
const MAX_AGE = 60 * 60 * 24 * 14;
const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status = 200) => Response.json(body, { status, headers });
const sign = (expiry, env) => createHmac('sha256', env.ADMIN_SESSION_SECRET || env.ADMIN_PASS).update(String(expiry)).digest('base64url');
const equal = (a, b) => timingSafeEqual(createHash('sha256').update(a).digest(), createHash('sha256').update(b).digest());

function safeNext(value) {
  if (!value || !value.startsWith('/') || value.startsWith('//')) return '/admin';
  try {
    if (/[\\\x00-\x1f\x7f]/.test(decodeURIComponent(value))) return '/admin';
  } catch { return '/admin'; }
  return value;
}

function validSession(request, env) {
  try {
    const cookies = (request.headers.get('cookie') || '').split(';').map(part => part.trim());
    const matches = cookies.filter(part => part.startsWith(`${COOKIE}=`));
    if (matches.length !== 1) return false;
    const token = decodeURIComponent(matches[0].slice(COOKIE.length + 1));
    const parts = token.split('.');
    if (parts.length !== 2 || !/^\d+$/.test(parts[0])) return false;
    const expires = Number(parts[0]);
    return Number.isSafeInteger(expires) && expires > Date.now() && equal(parts[1], sign(expires, env));
  } catch { return false; }
}

function cookie(value, maxAge) {
  return `${COOKIE}=${encodeURIComponent(value)}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}

function redirect(location, sessionCookie) {
  return new Response(null, { status: 303, headers: { ...headers, location, ...(sessionCookie ? { 'set-cookie': sessionCookie } : {}) } });
}

async function readForm(request) {
  if (!(request.headers.get('content-type') || '').toLowerCase().startsWith('application/x-www-form-urlencoded')) return null;
  const reader = request.body?.getReader();
  if (!reader) return new URLSearchParams();
  const chunks = [];
  let size = 0;
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 8192) { await reader.cancel(); return null; }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return new URLSearchParams(new TextDecoder().decode(bytes));
}

// Explicit routes only: other admin operations remain unavailable until migrated.
export async function handleAdminAuth(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;
  const isLogin = ['/admin/login', '/api/admin/login'].includes(path);
  const isLogout = ['/admin/logout', '/api/admin/logout'].includes(path);
  const isPing = path === '/api/admin/ping';
  const isGroups = path === '/api/admin/groups';
  const isReorder = path === '/api/admin/reorder-groups';
  const isArticleAI = ['/api/admin/generate-articles', '/api/admin/revise-article'].includes(path);
  const isPublish = path === '/api/admin/publish-article';
  const isUnpublish = path === '/api/admin/unpublish-article';
  const isImage = path === '/api/admin/generate-image';
  const isWatch = path === '/watch' || path.startsWith('/watch/');
  const isMarket = isMarketCompassRoute(path);
  const blogPaths = ['/admin', '/admin/', '/api/admin', '/api/admin/', '/admin/blog', '/admin/blog/', '/admin/blog/status', '/admin/blog/settings', '/admin/blog/articles', '/admin/blog/generate', '/admin/blog/editor', '/admin/blog/publish'];
  const studioEntry = ['/admin/blog', '/admin/blog/', '/admin/blog/generate'].includes(path);
  const asset = adminAssets[blogPaths.includes(path) ? '/admin' : path];
  if (!isLogin && !isLogout && !isPing && !asset && !isGroups && !isReorder && !isArticleAI && !isPublish && !isUnpublish && !isImage && !isWatch && !isMarket) return null;
  if (!env.ADMIN_PASS) return json({ error: 'Admin authentication is not configured' }, 503);
  if (isMarket) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    return marketCompass(request, env);
  }
  if (isWatch) {
    if (!validSession(request, env)) return redirect(`/admin/login?next=${encodeURIComponent(safeNext(path + url.search))}`);
    if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, { status: 405, headers: { ...headers, allow: 'GET, HEAD' } });
    const assetResponse = await env.ASSETS.fetch(request);
    const response = new Response(request.method === 'HEAD' ? null : assetResponse.body, assetResponse);
    response.headers.set('cache-control', 'private, no-store');
    response.headers.set('x-robots-tag', 'noindex, nofollow');
    response.headers.set('x-aiclimb-delivery', 'cloudflare-authenticated-assets');
    return response;
  }
  if (isImage) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    return generateImage(request, env);
  }
  if (isUnpublish) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    return unpublishArticle(request, env);
  }
  if (isPublish) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    return publishArticle(request, env);
  }
  if (isArticleAI) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    return articleAI(request, env, path.endsWith('/revise-article'));
  }
  if (isReorder) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    return reorderGroups(request, env);
  }
  if (isGroups) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    if (request.method === 'PUT') return updateGroup(request, env);
    if (request.method === 'POST') return createGroup(request, env);
    return readGroups(request, env);
  }
  if (asset) {
    if (!validSession(request, env)) return redirect(`/admin/login?next=${encodeURIComponent(safeNext(path + url.search))}`);
    if (studioEntry) return redirect('/admin/apps/blog.html');
    if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, { status: 405, headers: { ...headers, allow: 'GET, HEAD' } });
    return new Response(request.method === 'HEAD' ? null : asset.body, { headers: { ...headers, 'content-type': asset.type, 'x-content-type-options': 'nosniff' } });
  }
  if (isLogin && request.method === 'GET') {
    const next = safeNext(url.searchParams.get('next'));
    if (validSession(request, env)) return redirect(next);
    return new Response(loginPage(next), { headers: { ...headers, 'content-type': 'text/html; charset=utf-8' } });
  }
  if (isLogout && request.method === 'GET') {
    return new Response(loginPage('/admin', '', true), { headers: { ...headers, 'content-type': 'text/html; charset=utf-8' } });
  }
  if (isPing) {
    if (!validSession(request, env)) return json({ error: 'Authentication required' }, 401);
    if (request.method !== 'GET') return new Response(null, { status: 405, headers: { ...headers, allow: 'GET' } });
    const images = imageConfiguration(env);
    return json({ ok: true, connectionVerified: false, now: new Date().toISOString(), env: {
      hasColorme: Boolean(env.COLORME_ACCESS_TOKEN),
      hasAnthropic: Boolean(env.ANTHROPIC_API_KEY),
      hasOpenAI: Boolean(env.OPENAI_API_KEY),
      hasR2: images.storageConfigured,
      imageGenerationConfigured: images.generationConfigured,
    }, snsCreds: {
      xConfigured: Boolean(env.X_API_KEY && env.X_API_SECRET && env.X_ACCESS_TOKEN && env.X_ACCESS_TOKEN_SECRET),
      threadsConfigured: Boolean(env.THREADS_USER_ID && env.THREADS_ACCESS_TOKEN),
    } });
  }
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...headers, allow: 'POST' } });
  if (request.headers.get('origin') !== url.origin) return json({ error: 'Origin rejected' }, 403);
  if (isLogout) return redirect('/admin/login', cookie('', 0));
  // One shared admin identity; neither attacker-chosen usernames nor passwords
  // may generate fresh rate-limit buckets. The binding is location-local.
  try {
    const result = await env.ADMIN_LOGIN_LIMITER.limit({ key: 'admin-login' });
    if (result?.success === false) return Response.json({ error: 'Too many login attempts' }, {
      status: 429, headers: { ...headers, 'retry-after': '60' },
    });
    if (result?.success !== true) return json({ error: 'Login protection unavailable' }, 503);
  } catch {
    return json({ error: 'Login protection unavailable' }, 503);
  }
  const form = await readForm(request);
  if (!form) return json({ error: 'Invalid or oversized login form' }, 400);
  if (!equal(form.get('password') || '', env.ADMIN_PASS)) return new Response(
    loginPage(safeNext(form.get('next')), 'パスワードが違います。もう一度入力してください。'),
    { status: 401, headers: { ...headers, 'content-type': 'text/html; charset=utf-8' } },
  );
  const expiry = Date.now() + MAX_AGE * 1000;
  return redirect(safeNext(form.get('next')), cookie(`${expiry}.${sign(expiry, env)}`, MAX_AGE));
}
