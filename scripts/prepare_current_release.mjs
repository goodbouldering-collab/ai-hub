import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const hash = value => createHash('sha256').update(value).digest('hex');
export async function hashes(directory) {
  const files = (await fs.readdir(directory, { recursive: true, withFileTypes: true })).filter(x => x.isFile());
  const result = {};
  for (const file of files) {
    const full = path.join(file.parentPath, file.name);
    result[path.relative(directory, full).replaceAll('\\', '/')] = hash(await fs.readFile(full));
  }
  return result;
}
export function assertManifest(actual, expected) {
  const names = [...new Set([...Object.keys(actual), ...Object.keys(expected)])];
  const changed = names.filter(name => actual[name] !== expected[name]);
  if (changed.length) throw Error(`Unverified release assets: ${changed.join(', ')}`);
}
export function patchPortfolio(html) {
  const pattern = /<a class='pf-card'[^>]*href='https:\/\/minnanowa.net'[^>]*>.*?<\/a>/gs;
  const cards = html.match(pattern);
  if (cards?.length !== 1) throw Error('Expected exactly one minanowa card');
  const card = cards[0];
  const updated = card.replace(/\/img\/portfolio\/minanowa\.jpg(?:\?v=[^']*)?'/, "/img/portfolio/minanowa.jpg?v=20261115-scenes'")
    .replace("<span class='pf-chip'>Vercel</span><span class='pf-chip'>Supabase</span>", "<span class='pf-chip'>Cloudflare Workers</span><span class='pf-chip'>D1</span><span class='pf-chip'>R2</span>");
  if (!updated.includes('minanowa.jpg?v=20261115-scenes') || !updated.includes("<span class='pf-chip'>R2</span>")) throw Error('Unexpected portfolio markup');
  return html.replace(card, updated);
}
export async function assertLive(contract, request = fetch) {
  // Accept the verified predecessor or this exact release. A subsequent daily
  // publication requires rebasing the contract instead of silently rolling back.
  for (const name of contract.livePaths) {
    const url = new URL(name === 'index.html' ? '/' : `/${name}`, contract.url);
    const response = await request(url, { cache: 'no-store', signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw Error(`Production unavailable: ${url} (${response.status})`);
    const digest = hash(Buffer.from(await response.arrayBuffer()));
    if (![contract.baselineAssets[name], contract.assets[name]].includes(digest)) {
      throw Error(`Production advanced: ${name}. Rebase the release before deploying.`);
    }
  }
}
export async function prepare(root, { checkLive = true } = {}) {
  const contract = JSON.parse(await fs.readFile(path.join(root, 'deployment/current-release.json'), 'utf8'));
  const baseline = path.join(root, contract.baselineDirectory);
  const output = path.join(root, '.current-release/public');
  assertManifest(await hashes(baseline), contract.baselineAssets);
  const worker = await fs.readFile(path.join(root, 'deployment/meo-diagnosis/published-worker.mjs'));
  // Git uses LF while an existing Windows checkout can use CRLF.
  if (hash(worker.toString('utf8').replaceAll('\r\n', '\n')) !== contract.workerSha256) throw Error('Worker changed; rebase release contract');
  const home = Buffer.from(patchPortfolio(await fs.readFile(path.join(baseline, 'index.html'), 'utf8')));
  const photo = await fs.readFile(path.join(root, 'site/static/img/portfolio/minanowa.jpg'));
  const candidate = { ...contract.baselineAssets, 'index.html': hash(home), 'img/portfolio/minanowa.jpg': hash(photo) };
  assertManifest(candidate, contract.assets);
  if (checkLive) await assertLive(contract);
  try { assertManifest(await hashes(output), contract.assets); }
  catch (error) {
    if (error.code !== 'ENOENT') throw error;
    await fs.mkdir(output, { recursive: true });
    await fs.cp(baseline, output, { recursive: true });
    await fs.writeFile(path.join(output, 'index.html'), home);
    await fs.writeFile(path.join(output, 'img/portfolio/minanowa.jpg'), photo);
  }
  assertManifest(await hashes(output), contract.assets);
  console.log(JSON.stringify({ assets: Object.keys(candidate).length, changed: ['index.html', 'img/portfolio/minanowa.jpg'], liveChecked: checkLive, workerSha256: contract.workerSha256 }));
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await prepare(path.resolve(import.meta.dirname, '..'));
}
