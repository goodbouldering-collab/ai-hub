import { readGroups } from './groups.mjs';
import { readUpdate, updateGroup } from './groups-write.mjs';

const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status) => Response.json(body, { status, headers });
const validId = id => /^[1-9]\d*$/.test(String(id)) && Number.isSafeInteger(Number(id));

export async function reorderGroups(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...headers, allow: 'POST' } });
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid reorder body' }, error);
  const ids = body?.orderedIds;
  if (!validId(body?.parentId) || !Array.isArray(ids) || !ids.length || !ids.every(validId) || new Set(ids.map(Number)).size !== ids.length) return json({ error: 'Invalid or duplicate article IDs' }, 400);
  const url = new URL('/api/admin/groups', request.url);
  url.searchParams.set('parent', String(body.parentId));
  const listed = await readGroups(new Request(url), env);
  if (!listed.ok) return listed;
  const { groups } = await listed.json();
  const siblings = new Set(groups.map(group => Number(group.id)));
  if (groups.length !== ids.length || siblings.size !== ids.length || !ids.every(id => siblings.has(Number(id)))) return json({ error: '記事一覧が変わっています。再読み込みしてから並び替えてください。' }, 409);
  const results = [];
  for (let sort = 0; sort < ids.length; sort++) {
    const id = Number(ids[sort]);
    const update = new Request(request.url, { method: 'PUT', headers: request.headers, body: JSON.stringify({ id, sort }) });
    const result = await updateGroup(update, env);
    results.push({ id, sort, ok: result.ok });
    if (!result.ok) return json({ ok: false, results, status: 'write_outcome_unknown', error: '並び替えが途中で停止しました。記事一覧を再取得して状態を確認してください。' }, 502);
  }
  return json({ ok: true, results }, 200);
}
