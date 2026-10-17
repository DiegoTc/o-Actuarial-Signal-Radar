/** Publish only the staged production bundle, copying one existing secret without logging it. */
import {readFileSync,writeFileSync,mkdirSync,chmodSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const config=root+'.local/cloudflare/frontend/wrangler.jsonc';
const parsed=JSON.parse(readFileSync(config,'utf8'));
if(parsed.name!=='actuarial-signal-radar'||parsed.vars?.LOCAL_EXPERIMENT)throw Error('Build production configuration first');
const vars=Object.fromEntries(readFileSync(root+'.local/railway/secrets.env','utf8').split('\n').filter(s=>s.includes('=')).map(s=>{const i=s.indexOf('=');return [s.slice(0,i),s.slice(i+1).trim()];}));
const token=vars.DASHBOARD_BACKEND_TOKEN;
if(!token||!/^[A-Za-z0-9_-]{43,}$/.test(token))throw Error('Existing deployment token missing or invalid');
const dir=root+'.local/cloudflare-production';mkdirSync(dir,{recursive:true});
const file=dir+'/worker-secrets.json';writeFileSync(file,JSON.stringify({DASHBOARD_BACKEND_TOKEN:token}),{mode:0o600});chmodSync(file,0o600);
const result=spawnSync(process.execPath,[root+'cloudflare/node_modules/wrangler/bin/wrangler.js','deploy','--config',config,'--secrets-file',file],{cwd:root,stdio:'inherit',env:{...process.env,WRANGLER_SEND_METRICS:'false'}});
process.exit(result.status??1);
