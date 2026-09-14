import { createHash, randomUUID } from 'node:crypto';
import { Buffer } from 'node:buffer';
import { readUpdate } from './groups-write.mjs';
const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status) => Response.json(body, { status, headers });
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const MAX_RESPONSE_BYTES = 13 * 1024 * 1024;
async function readImageResponse(response) {
  if (Number(response.headers.get('content-length')) > MAX_RESPONSE_BYTES) {
    await response.body?.cancel();
    throw Error();
  }
  const reader = response.body?.getReader();
  if (!reader) throw Error();
  const chunks = []; let size = 0;
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_RESPONSE_BYTES) { await reader.cancel(); throw Error(); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
}

export function imageConfiguration(env) {
  let publicBase;
  try {
    publicBase = new URL(env.ARTICLE_IMAGES_PUBLIC_URL);
    if (publicBase.protocol !== 'https:' || publicBase.username || publicBase.password || publicBase.search || publicBase.hash) publicBase = undefined;
  } catch { publicBase = undefined; }
  const storageConfigured = Boolean(publicBase && typeof env.ARTICLE_IMAGES?.put === 'function' && typeof env.ARTICLE_IMAGES?.get === 'function');
  return { publicBase, storageConfigured, generationConfigured: Boolean(storageConfigured && env.OPENAI_API_KEY && env.AI_HUB_IMAGE_MODEL === 'gpt-image-2') };
}

export async function generateImage(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...headers, allow: 'POST' } });
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid image request' }, error);
  if (typeof body?.prompt !== 'string' || !body.prompt.trim()) return json({ error: 'Prompt is required' }, 400);
  const { publicBase, generationConfigured } = imageConfiguration(env);
  if (!generationConfigured) return json({ error: 'Image generation and storage are not configured' }, 503);
  let storedKey;
  try {
    const response = await fetch('https://api.openai.com/v1/images/generations', {
      method: 'POST', redirect: 'manual', signal: AbortSignal.timeout(120000),
      headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: env.AI_HUB_IMAGE_MODEL, prompt: body.prompt.trim(), n: 1, size: '1024x1024', output_format: 'png' }),
    });
    if (!response.ok) throw Error();
    const encoded = (await readImageResponse(response))?.data?.[0]?.b64_json;
    if (typeof encoded !== 'string' || encoded.length > 12 * 1024 * 1024 || !/^[A-Za-z0-9+/]+={0,2}$/.test(encoded)) throw Error();
    const bytes = Buffer.from(encoded, 'base64');
    if (bytes.length > 8 * 1024 * 1024 || bytes.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw Error();
    const hint = (typeof body.filenameHint === 'string' ? body.filenameHint : 'group').replace(/[^\w-]/g, '_').slice(0, 60) || 'group';
    const key = `colorme-groups/${randomUUID()}_${hint}.png`;
    const checksum = hash(bytes);
    storedKey = key;
    const saved = await env.ARTICLE_IMAGES.put(key, bytes, { httpMetadata: { contentType: 'image/png' }, sha256: checksum, onlyIf: { etagDoesNotMatch: '*' } });
    if (!saved) throw Error();
    const readback = await env.ARTICLE_IMAGES.get(key);
    if (!readback || hash(Buffer.from(await readback.arrayBuffer())) !== checksum) throw Error();
    return json({ url: `${publicBase.href.replace(/\/+$/, '')}/${key}` }, 200);
  } catch {
    // Keep any uncertain object for inspection; do not regenerate or delete automatically.
    return json({ error: storedKey ? '画像保存を確認できませんでした。再生成前に保存状態を確認してください。' : '画像生成を確認できませんでした。', status: storedKey ? 'storage_outcome_unknown' : 'generation_failed', ...(storedKey ? { storageKey: storedKey } : {}) }, 502);
  }
}
