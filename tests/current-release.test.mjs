import test from 'node:test';
import assert from 'node:assert/strict';
import { assertLive, assertManifest, hash, patchPortfolio } from '../scripts/prepare_current_release.mjs';

test('refuse missing, additional or changed baseline assets', () => {
  for (const actual of [{}, { a: 'x', b: 'y' }, { a: 'y' }]) assert.throws(() => assertManifest(actual, { a: 'x' }));
  assertManifest({ a: 'x' }, { a: 'x' });
});
test('block a newer live news article, accept previous and current release', async () => {
  const contract = { url: 'https://example.com', livePaths: ['ai-news/index.html'], baselineAssets: { 'ai-news/index.html': hash('before') }, assets: { 'ai-news/index.html': hash('after') } };
  for (const body of ['before', 'after']) await assertLive(contract, async () => new Response(body));
  await assert.rejects(assertLive(contract, async () => new Response('newer article')), /Production advanced/);
  await assert.rejects(assertLive(contract, async () => new Response('', { status: 503 })), /unavailable/);
});
test('change only the existing card, preserve unrelated news and avoid duplicates', () => {
  const card = "<a class='pf-card' href='https://minnanowa.net'><img src='/img/portfolio/minanowa.jpg'><span class='pf-chip'>Vercel</span><span class='pf-chip'>Supabase</span></a>";
  const result = patchPortfolio(`LATEST NEWS${card}OTHER CARDS`);
  assert.ok(result.startsWith('LATEST NEWS'));
  assert.ok(result.endsWith('OTHER CARDS'));
  assert.ok(result.includes('Cloudflare Workers'));
  assert.equal(patchPortfolio(result), result);
  assert.throws(() => patchPortfolio(card + card), /exactly one/);
  assert.throws(() => patchPortfolio('missing'), /exactly one/);
});
