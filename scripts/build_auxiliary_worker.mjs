import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const require=createRequire(import.meta.url);
// Reuse an installed esbuild for constrained local checkouts; no download or install.
const {build,version}=require(process.env.AUX_ESBUILD_MODULE||'esbuild');
const root=fileURLToPath(new URL('../',import.meta.url));
await build({absWorkingDir:root,entryPoints:['deployment/admin-workspace/worker.mjs'],outfile:'deployment/admin-workspace/published-worker.mjs',bundle:true,format:'esm',platform:'node',target:'es2022',external:['cloudflare:*'],legalComments:'eof'});
console.log(JSON.stringify({esbuild:version,entry:'deployment/admin-workspace/worker.mjs',output:'deployment/admin-workspace/published-worker.mjs',publicAssetsChanged:0}));
