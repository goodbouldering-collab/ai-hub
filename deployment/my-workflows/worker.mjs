import published from '../ai-news/published-worker.mjs';
import assets from './admin-assets.generated.mjs';
import { createNativeContentProxy } from './native-content-proxy.mjs';

// Authorize through the unchanged published application, preserving its session rules.
async function authorized(request, env, ctx) {
  const url = new URL('/api/admin/ping', request.url);
  const check = await published.fetch(new Request(url, { headers: request.headers }), env, ctx);
  const body = await check.json().catch(() => null);
  return check.status === 200 && body?.ok === true;
}

export default {
  async fetch(request, env, ctx) {
    const path = new URL(request.url).pathname;
    if (path.startsWith('/api/content-studio/')) {
      return createNativeContentProxy({
        profileId: 'ai-hub', clientOrigin: 'https://aiclimb.aiclimb.workers.dev',
        authorize: (req, bindings) => authorized(req, bindings, ctx),
        secret: bindings => bindings.ADMIN_SESSION_SECRET,
        serverKey: bindings => bindings.OPENAI_API_KEY || '',
      })(request, env);
    }
    if (Object.hasOwn(assets, path)) {
      if (!await authorized(request, env, ctx)) {
        return new Response(null, { status: 303, headers: { location: '/admin/login?next=' + encodeURIComponent(path), 'cache-control': 'no-store' } });
      }
      if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, { status: 405 });
      return new Response(request.method === 'HEAD' ? null : assets[path].body, { headers: {
        'content-type': assets[path].type, 'cache-control': 'private, no-store',
        'x-content-type-options': 'nosniff', 'x-robots-tag': 'noindex, nofollow',
      } });
    }
    return published.fetch(request, env, ctx);
  },
};
