/** Explicit read-only or live public validation; no cloud provisioning and no secret output. */
import {chromium} from '../frontend/node_modules/@playwright/test/index.mjs';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual} from 'node:util';
const root=fileURLToPath(new URL('../',import.meta.url));
const base=process.argv[2];const live=process.argv.includes('--live');
const selectedCase=process.argv.find(a=>a.startsWith('--case='))?.slice(7);
const retryWarning=process.argv.find(a=>a.startsWith('--retry-warning='))?.slice(16);
const caseIds=['market_claims_2025_09','market_ratio_2025_03'];
if(selectedCase&&!caseIds.includes(selectedCase))throw Error('Unknown case');
if(retryWarning&&(!selectedCase||!live))throw Error('Reviewed warning retry requires an explicit case and live mode');
if(!base||!/^https:\/\/[a-z0-9.-]+\.workers\.dev$/.test(base))throw Error('Supply the verified workers.dev HTTPS URL');
const out=root+'.local/cloudflare-production';mkdirSync(out,{recursive:true});
const secrets=[];
for(const file of ['.env','.local/railway/secrets.env']){
 for(const line of readFileSync(root+file,'utf8').split('\n')){const i=line.indexOf('=');const key=line.slice(0,i);const value=line.slice(i+1).trim().replace(/^['"]|['"]$/g,'');if(i>0&&/(_KEY|_TOKEN|_SECRET|_PASSWORD)$/.test(key)&&value.length>12)secrets.push(value);}
}
const scan=value=>{if(secrets.some(secret=>value.includes(secret)))throw Error('Secret exposure detected; details withheld');};
const assert=(value,message)=>{if(!value)throw Error(message);};
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext();const page=await context.newPage();const issues=[];const checks=[];const pending=[];
page.on('pageerror',()=>issues.push('PAGE_ERROR'));
page.on('console',msg=>{if(msg.type()==='error')issues.push('CONSOLE_ERROR');});
page.on('request',r=>{if(r.url().includes('.up.railway.app'))issues.push('DIRECT_BROWSER_BACKEND_REQUEST');scan(JSON.stringify(r.headers()));});
page.on('response',r=>{pending.push((async()=>{if(r.request().resourceType()==='image')return;try{scan(await r.text());}catch(e){if(String(e).includes('Secret exposure'))throw e;}})());});
try{
 const direct=await fetch('https://actuarial-signal-radar-api-production.up.railway.app/api/summary');assert(direct.status===401,'Railway must reject unauthenticated API access');
 for(const [path,kind] of [['/','overview'],['/?metric=claims&view=year&year=2020','2020-claims'],['/?metric=ratio&view=year&year=2020','2020-ratio'],['/?metric=claims&view=year&year=2025','2025-claims'],['/?metric=ratio&view=year&year=2025','2025-ratio'],['/?metric=claims&view=compare&years=2023,2024,2025,2026','compare']]){
  const started=Date.now();await page.goto(base+path);await page.locator('.stats-grid').waitFor();assert(await page.locator('.error').count()===0,'Dashboard API failed');
  if(kind==='overview'){assert((await page.locator('.human-intro').textContent()).includes('Honduras'),'Spanish intro missing');await page.locator('.technical-methodology summary').click();await page.locator('.technical-methodology[open]').waitFor();await page.getByRole('button',{name:'Change language'}).click();assert((await page.locator('.human-intro').textContent()).includes('Honduran'),'English switch failed');await page.getByRole('button',{name:'Change language'}).click();}
  if(kind.startsWith('2020'))assert((await page.locator('.year-summary').textContent()).includes('Sin puntuar'),'Unscored summary missing');
  checks.push({view:kind,seconds:(Date.now()-started)/1000});await page.screenshot({path:out+'/'+kind+'.png',fullPage:true});
 }
 const cases=[];
 for(const id of (selectedCase?[selectedCase]:caseIds)){
  const response=await page.request.get(base+'/api/cases/'+id);assert(response.ok(),'Case API failed');const data=await response.json();
  const pkg=JSON.parse(readFileSync(root+'data/processed/investigations/'+id+'.json','utf8'));
  for(const key of ['observed_value','expected_value','residual','relative_residual','raw_signal_level','adjusted_signal_level','report_date','availability_date'])assert(data.signal[key]===pkg[key],'Source value mismatch: '+key);
  await page.goto(base+'/cases/'+id);await page.locator('.case-human-lead').waitFor();await page.locator('.investigation-panel .status-tag').waitFor();
  const jobPath=base+'/api/investigations/'+id+'?language=es';let job=await (await page.request.get(jobPath)).json();let elapsed=null;
  if(live){
   assert(job.state==='NOT_STARTED'||(retryWarning&&job.state==='VALIDATION_WARNING'&&job.execution_id===retryWarning),'Refuses cached/already-started case; only an explicitly reviewed warning can be retried');
   if(retryWarning)console.log(JSON.stringify({event:'explicit_reviewed_warning_retry',case:id,previous_execution_id:retryWarning}));
   const started=Date.now();console.log(JSON.stringify({event:'starting_live_case',case:id}));await page.getByRole('button',{name:'Investigar señal',exact:false}).click();
   await page.locator('.investigation-panel [role="status"]').filter({hasText:'Investigación en curso'}).waitFor();
   while(Date.now()-started<420000){await page.waitForTimeout(3000);job=await(await page.request.get(jobPath)).json();if(!['NOT_STARTED','SUBMITTING','EVOLUS_RECEIVED'].includes(job.state))break;}
   elapsed=(Date.now()-started)/1000;console.log(JSON.stringify({event:'live_case_finished',case:id,state:job.state,seconds:elapsed}));
   assert(job.state==='COMPLETED','Investigation did not complete; do not resubmit automatically');
   assert(job.human_review_required===true&&job.provider==='amd_token_factory'&&job.model_name==='DeepSeek-V4-Flash','Provider/review contract mismatch');
   assert(job.knowledge_available===true&&job.validation_issue_count===0,'Knowledge or validation failed');
   for(const [key,value] of Object.entries(job.investigation.signal_snapshot))assert(isDeepStrictEqual(pkg[key],value),'Immutable signal changed');
   await page.locator('.result-sections').waitFor();scan(JSON.stringify(job));writeFileSync(out+'/'+id+'.public.json',JSON.stringify(job,null,2));
  }
  cases.push({case:id,state:job.state,fresh_execution:live,seconds:elapsed,human_review_required:job.human_review_required,provider:job.provider,model:job.model_name,execution_id:job.execution_id,...(retryWarning?{reviewed_warning_retry:retryWarning}:{})});
  writeFileSync(out+'/latest-case-receipts.json',JSON.stringify(cases,null,2));
  await page.screenshot({path:out+'/'+id+'.png',fullPage:true});
 }
 await page.setViewportSize({width:390,height:844});await page.goto(base);await page.locator('.stats-grid').waitFor();await page.waitForTimeout(500);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile overflow');
 await Promise.all(pending);assert(!issues.length,'Browser errors detected: '+issues.join(','));
 const result={base,live,checks,cases,browser_errors:issues,secret_scan:'PASS',direct_railway_unauthenticated:401};writeFileSync(out+'/public-validation.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{await browser.close();}
