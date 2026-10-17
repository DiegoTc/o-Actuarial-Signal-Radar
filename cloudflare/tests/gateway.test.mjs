import test from 'node:test';
import assert from 'node:assert/strict';
import {proxyApi} from '../gateway.mjs';
const env={LOCAL_EXPERIMENT:'1',API_ORIGIN:'http://127.0.0.1:3000'};
test('saved values and query are passed unchanged; request secrets are not forwarded',async()=>{
 let sent;const data={observed_value:185377003.67,residual:42942866.19};
 const response=await proxyApi(new Request('http://localhost:8787/api/signals?metric=monthly_claims',{headers:{Authorization:'browser-secret'}}),env,async(url,options)=>{sent=options;assert.equal(url.search,'?metric=monthly_claims');return Response.json(data)});
 assert.deepEqual(await response.json(),data);assert.equal(sent.headers.has('Authorization'),false);assert.equal(response.headers.has('Set-Cookie'),false);
});
test('local origin validated before translation for existing backend',async()=>{
 let invoked=false;
 const response=await proxyApi(new Request('http://localhost:8787/api/investigations/market_claims_2025_09',{method:'POST',headers:{Origin:'http://localhost:8787','Content-Type':'application/json'},body:'{}'}),env,async(url,options)=>{invoked=true;assert.equal(options.headers.get('Origin'),'http://localhost:3000');assert.equal(options.body,'{}');return Response.json({state:'SUBMITTING',human_review_required:true})});
 assert.equal(invoked,true);assert.equal((await response.json()).human_review_required,true);
 assert.equal((await proxyApi(new Request('http://localhost:8787/api/investigations/id',{method:'POST',headers:{Origin:'https://evil.example'}}),env)).status,403);
});
test('public requests, nonlocal upstreams, unknown routes and redirects fail closed',async()=>{
 assert.equal((await proxyApi(new Request('https://public.example/api/summary'),env)).status,403);
 assert.equal((await proxyApi(new Request('http://localhost:8787/api/summary'),{...env,API_ORIGIN:'https://remote.example'})).status,503);
 assert.equal((await proxyApi(new Request('http://localhost:8787/api/secrets'),env)).status,404);
 assert.equal((await proxyApi(new Request('http://localhost:8787/api/summary'),env,async()=>new Response(null,{status:302}))).status,502);
});
test('transport failures expose a fixed error only',async()=>{
 const r=await proxyApi(new Request('http://localhost:8787/api/summary'),env,async()=>{throw Error('secret')});assert.deepEqual(await r.json(),{error:'API_UNAVAILABLE'});
});
