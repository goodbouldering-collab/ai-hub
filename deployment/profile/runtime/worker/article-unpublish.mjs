import { replaceArticle } from './article-publish.mjs';
import { readUpdate, updateGroup } from './groups-write.mjs';
const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status) => Response.json(body, { status, headers });
const validId = id => /^[1-9]\d*$/.test(String(id)) && Number.isSafeInteger(Number(id));

export async function unpublishArticle(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...headers, allow: 'POST' } });
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid unpublish body' }, error);
  if (!body || !validId(body.groupId) || !['preview', 'live'].includes(body.target) || (Object.hasOwn(body, 'hideGroup') && typeof body.hideGroup !== 'boolean')) return json({ error: 'Invalid unpublish fields' }, 400);
  const templateId = body.target === 'live' ? env.COLORME_LIVE_TEMPLATE_ID : env.COLORME_PREVIEW_TEMPLATE_ID;
  if (!validId(templateId) || !env.COLORME_ACCESS_TOKEN || (body.target === 'preview' && Number(templateId) === Number(env.COLORME_LIVE_TEMPLATE_ID))) return json({ error: 'Template is not safely configured' }, 503);
  const endpoint = `https://api.shop-pro.jp/v1/templates/${templateId}/pages/product_list`;
  const call = async (method, payload) => {
    const response = await fetch(endpoint, { method, redirect: 'manual', signal: AbortSignal.timeout(15000), headers: { Authorization: `Bearer ${env.COLORME_ACCESS_TOKEN}`, 'Content-Type': 'application/json' }, ...(payload ? { body: JSON.stringify(payload) } : {}) });
    if (!response.ok) throw Error();
    return response.json();
  };
  let attempted = false;
  let templateVerified = false;
  try {
    const source = (await call('GET'))?.template_page?.html;
    if (typeof source !== 'string' || !source) throw Error();
    const next = replaceArticle(source, String(body.groupId), null);
    if ((await call('GET'))?.template_page?.html !== source) return json({ error: 'テンプレートが変更されました。再取得してください。' }, 409);
    if (next !== source) {
      attempted = true;
      await call('PUT', { template_page: { html: next } });
      if ((await call('GET'))?.template_page?.html !== next) throw Error();
    }
    templateVerified = true;
    if (body.target === 'live' && body.hideGroup !== false) {
      attempted = true;
      const hide = new Request(request.url, { method: 'PUT', headers: request.headers, body: JSON.stringify({ id: body.groupId, display_state: 'hidden' }) });
      if (!(await updateGroup(hide, env)).ok) throw Error();
    }
    return json({ ok: true, target: body.target, templateId: Number(templateId), pageType: 'product_list' }, 200);
  } catch (failure) {
    if (failure.message === 'markers') return json({ error: '記事マーカーが不正です。変更していません。' }, 409);
    return json({ ok: false, templateVerified, status: attempted ? 'write_outcome_unknown' : 'upstream_unavailable', error: '非公開化を確認できません。記事と表示状態を再取得してください。' }, 502);
  }
}
