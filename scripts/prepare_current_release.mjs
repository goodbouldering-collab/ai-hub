import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

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
  const updated = card.replace(/\/img\/portfolio\/minanowa\.jpg(?:\?v=[^']*)?'/, "/img/portfolio/minanowa.jpg?v=20261117-v4'")
    .replace("<span class='pf-chip'>Vercel</span><span class='pf-chip'>Supabase</span>", "<span class='pf-chip'>Cloudflare Workers</span><span class='pf-chip'>D1</span><span class='pf-chip'>R2</span>");
  if (!updated.includes('minanowa.jpg?v=20261117-v4') || !updated.includes("<span class='pf-chip'>R2</span>")) throw Error('Unexpected portfolio markup');
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
export const newsInputs = [
  'core', 'config', 'site/templates/ai-news', 'scripts/build_ai_news_feature.py',
  'scripts/build_search_presence_release.py', 'scripts/verify_ai_news_feature.py',
  'content/daily-ai-news.json', 'content/ai-news', 'site/static/brand/brand.css',
  'site/static/img/portfolio',
  'site/static/design-system/studio/focused-ux.js',
  'deployment/meo-diagnosis/published-worker.mjs', 'deployment/current-release.json',
];
const pythonExecutable = () => process.env.PYTHON_EXECUTABLE || process.env.PYTHON || 'python';
export async function snapshotCommittedSource(root, directory, sha, run = execFileAsync) {
  const archive = path.join(directory, 'source.zip');
  const source = path.join(directory, 'source');
  await run('git', ['archive', '--format=zip', '--output', archive, sha, '--', ...newsInputs], { cwd: root });
  // Do not extract links or paths outside the new source directory, even if an
  // unexpected entry is introduced into a future committed archive.
  await run(pythonExecutable(), ['-c', `
import pathlib, stat, sys, zipfile
root = pathlib.Path(sys.argv[2]).resolve()
root.mkdir(exist_ok=False)
with zipfile.ZipFile(sys.argv[1]) as archive:
    for item in archive.infolist():
        name = pathlib.PurePosixPath(item.filename)
        if name.is_absolute() or '..' in name.parts or chr(92) in item.filename or ':' in item.filename:
            raise ValueError('Unsafe archive path: ' + item.filename)
        mode = item.external_attr >> 16
        if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ValueError('Unsupported archive entry: ' + item.filename)
        target = (root / item.filename).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Archive path escaped source')
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(archive.read(item))
`, archive, source], { cwd: root });
  return source;
}
export async function prepare(root, { checkLive = true, request = fetch, run = execFileAsync, workingTree = false } = {}) {
  if (workingTree && checkLive) throw Error('Working-tree candidates require checkLive=false; never use them for deployment');
  let contract = JSON.parse(await fs.readFile(path.join(root, 'deployment/current-release.json'), 'utf8'));
  let sourceSha;
  if (contract.aiNews === true && !workingTree) {
    sourceSha = (await run('git', ['rev-parse', 'HEAD'], { cwd: root })).stdout.trim();
    contract = JSON.parse((await run('git', ['show', `${sourceSha}:deployment/current-release.json`], { cwd: root, maxBuffer: 10 * 1024 * 1024 })).stdout);
    if (contract.aiNews !== true) throw Error('Commit the daily release contract before preparing deployment');
  }
  const baseline = path.join(root, contract.baselineDirectory);
  const output = path.join(root, '.current-release/public');
  assertManifest(await hashes(baseline), contract.baselineAssets);
  let temporary;
  try {
    let home, photo, candidate;
    let generated = baseline;
    let source = root;
    if (contract.aiNews === true) {
      temporary = await fs.mkdtemp(path.join(root, '.current-release-build-'));
      if (!workingTree) source = await snapshotCommittedSource(root, temporary, sourceSha, run);
      generated = path.join(temporary, 'public');
    }
    const worker = await fs.readFile(path.join(source, 'deployment/meo-diagnosis/published-worker.mjs'));
    // Git uses LF while an existing Windows checkout can use CRLF.
    if (hash(worker.toString('utf8').replaceAll('\r\n', '\n')) !== contract.workerSha256) throw Error('Worker changed; rebase release contract');
    if (contract.aiNews === true) {
      await run(pythonExecutable(), [
        path.join(source, 'scripts/build_ai_news_feature.py'),
        '--base-assets', baseline, '--output', generated, '--preserve-baseline-presentation',
      ], { cwd: source, maxBuffer: 10 * 1024 * 1024 });
      // Only replace portfolio files whose content changed in this release.
      // Other images stay byte-identical to the verified production baseline.
      for (const [name, digest] of Object.entries(contract.assets)) {
        if (/^img\/portfolio\/(?:[a-z0-9-]+\.jpg|manifest\.json)$/.test(name)
          && digest !== contract.baselineAssets[name]) {
          const input = path.join(source, 'site/static', name);
          const target = path.join(generated, name);
          if (name.endsWith('.json')) {
            await fs.writeFile(target, (await fs.readFile(input, 'utf8')).replaceAll('\r\n', '\n'));
          } else {
            await fs.copyFile(input, target);
          }
        }
      }
      candidate = await hashes(generated);
    } else {
      home = Buffer.from(patchPortfolio(await fs.readFile(path.join(baseline, 'index.html'), 'utf8')));
      photo = await fs.readFile(path.join(root, 'site/static/img/portfolio/minanowa.jpg'));
      candidate = { ...contract.baselineAssets, 'index.html': hash(home), 'img/portfolio/minanowa.jpg': hash(photo) };
    }
    // Validate every generated byte before accepting production or touching output.
    assertManifest(candidate, contract.assets);
    if (checkLive) await assertLive(contract, request);
    if (sourceSha && (await run('git', ['rev-parse', 'HEAD'], { cwd: root })).stdout.trim() !== sourceSha) {
      throw Error('HEAD advanced during release preparation');
    }
    try { assertManifest(await hashes(output), contract.assets); }
    catch (error) {
      if (error.code !== 'ENOENT') throw error;
      await fs.mkdir(output, { recursive: true });
      await fs.cp(generated, output, { recursive: true });
      if (contract.aiNews !== true) {
        await fs.writeFile(path.join(output, 'index.html'), home);
        await fs.writeFile(path.join(output, 'img/portfolio/minanowa.jpg'), photo);
      }
    }
    assertManifest(await hashes(output), contract.assets);
    const changed = Object.keys(candidate).filter(name => candidate[name] !== contract.baselineAssets[name]);
    console.log(JSON.stringify({ assets: Object.keys(candidate).length, changed, liveChecked: checkLive, workerSha256: contract.workerSha256, sourceSha, workingTree }));
  } finally {
    if (temporary) {
      if (path.dirname(path.resolve(temporary)) !== path.resolve(root)) throw Error('Temporary release directory escaped root');
      await fs.rm(temporary, { recursive: true, force: true });
    }
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const workingTree = process.argv.includes('--candidate-working-tree');
  await prepare(path.resolve(import.meta.dirname, '..'), { workingTree, checkLive: !workingTree });
}
