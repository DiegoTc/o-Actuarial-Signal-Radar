import next from './.open-next/worker.js';
import {proxyApi} from './gateway.mjs';
export default {async fetch(request,env,ctx){
 if(new URL(request.url).pathname.startsWith('/api/'))return proxyApi(request,env);
 return next.fetch(request,env,ctx);
}};
