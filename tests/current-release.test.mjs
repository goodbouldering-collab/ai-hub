import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { assertLive, assertManifest, hash, hashes, patchPortfolio, prepare } from '../scripts/prepare_current_release.mjs';

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

async function releaseFixture(t, aiNews = true) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'ai-news-release-test-'));
  t.after(async () => {
    assert.equal(path.dirname(path.resolve(root)), path.resolve(os.tmpdir()));
    await fs.rm(root, { recursive: true, force: true });
  });
  const baseline = path.join(root, 'baseline');
  await fs.mkdir(path.join(baseline, 'img/portfolio'), { recursive: true });
  await fs.writeFile(path.join(baseline, 'index.html'), aiNews ? 'previous home' : "<a class='pf-card' href='https://minnanowa.net'><img src='/img/portfolio/minanowa.jpg'><span class='pf-chip'>Vercel</span><span class='pf-chip'>Supabase</span></a>");
  await fs.writeFile(path.join(baseline, 'img/portfolio/minanowa.jpg'), 'old photo');
  await fs.mkdir(path.join(root, 'deployment/meo-diagnosis'), { recursive: true });
  await fs.writeFile(path.join(root, 'deployment/meo-diagnosis/published-worker.mjs'), 'worker\r\n');
  const baselineAssets = await hashes(baseline);
  const home = aiNews ? 'new daily home' : patchPortfolio(await fs.readFile(path.join(baseline, 'index.html'), 'utf8'));
  const assets = { ...baselineAssets, 'index.html': hash(home) };
  if (!aiNews) {
    await fs.mkdir(path.join(root, 'site/static/img/portfolio'), { recursive: true });
    await fs.writeFile(path.join(root, 'site/static/img/portfolio/minanowa.jpg'), 'new photo');
    assets['img/portfolio/minanowa.jpg'] = hash('new photo');
  }
  const contract = { ...(aiNews ? { aiNews: true } : {}), baselineDirectory: 'baseline', baselineAssets, assets, workerSha256: hash('worker\n'), url: 'https://example.com', livePaths: ['index.html'] };
  await fs.writeFile(path.join(root, 'deployment/current-release.json'), JSON.stringify(contract));
  const run = async (executable, args, options) => {
    assert.equal(executable, process.env.PYTHON_EXECUTABLE || process.env.PYTHON || 'python');
    assert.equal(options.cwd, root);
    assert.equal(args[0], path.join(root, 'scripts/build_ai_news_feature.py'));
    assert.equal(args[1], '--base-assets');
    assert.equal(args[2], baseline);
    assert.equal(args[3], '--output');
    assert.equal(args[5], '--preserve-baseline-presentation');
    const generated = args[4];
    await assert.rejects(fs.access(generated), { code: 'ENOENT' });
    await fs.cp(baseline, generated, { recursive: true });
    await fs.writeFile(path.join(generated, 'index.html'), home);
    return { stdout: '{}' };
  };
  return { root, run, contract, output: path.join(root, '.current-release/public') };
}

test('daily mode builds from verified baseline, validates all files and is repeatable', async t => {
  const fixture = await releaseFixture(t);
  let requests = 0;
  const request = async () => { requests++; return new Response('previous home'); };
  await prepare(fixture.root, { run: fixture.run, request });
  await prepare(fixture.root, { run: fixture.run, request });
  assert.equal(requests, 2);
  assertManifest(await hashes(fixture.output), fixture.contract.assets);
  assert.ok(!(await fs.readdir(fixture.root)).some(name => name.startsWith('.current-release-build-')));
});

test('daily mode rejects unexpected generated assets before output or production checks', async t => {
  const fixture = await releaseFixture(t);
  const run = async (...args) => {
    await fixture.run(...args);
    await fs.writeFile(path.join(args[1][4], 'unrelated.txt'), 'unverified');
  };
  await assert.rejects(prepare(fixture.root, { run, request: () => assert.fail('must validate first') }), /Unverified release assets/);
  await assert.rejects(fs.access(fixture.output), { code: 'ENOENT' });
  assert.ok(!(await fs.readdir(fixture.root)).some(name => name.startsWith('.current-release-build-')));
});

test('daily mode blocks advanced production and preserves mismatching existing output', async t => {
  const fixture = await releaseFixture(t);
  await assert.rejects(prepare(fixture.root, { run: fixture.run, request: async () => new Response('newer release') }), /Production advanced/);
  await assert.rejects(fs.access(fixture.output), { code: 'ENOENT' });
  await fs.mkdir(fixture.output, { recursive: true });
  await fs.writeFile(path.join(fixture.output, 'index.html'), 'do not overwrite');
  const before = await hashes(fixture.output);
  await assert.rejects(prepare(fixture.root, { run: fixture.run, checkLive: false }), /Unverified release assets/);
  assert.deepEqual(await hashes(fixture.output), before);
});

test('contracts without aiNews keep the existing portfolio build and do not invoke Python', async t => {
  const fixture = await releaseFixture(t, false);
  await prepare(fixture.root, { checkLive: false, run: () => assert.fail('portfolio must not run Python') });
  assertManifest(await hashes(fixture.output), fixture.contract.assets);
});
