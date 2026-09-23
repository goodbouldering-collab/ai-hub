import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const sharp=createRequire(import.meta.url)(process.env.SHARP_MODULE || 'sharp');
const items=JSON.parse(await fs.readFile(process.argv[2] || 'docs/design/cyber-20260923-prompts.json','utf8'));
await fs.mkdir('docs/design/cyber-originals',{recursive:true});
for(const item of items){
 const source=item.path || path.join('docs/design',item.original);
 if(item.path) await fs.copyFile(source,`docs/design/cyber-originals/${item.name}.png`);
 await sharp(source).resize(1536,1024,{fit:'cover'}).webp({quality:84}).toFile(`site/static/design-system/studio/images/${item.name}.webp`);
}
await fs.writeFile('docs/design/cyber-20260923-prompts.json',JSON.stringify(items.map(({name,prompt})=>({name,prompt,mode:'built-in image_gen',original:`cyber-originals/${name}.png`})),null,2)+'\n');
const tiles=await Promise.all(items.map(async (item,i)=>({input:await sharp(`site/static/design-system/studio/images/${item.name}.webp`).resize(320,214).toBuffer(),left:(i%3)*320,top:Math.floor(i/3)*214})));
await sharp({create:{width:960,height:Math.ceil(items.length/3)*214,channels:3,background:'#f5f6fa'}}).composite(tiles).png().toFile('docs/design/cyber-20260923-contact-sheet.png');
console.log(`Imported ${items.length} distinct artworks`);
