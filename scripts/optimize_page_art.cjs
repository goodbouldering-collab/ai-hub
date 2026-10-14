// Run with NODE_PATH pointing at the installed Sharp package directory.
// Only resize/encode generated originals. Do not change illustration content.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'config/page-art.json')));
async function main() {
  let count = 0, bytes = 0;
  for (const item of manifest.images.filter(i => i.mode === 'generate')) {
    const source = path.join(root, 'assets/paper-20261015/originals', item.key + '.png');
    if (!fs.existsSync(source)) continue;
    const target = path.join(root, 'site/static', item.target);
    fs.mkdirSync(path.dirname(target), {recursive:true});
    if (!fs.existsSync(target) || fs.statSync(source).mtimeMs > fs.statSync(target).mtimeMs) {
      await sharp(source).resize({width:1440, withoutEnlargement:true}).webp({quality:88, effort:6}).toFile(target);
    }
    count++; bytes += fs.statSync(target).size;
  }
  console.log(JSON.stringify({optimized:count, expected:manifest.images.filter(i=>i.mode==='generate').length, bytes}));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
