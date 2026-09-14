import sanitizeHtml from 'sanitize-html';
import { readUpdate } from './groups-write.mjs';
import { SYSTEM_PROMPT } from './article-prompt.mjs';

const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status = 200) => Response.json(body, { status, headers });
function cleanDraft(value, includeSummary) {
  if (!value || typeof value.title !== 'string' || !value.title.trim() || typeof value.html !== 'string' || !value.html.trim()) throw Error();
  const html = sanitizeHtml(value.html, {
    allowedTags: ['h2', 'h3', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'b', 'i', 'br', 'a', 'small'],
    allowedAttributes: { a: ['href', 'rel'] }, allowedSchemes: ['https', 'http'], allowProtocolRelative: false,
    transformTags: { a: sanitizeHtml.simpleTransform('a', { rel: 'noopener noreferrer' }) },
  }).trim();
  if (!html) throw Error();
  return { title: value.title.trim(), html, ...(includeSummary ? { summary: typeof value.summary === 'string' ? value.summary.trim() : '' } : {}) };
}

export async function articleAI(request, env, revise) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...headers, allow: 'POST' } });
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid AI request body' }, error);
  const required = revise ? ['title', 'html', 'instruction'] : ['theme'];
  if (!body || required.some(key => typeof body[key] !== 'string' || !body[key].trim())) return json({ error: 'Required text is missing' }, 400);
  if (!env.ANTHROPIC_API_KEY) return json({ error: 'AI provider is not configured' }, 503);
  const count = Math.min(5, Math.max(1, Math.floor(Number(body.count) || 3)));
  const content = revise
    ? `現在のタイトル: ${body.title.trim()}\n現在の本文HTML:\n${body.html.trim()}\n\n修正指示: ${body.instruction.trim()}\n\n修正後を JSON {title, html} で返してください。`
    : `テーマ: ${body.theme.trim()}\n\n上記テーマで ${count} 案を JSON 配列 [{title,html,summary}, ...] で返してください。`;
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST', redirect: 'manual', signal: AbortSignal.timeout(55000),
      headers: { 'x-api-key': env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
      body: JSON.stringify({ model: env.AI_HUB_CLAUDE_MODEL || 'claude-sonnet-4-6', max_tokens: 4096, system: SYSTEM_PROMPT, messages: [{ role: 'user', content }] }),
    });
    if (!response.ok) throw Error();
    const message = await response.json();
    if (message.stop_reason === 'max_tokens' || !Array.isArray(message.content)) throw Error();
    const text = message.content.filter(block => block.type === 'text').map(block => block.text).join('\n').trim();
    const start = text.indexOf(revise ? '{' : '[');
    const end = text.lastIndexOf(revise ? '}' : ']');
    if (start < 0 || end < start) throw Error();
    const parsed = JSON.parse(text.slice(start, end + 1));
    if (revise) return json(cleanDraft(parsed, false));
    if (!Array.isArray(parsed) || !parsed.length || parsed.length > count) throw Error();
    return json({ drafts: parsed.map(draft => cleanDraft(draft, true)) });
  } catch (error) {
    const timeout = ['TimeoutError', 'AbortError'].includes(error?.name);
    return json({ error: timeout ? 'AI応答が制限時間を超えました。' : 'AI応答を確認できませんでした。' }, timeout ? 504 : 502);
  }
}
