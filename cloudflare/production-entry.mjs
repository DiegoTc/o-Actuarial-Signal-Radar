import next from './.open-next/worker.js';
import {proxyApi} from './gateway.mjs';
export default {async fetch(request,env,ctx){
 const response=new URL(request.url).pathname.startsWith('/api/')?await proxyApi(request,env):await next.fetch(request,env,ctx);
 const headers=new Headers(response.headers);
 headers.set('X-Content-Type-Options','nosniff');headers.set('Referrer-Policy','same-origin');headers.set('X-Frame-Options','DENY');
 headers.set('Permissions-Policy','camera=(), microphone=(), geolocation=()');
 return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
}};
