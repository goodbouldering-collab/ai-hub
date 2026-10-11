import { createCipheriv,createDecipheriv,randomBytes,timingSafeEqual,createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir,readFile,writeFile,lstat } from 'node:fs/promises';
import { resolve,join } from 'node:path';
import { snapshotId } from './auxiliary-encrypted-source.mjs';

export const VAULT_DIRECTORY=resolve('C:/Project/AI相談/tmp/auxiliary-transfer-v1');
const FORMAT='ai-hub-auxiliary-encrypted-transfer-v1';
const fail=()=>new Error('AI Hub auxiliary encrypted vault operation failed; no plaintext output is available');
export function dpapi(bytes,reverse=false) {
  if(process.platform!=='win32'||!Buffer.isBuffer(bytes))throw fail();
  const code=`Add-Type -AssemblyName System.Security; $b=[Convert]::FromBase64String([Console]::In.ReadToEnd()); $r=[Security.Cryptography.ProtectedData]::${reverse?'Unprotect':'Protect'}($b,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser); [Console]::Out.Write([Convert]::ToBase64String($r))`;
  const result=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',code],{input:bytes.toString('base64'),encoding:'utf8',windowsHide:true,maxBuffer:2_000_000});
  if(result.status!==0||!result.stdout.trim())throw fail();
  return Buffer.from(result.stdout.trim(),'base64');
}
function keyBytes(key) {if(!Buffer.isBuffer(key)||key.length!==32)throw fail();return key;}
export function encryptBackup(value,key) {
  keyBytes(key);const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key,iv);
  const plain=Buffer.from(JSON.stringify(value));
  try {cipher.setAAD(Buffer.from(FORMAT));return {format:FORMAT,iv:iv.toString('base64'),ciphertext:Buffer.concat([cipher.update(plain),cipher.final()]).toString('base64'),tag:cipher.getAuthTag().toString('base64')};}
  finally {plain.fill(0);}
}
export function decryptBackup(value,key) {
  let plain;
  try {
    keyBytes(key);if(value.format!==FORMAT)throw fail();
    const decode=text=>{if(typeof text!=='string'||text.length>40_000_000)throw fail();const b=Buffer.from(text,'base64');if(b.toString('base64')!==text)throw fail();return b;};
    const iv=decode(value.iv),tag=decode(value.tag),ciphertext=decode(value.ciphertext);
    if(iv.length!==12||tag.length!==16)throw fail();
    const cipher=createDecipheriv('aes-256-gcm',key,iv);cipher.setAAD(Buffer.from(FORMAT));cipher.setAuthTag(tag);
    plain=Buffer.concat([cipher.update(ciphertext),cipher.final()]);return JSON.parse(plain.toString('utf8'));
  } catch {throw fail();} finally {plain?.fill(0);}
}
export async function writeVerifiedBackup(path,value,key) {
  try {
    const encrypted=encryptBackup(value,key);
    await writeFile(path,JSON.stringify(encrypted)+'\n',{flag:'wx',mode:0o600});
    const restored=decryptBackup(JSON.parse(await readFile(path,'utf8')),key);
    const a=Buffer.from(JSON.stringify(value)),b=Buffer.from(JSON.stringify(restored));
    try {if(a.length!==b.length||!timingSafeEqual(a,b))throw fail();} finally {a.fill(0);b.fill(0);}
    return {verified:true,ciphertextSha256:createHash('sha256').update(JSON.stringify(encrypted)).digest('hex')};
  } catch {throw fail();}
}
const unixPath=p=>p.replaceAll('\\','/').replace(/^([A-Za-z]):/,(_,d)=>'/'+d.toLowerCase());
function gpg(directory,args,input) {
  const result=spawnSync('C:/Program Files/Git/usr/bin/gpg.exe',['--homedir',unixPath(join(directory,'gnupg')),'--batch','--no-tty',...args.map(a=>/^[A-Za-z]:[\\/]/.test(a)?unixPath(a):a)],{input,windowsHide:true,maxBuffer:25_000_000});
  if(result.status!==0)throw fail();return result.stdout;
}
export async function initializeVault(directory=VAULT_DIRECTORY) {
  // mkdir without recursive makes an existing/partial vault a hard stop. It is
  // never silently rekeyed. The caller may inspect and explicitly resume it.
  await mkdir(directory,{mode:0o700});await mkdir(join(directory,'gnupg'),{mode:0o700});
  const pass=Buffer.from(randomBytes(32).toString('base64'));
  const bundle=Buffer.from(JSON.stringify({format:FORMAT,backupKey:randomBytes(32).toString('base64'),pgpPassphrase:pass.toString()}));
  try {
    await writeFile(join(directory,'keys.dpapi'),dpapi(bundle),{flag:'wx',mode:0o600});
    const withPass=args=>gpg(directory,['--pinentry-mode','loopback','--passphrase-fd','0',...args],Buffer.concat([pass,Buffer.from('\n')]));
    withPass(['--quick-generate-key','AI Hub auxiliary migration <migration@example.invalid>','rsa3072','sign','1y']);
    const fingerprint=gpg(directory,['--with-colons','--list-keys']).toString().split('\n').find(l=>l.startsWith('fpr:'))?.split(':')[9];
    if(!/^[A-F0-9]{40}$/.test(fingerprint??''))throw fail();
    withPass(['--quick-add-key',fingerprint,'rsa3072','encr','1y']);
    await writeFile(join(directory,'public.asc'),gpg(directory,['--armor','--export',fingerprint]),{flag:'wx'});
    return {format:FORMAT,keyProtection:'Windows CurrentUser DPAPI; encrypted OpenPGP private key',fingerprint};
  } finally {pass.fill(0);bundle.fill(0);}
}
export async function openVault(directory=VAULT_DIRECTORY) {
  if((await lstat(directory)).isSymbolicLink()||(await lstat(join(directory,'keys.dpapi'))).isSymbolicLink())throw fail();
  const raw=dpapi(await readFile(join(directory,'keys.dpapi')),true);
  let keys;try{keys=JSON.parse(raw.toString());if(keys.format!==FORMAT)throw fail();}finally{raw.fill(0);}
  const backupKey=Buffer.from(keys.backupKey,'base64');keyBytes(backupKey);
  const file=(id,suffix)=>join(directory,`${snapshotId(id)}.${suffix}`);
  return {
    async decryptSource(id) {
      const pass=Buffer.from(keys.pgpPassphrase+'\n');
      try{return gpg(directory,['--pinentry-mode','loopback','--passphrase-fd','0','--decrypt',file(id,'pgp')],pass);}finally{pass.fill(0);}
    },
    async write(id,value) {return writeVerifiedBackup(file(id,'aes256gcm.json'),value,backupKey);},
    async read(id) {return decryptBackup(JSON.parse(await readFile(file(id,'aes256gcm.json'),'utf8')),backupKey);},
    close() {backupKey.fill(0);keys={};},
  };
}

// Only synthetic bytes are accepted by this explicit OS round-trip helper.
export async function probeVault(directory) {
  await initializeVault(directory);
  const publicKey=await readFile(join(directory,'public.asc'),'utf8');
  const listing=gpg(directory,['--with-colons','--list-keys']).toString();
  const fingerprint=listing.split('\n').find(l=>l.startsWith('fpr:')).split(':')[9];
  const fixture=Buffer.from('ai-hub-auxiliary-synthetic-os-vault-probe');
  await writeFile(join(directory,'synthetic.pgp'),gpg(directory,['--trust-model','always','--recipient',fingerprint,'--encrypt'],fixture),{flag:'wx'});
  const vault=await openVault(directory);
  try {
    const restored=await vault.decryptSource('synthetic');try{if(!restored.equals(fixture))throw fail();}finally{restored.fill(0);}
    await vault.write('synthetic',{format:'synthetic-only',text:'no production credential'});
    if((await vault.read('synthetic')).format!=='synthetic-only')throw fail();
    return {syntheticOnly:true,openPgpRoundtrip:true,dpapiRoundtrip:true,backupReadback:true,publicKey};
  } finally {vault.close();fixture.fill(0);}
}
