// Colorme remains the article system of record. No Vercel intermediary.
export async function readGroups(request, env) {
  const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
  const json = (body, status = 200) => Response.json(body, { status, headers });
  if (request.method !== 'GET') return json({ error: 'Article writes are not migrated yet' }, 503);
  const query = new URL(request.url).searchParams;
  const top = Boolean(query.get('top'));
  const id = query.get('id');
  const parent = query.get('parent');
  if (!top && !/^\d+$/.test(id || parent || '')) return json({ error: 'A numeric parent or id, or top=1, is required' }, 400);
  if (!env.COLORME_ACCESS_TOKEN) return json({ error: 'Article provider is not configured' }, 503);
  const detail = !top && Boolean(id);
  const path = detail ? `/v1/groups/${id}` : '/v1/groups?limit=1000&offset=0';
  try {
    const response = await fetch(`https://api.shop-pro.jp${path}`, {
      method: 'GET', redirect: 'manual', signal: AbortSignal.timeout(15000),
      headers: { Authorization: `Bearer ${env.COLORME_ACCESS_TOKEN}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) return json({ error: 'Article provider request failed' }, 502);
    const data = await response.json();
    if (detail) {
      const group = data?.group ?? data;
      if (!group || typeof group !== 'object' || Array.isArray(group) || group.id == null) return json({ error: 'Invalid article response' }, 502);
      return json(group);
    }
    if (!Array.isArray(data?.groups)) return json({ error: 'Invalid article list response' }, 502);
    const groups = data.groups.filter(g => g && (top ? g.parent_group_id == null : Number(g.parent_group_id) === Number(parent)))
      .sort((a, b) => Number(a.sort ?? 0) - Number(b.sort ?? 0));
    return json({ groups });
  } catch {
    return json({ error: 'Article provider request failed' }, 502);
  }
}
