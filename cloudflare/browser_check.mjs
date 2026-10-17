/** Browser errors, secret-leak scan and visual evidence; no POST/model execution. */
import {chromium} from '../.local/cloudflare/frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const output=new URL('../.local/cloudflare/',import.meta.url);
const browser=await chromium.launch({channel:'chrome',headless:true});
const errors=[],bodies=[];
const context=await browser.newContext();const page=await context.newPage();
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
page.on('response',async r=>{if(r.url().startsWith('http://127.0.0.1:8787/')&&/json|javascript|html/.test(r.headers()['content-type']||''))try{bodies.push(await r.text());}catch{}});
for(const [name,query] of [['historical',''],['claims-2020','?metric=claims&view=year&year=2020'],['ratio-2020','?metric=ratio&view=year&year=2020'],['compare','?metric=claims&view=compare&years=2023,2024,2025,2026'],['claims-case','cases/market_claims_2025_09'],['ratio-case','cases/market_ratio_2025_03']]){
 await page.goto('http://127.0.0.1:8787/'+query);await page.locator('.recharts-surface').first().waitFor();
 if(name.endsWith('-case')){
  const status=page.locator('.investigation-panel .status-tag');
  await status.filter({hasText:'COMPLETED'}).waitFor();
  if(!(await page.locator('.investigation-panel').innerText()).includes('HUMAN_REVIEW_REQUIRED'))throw Error('Missing human review');
  await page.getByRole('heading',{name:'Resumen ejecutivo',exact:true}).waitFor();
 }
 await page.screenshot({path:new URL(name+'.png',output).pathname,fullPage:true});
}
await page.setViewportSize({width:390,height:844});await page.waitForTimeout(500);
if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw Error('Mobile overflow');
await page.screenshot({path:new URL('mobile.png',output).pathname,fullPage:true});
// Compare known local secret values in memory; never print them or save them to evidence.
const env=fs.readFileSync(new URL('../.env',import.meta.url),'utf8');let leaked=false;
for(const line of env.split('\n')){const match=line.match(/^([A-Z_]*(?:API_KEY|TOKEN|PASSWORD))=(.+)$/);if(match){const value=match[2].trim().replace(/^['"]|['"]$/g,'');if(value.length>12&&bodies.some(body=>body.includes(value)))leaked=true;}}
const result={pages:6,console_errors:errors,secret_leak_detected:leaked,mobile_overflow:false};fs.writeFileSync(new URL('browser-review.json',output),JSON.stringify(result,null,2));
await browser.close();console.log(JSON.stringify({pages:6,console_error_count:errors.length,secret_leak_detected:leaked,mobile_overflow:false}));
if(errors.length||leaked)process.exit(1);
