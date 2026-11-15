import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { build } = require(process.env.AUX_ESBUILD_MODULE || 'esbuild');
const root = fileURLToPath(new URL('../', import.meta.url));

await build({
  absWorkingDir: root,
  entryPoints: ['deployment/admin-workspace/worker.mjs'],
  outfile: 'deployment/admin-workspace/published-worker.mjs',
  bundle: true,
  format: 'esm',
  platform: 'node',
  external: ['cloudflare:*'],
});
