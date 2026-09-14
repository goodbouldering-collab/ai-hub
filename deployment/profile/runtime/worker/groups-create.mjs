import { readGroups } from './groups.mjs';
import { readUpdate, updateGroup } from './groups-write.mjs';

const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status) => Response.json(body, { status, headers });
const validId = id => /^[1-9]\d*$/.test(String(id)) && Number.isSafeInteger(Number(id));

// Preserve the legacy front-insertion behavior, but stop at uncertain writes.
export async function createGroup(request, env) {
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid creation body' }, error);
  if (!body || typeof body.name !== 'string' || !body.name.trim() || !validId(body.parent_group_id)) return json({ error: 'Title and valid parent are required' }, 400);
  const group = { name: body.name.trim() };
  if (Object.hasOwn(body, 'expl')) {
    if (typeof body.expl !== 'string') return json({ error: 'Invalid article body' }, 400);
    group.expl = body.expl;
  }
  if (Object.hasOwn(body, 'image_url')) {
    if (typeof body.image_url !== 'string') return json({ error: 'Invalid image URL' }, 400);
    if (body.image_url) {
      try { if (new URL(body.image_url).protocol !== 'https:') throw Error(); }
      catch { return json({ error: 'Image URL must use HTTPS' }, 400); }
    }
    group.image_url = body.image_url;
  }
  group.display_state = body.display_state ?? 'hidden';
  if (!['hidden', 'showing'].includes(group.display_state)) return json({ error: 'Invalid display state' }, 400);
  group.parent_group_id = Number(body.parent_group_id);
  group.sort = 0;
  const listUrl = new URL('/api/admin/groups', request.url);
  listUrl.searchParams.set('parent', String(group.parent_group_id));
  const listed = await readGroups(new Request(listUrl), env);
  if (!listed.ok) return listed;
  const { groups } = await listed.json();
  if (!groups.every(g => validId(g.id) && Number.isSafeInteger(Number(g.sort ?? 0)) && Number(g.sort ?? 0) >= 0 && Number(g.sort ?? 0) < Number.MAX_SAFE_INTEGER)) return json({ error: 'Invalid existing article order' }, 502);
  const results = [];
  for (const sibling of groups) {
    const sort = Number(sibling.sort ?? 0) + 1;
    const update = new Request(request.url, { method: 'PUT', headers: request.headers, body: JSON.stringify({ id: sibling.id, sort }) });
    const result = await updateGroup(update, env);
    results.push({ id: sibling.id, sort, ok: result.ok });
    if (!result.ok) return json({ error: '並び順の変更中に停止しました。記事一覧を再取得してください。', status: 'write_outcome_unknown', creationAttempted: false, results }, 502);
  }
  try {
    const response = await fetch('https://api.shop-pro.jp/v1/groups', {
      method: 'POST', redirect: 'manual', signal: AbortSignal.timeout(15000),
      headers: { Authorization: `Bearer ${env.COLORME_ACCESS_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ group }),
    });
    if (!response.ok) throw Error();
    const created = await response.json();
    if (!validId(created?.group?.id)) throw Error();
    return json(created, 200);
  } catch {
    return json({ error: '作成結果が不明です。再作成せず記事一覧で確認してください。', status: 'write_outcome_unknown', creationAttempted: true, results }, 502);
  }
}
