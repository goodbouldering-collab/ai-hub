import sanitizeHtml from 'sanitize-html';
import { readUpdate } from './groups-write.mjs';
const BEGIN = '<!-- BEGIN:AI_GROUP_ARTICLES -->';
const END = '<!-- END:AI_GROUP_ARTICLES -->';
const headers = { 'cache-control': 'no-store', 'x-aiclimb-delivery': 'cloudflare-worker' };
const json = (body, status) => Response.json(body, { status, headers });
const validId = id => /^[1-9]\d*$/.test(String(id)) && Number.isSafeInteger(Number(id));
const escape = text => text.replace(/[&<>"{}]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', '{': '&#123;', '}': '&#125;' })[char]);

export function replaceArticle(source, id, article) {
  let page = source;
  const begins = page.split(BEGIN).length - 1;
  const ends = page.split(END).length - 1;
  if (begins === 0 && ends === 0) {
    if (article === null) return source;
    const match = /<body[^>]*>/i.exec(page);
    const at = match ? match.index + match[0].length : 0;
    page = page.slice(0, at) + BEGIN + '\n' + END + page.slice(at);
  } else if (begins !== 1 || ends !== 1 || page.indexOf(END) < page.indexOf(BEGIN)) throw Error('markers');
  const start = page.indexOf(BEGIN) + BEGIN.length;
  const end = page.indexOf(END);
  let inner = page.slice(start, end);
  const seen = new Set();
  let open = null;
  for (const token of inner.matchAll(/<!-- (BEGIN|END):AI_GROUP_ARTICLE_([^ ]+) -->/g)) {
    if (token[1] === 'BEGIN') {
      if (open || seen.has(token[2])) throw Error('markers');
      open = token[2]; seen.add(open);
    } else {
      if (open !== token[2]) throw Error('markers');
      open = null;
    }
  }
  if (open) throw Error('markers');
  const begin = `<!-- BEGIN:AI_GROUP_ARTICLE_${id} -->`;
  const finish = `<!-- END:AI_GROUP_ARTICLE_${id} -->`;
  const wrapped = `${begin}\n${article}\n${finish}`;
  const articleStart = inner.indexOf(begin);
  if (article === null) {
    if (articleStart < 0) return source;
    inner = inner.slice(0, articleStart) + inner.slice(inner.indexOf(finish, articleStart) + finish.length);
    return page.slice(0, start) + inner + page.slice(end);
  }
  inner = articleStart < 0 ? `\n${wrapped}\n${inner}` : inner.slice(0, articleStart) + wrapped + inner.slice(inner.indexOf(finish, articleStart) + finish.length);
  return page.slice(0, start) + inner + page.slice(end);
}

export async function publishArticle(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...headers, allow: 'POST' } });
  if (request.headers.get('origin') !== new URL(request.url).origin) return json({ error: 'Origin rejected' }, 403);
  const { body, error } = await readUpdate(request);
  if (error) return json({ error: 'Invalid publication body' }, error);
  if (!body || !validId(body.groupId) || !validId(body.parentGroupId) || !['preview', 'live'].includes(body.target) || typeof body.title !== 'string' || !body.title.trim() || typeof body.html !== 'string' || !body.html.trim() || !/^\d{4}-\d{2}-\d{2}$/.test(body.publishedAt || '')) return json({ error: 'Invalid publication fields' }, 400);
  const templateId = body.target === 'live' ? env.COLORME_LIVE_TEMPLATE_ID : env.COLORME_PREVIEW_TEMPLATE_ID;
  if (!validId(templateId) || !env.COLORME_ACCESS_TOKEN || (body.target === 'preview' && Number(templateId) === Number(env.COLORME_LIVE_TEMPLATE_ID))) return json({ error: 'Publication template is not safely configured' }, 503);
  const html = sanitizeHtml(body.html, { allowedTags: ['h2','h3','p','ul','ol','li','strong','em','b','i','br','a','small'], allowedAttributes: { a: ['href'] }, allowedSchemes: ['https','http'], allowProtocolRelative: false }).replace(/[{}]/g, c => c === '{' ? '&#123;' : '&#125;');
  if (!html.trim()) return json({ error: 'Empty article HTML' }, 400);
  const article = `{if $smarty.get.mode == "grp" && $smarty.get.gid == ${Number(body.parentGroupId)}}\n<section class="ai-group-article" data-published="${body.publishedAt}">\n<h2>${escape(body.title.trim())}</h2>\n<p class="ai-group-article__date"><small>${body.publishedAt} 公開</small></p>\n${html}\n</section>\n{/if}`;
  const endpoint = `https://api.shop-pro.jp/v1/templates/${templateId}/pages/product_list`;
  const call = async (method, payload) => {
    const response = await fetch(endpoint, { method, redirect: 'manual', signal: AbortSignal.timeout(15000), headers: { Authorization: `Bearer ${env.COLORME_ACCESS_TOKEN}`, 'Content-Type': 'application/json' }, ...(payload ? { body: JSON.stringify(payload) } : {}) });
    if (!response.ok) throw Error('provider');
    return response.json();
  };
  let attempted = false;
  try {
    const source = (await call('GET'))?.template_page?.html;
    if (typeof source !== 'string' || !source) throw Error('provider');
    const next = replaceArticle(source, String(body.groupId), article);
    if ((await call('GET'))?.template_page?.html !== source) return json({ error: 'テンプレートが変更されました。再取得してください。' }, 409);
    attempted = true;
    await call('PUT', { template_page: { html: next } });
    if ((await call('GET'))?.template_page?.html !== next) throw Error('verify');
    return json({ ok: true, target: body.target, templateId: Number(templateId), pageType: 'product_list', blockSize: article.length, pageSize: next.length, liveUrl: `${(env.COLORME_SHOP_URL || 'https://goodbouldering.com').replace(/\/+$/, '')}/?mode=grp&gid=${Number(body.parentGroupId)}` }, 200);
  } catch (failure) {
    if (failure.message === 'markers') return json({ error: '記事マーカーが不正です。テンプレートを変更していません。' }, 409);
    return json({ error: attempted ? '公開結果が不明です。再公開前に表示を確認してください。' : '公開先を取得できませんでした。', status: attempted ? 'write_outcome_unknown' : 'upstream_unavailable' }, 502);
  }
}
