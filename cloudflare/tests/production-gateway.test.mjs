import test from 'node:test';import assert from 'node:assert/strict';
import {proxyApi} from '../production-gateway.mjs';
const env={PUBLIC_BACKEND_URL:'https://actuarial-signal-radar-api-production.up.railway.app',DASHBOARD_BACKEND_TOKEN:'test-only-not-a-real-credential'};
const request=(path='/api/summary',init={})=>new Request('https://radar.example'+path,init);
test('fixed backend receives secret server-side; browser headers and upstream secrets are dropped',async()=>{
 const r=await proxyApi(request('/api/signals?metric=monthly_claims',{headers:{Authorization:'untrusted-browser',Cookie:'private'}}),env,async(url,init)=>{
  assert.equal(url,env.PUBLIC_BACKEND_URL+'/api/signals?metric=monthly_claims');assert.equal(init.headers.get('Authorization'),'Bearer '+env.DASHBOARD_BACKEND_TOKEN);assert.equal(init.headers.has('Cookie'),false);
  return Response.json({observed_value:185377003.67},{headers:{'Set-Cookie':'private','X-ApiKey':'secret'}});
 });
 assert.deepEqual(await r.json(),{observed_value:185377003.67});assert.equal(r.headers.has('Set-Cookie'),false);assert.equal(r.headers.has('X-ApiKey'),false);
});
test('same-origin empty POST keeps the existing asynchronous backend contract',async()=>{
 const r=await proxyApi(request('/api/investigations/market_claims_2025_09?language=es',{method:'POST',headers:{Origin:'https://radar.example','Content-Type':'application/json'},body:'{}'}),env,async(_,init)=>{assert.equal(init.body,'{}');assert.equal(init.headers.has('Origin'),false);return Response.json({state:'SUBMITTING',human_review_required:true},{status:202});});
 assert.equal(r.status,202);assert.equal((await r.json()).human_review_required,true);
});
test('missing config, foreign origin, signal overrides and oversized bodies fail closed',async()=>{
 assert.equal((await proxyApi(request(),{})).status,503);
 assert.equal((await proxyApi(request(),{...env,PUBLIC_BACKEND_URL:'https://evil.example'})).status,503);
 for(const [origin,body,status] of [['https://evil.example','{}',403],['https://radar.example','{"residual":1}',400],['https://radar.example','x'.repeat(1025),413]]){
  assert.equal((await proxyApi(request('/api/investigations/id',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body}),env)).status,status);
 }
});
test('upstream errors, redirects and exceptions never expose credential or stack details',async()=>{
 for(const status of [301,401,403,500]){
  const r=await proxyApi(request(),env,async()=>new Response('private upstream details',{status}));assert.ok(r.status>=500);assert.ok(!(await r.text()).includes('private'));
 }
 const r=await proxyApi(request(),env,async()=>{throw Error('secret-stack')});assert.deepEqual(await r.json(),{error:'BACKEND_TEMPORARILY_UNAVAILABLE'});
});
