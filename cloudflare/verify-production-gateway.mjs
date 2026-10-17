/** Read-only gateway-to-Railway contract check in Node; not proof of a hosted Worker. */
import {proxyApi} from './production-gateway.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const vars=Object.fromEntries(readFileSync(root+'.local/railway/secrets.env','utf8').split('\n').filter(s=>s.includes('=')).map(s=>{const i=s.indexOf('=');return [s.slice(0,i),s.slice(i+1).trim()];}));
const env={PUBLIC_BACKEND_URL:'https://actuarial-signal-radar-api-production.up.railway.app',DASHBOARD_BACKEND_TOKEN:vars.DASHBOARD_BACKEND_TOKEN};
const paths=['/api/summary','/api/cases','/api/cases/market_claims_2025_09','/api/cases/market_ratio_2025_03'];const checks=[];
for(const path of paths){
 const start=Date.now();const response=await proxyApi(new Request('https://frontend.example'+path),env);const text=await response.text();if(text.includes(env.DASHBOARD_BACKEND_TOKEN))throw Error('Secret exposure detected');
 if(response.status!==200)throw Error('Gateway read failed: '+response.status);
 const value=JSON.parse(text);
 if(path.startsWith('/api/cases/')){const id=path.split('/').at(-1);const pkg=JSON.parse(readFileSync(root+'data/processed/investigations/'+id+'.json','utf8'));for(const key of ['observed_value','expected_value','residual','raw_signal_level','adjusted_signal_level','availability_date'])if(value.signal[key]!==pkg[key])throw Error('Source mismatch: '+key);}
 checks.push({path,status:response.status,seconds:(Date.now()-start)/1000});
}
const direct=await fetch(env.PUBLIC_BACKEND_URL+'/api/summary');if(direct.status!==401)throw Error('Unauthenticated backend must reject requests');
const receipt={runtime:'Node transport check, not deployed Cloudflare',checks,unauthenticated_backend:401,secret_scan:'PASS'};
writeFileSync(root+'.local/cloudflare-production/gateway-contracts.json',JSON.stringify(receipt,null,2));console.log(JSON.stringify(receipt));
