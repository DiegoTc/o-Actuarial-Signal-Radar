/** Production transport only. Credentials are Worker bindings, never browser input. */
const BACKEND='https://actuarial-signal-radar-api-production.up.railway.app';
const json=(status,error)=>Response.json({error},{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
export async function proxyApi(request,env,transport=fetch){
 const url=new URL(request.url);
 if(!/^\/api\/(summary|signals|cases|investigations)(\/[a-zA-Z0-9_]+)?$/.test(url.pathname))return json(404,'NOT_FOUND');
 if(!['GET','POST'].includes(request.method))return json(405,'METHOD_NOT_ALLOWED');
 if(env.PUBLIC_BACKEND_URL!==BACKEND||!env.DASHBOARD_BACKEND_TOKEN)return json(503,'BACKEND_NOT_CONFIGURED');
 const headers=new Headers({'Accept':'application/json','Authorization':'Bearer '+env.DASHBOARD_BACKEND_TOKEN});
 let body;
 if(request.method==='POST'){
  if(!/^\/api\/investigations\/[a-zA-Z0-9_]+$/.test(url.pathname))return json(405,'METHOD_NOT_ALLOWED');
  if(request.headers.get('Origin')!==url.origin||request.headers.get('Sec-Fetch-Site')==='cross-site')return json(403,'SAME_ORIGIN_REQUIRED');
  if(request.headers.get('Content-Type')?.split(';')[0]!=='application/json')return json(415,'JSON_REQUIRED');
  // The API accepts no signal overrides. Keep the body bounded without reading an arbitrary stream.
  const reader=request.body?.getReader();let size=0;const chunks=[];
  if(reader){while(true){const part=await reader.read();if(part.done)break;size+=part.value.byteLength;if(size>1024){await reader.cancel();return json(413,'REQUEST_TOO_LARGE');}chunks.push(part.value);}}
  const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
  body=new TextDecoder().decode(bytes)||'{}';
  try{const value=JSON.parse(body);if(!value||Array.isArray(value)||Object.keys(value).length)return json(400,'SIGNAL_OVERRIDES_NOT_ALLOWED');}catch{return json(400,'INVALID_JSON');}
  headers.set('Content-Type','application/json');
  // Authenticated server-to-server request: omit browser Origin. Backend already accepts this contract.
 }
 try{
  const upstream=await transport(BACKEND+url.pathname+url.search,{method:request.method,headers,body,redirect:'manual',signal:AbortSignal.timeout(55000)});
  if(upstream.status>=300&&upstream.status<400)return json(502,'UPSTREAM_REDIRECT_REJECTED');
  if(upstream.status>=500)return json(503,'BACKEND_TEMPORARILY_UNAVAILABLE');
  if(upstream.status===401||upstream.status===403)return json(502,'BACKEND_AUTHENTICATION_FAILED');
  // Stream JSON; no parsing/copying the multi-MB saved signals payload on Workers Free.
  return new Response(upstream.body,{status:upstream.status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
 }catch{return json(503,'BACKEND_TEMPORARILY_UNAVAILABLE');}
}
