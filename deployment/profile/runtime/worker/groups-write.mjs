const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status) => Response.json(body, { status, headers });

export async function readUpdate(request) {
  if ((request.headers.get('content-type') || '').split(';')[0].trim() !== 'application/json') return { error: 415 };
  const reader = request.body?.getReader();
  if (!reader) return { error: 400 };
  const chunks = [];
  let length = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      length += value.byteLength;
      if (length > 1024 * 1024) { await reader.cancel(); return { error: 413 }; }
      chunks.push(value);
    }
    const bytes = new Uint8Array(length);
    let offset = 0;
    for (const value of chunks) { bytes.set(value, offset); offset += value.byteLength; }
    return { body: JSON.parse(new TextDecoder().decode(bytes)) };
  } catch { return { error: 400 }; }
  finally { reader.releaseLock(); }
}

// Called only after session verification. Never retry a write of uncertain outcome.
export async function updateGroup(request, env) {
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid or oversized update body' }, error);
  if (!body || typeof body !== 'object' || Array.isArray(body) || !/^[1-9]\d*$/.test(String(body.id)) || !Number.isSafeInteger(Number(body.id))) return json({ error: 'Invalid article id' }, 400);
  const group = {};
  for (const name of ['name', 'image_url', 'expl', 'display_state', 'sort']) {
    if (Object.hasOwn(body, name)) group[name] = body[name];
  }
  if (!Object.keys(group).length) return json({ error: 'No article fields to update' }, 400);
  if (Object.hasOwn(group, 'name') && (typeof group.name !== 'string' || !group.name.trim())) return json({ error: 'Invalid title' }, 400);
  if (Object.hasOwn(group, 'expl') && typeof group.expl !== 'string') return json({ error: 'Invalid article body' }, 400);
  if (Object.hasOwn(group, 'display_state') && !['hidden', 'showing'].includes(group.display_state)) return json({ error: 'Invalid display state' }, 400);
  if (Object.hasOwn(group, 'sort') && (!Number.isSafeInteger(group.sort) || group.sort < 0)) return json({ error: 'Invalid sort value' }, 400);
  if (Object.hasOwn(group, 'image_url')) {
    if (typeof group.image_url !== 'string') return json({ error: 'Invalid image URL' }, 400);
    if (group.image_url) {
      try { if (new URL(group.image_url).protocol !== 'https:') throw Error(); }
      catch { return json({ error: 'Image URL must use HTTPS' }, 400); }
    }
  }
  if (!env.COLORME_ACCESS_TOKEN) return json({ error: 'Article provider is not configured' }, 503);
  try {
    const response = await fetch(`https://api.shop-pro.jp/v1/groups/${body.id}`, {
      method: 'PUT', redirect: 'manual', signal: AbortSignal.timeout(15000),
      headers: { Authorization: `Bearer ${env.COLORME_ACCESS_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ group }),
    });
    if (!response.ok) throw Error();
    const data = await response.json();
    if (!data?.group || Number(data.group.id) !== Number(body.id)) throw Error();
    return json(data, 200);
  } catch {
    return json({ error: '更新結果を確認できません。再保存する前に記事を再取得してください。', status: 'write_outcome_unknown' }, 502);
  }
}
