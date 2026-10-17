/** Local-only transport adapter. Does not recalculate values or hold provider credentials. */
const loopback=host=>['localhost','127.0.0.1','[::1]'].includes(host);
const error=(status,code)=>Response.json({error:code},{status,headers:{'Cache-Control':'no-store'}});
export async function proxyApi(request,env,transport=fetch){
 const url=new URL(request.url);
 if(env.LOCAL_EXPERIMENT!=='1'||!loopback(url.hostname))return error(403,'LOCAL_EXPERIMENT_ONLY');
 if(!/^\/api\/(summary|signals|cases|investigations)(\/[a-zA-Z0-9_]+)?$/.test(url.pathname))return error(404,'NOT_FOUND');
 if(!['GET','POST'].includes(request.method))return error(405,'METHOD_NOT_ALLOWED');
 if(request.method==='POST'&&(!url.pathname.startsWith('/api/investigations/')||request.headers.get('Origin')!==url.origin))return error(403,'SAME_ORIGIN_REQUIRED');
 let origin;try{origin=new URL(env.API_ORIGIN);}catch{return error(503,'API_ORIGIN_REQUIRED');}
 if(!loopback(origin.hostname)||origin.protocol!=='http:')return error(503,'LOOPBACK_API_REQUIRED');
 // Existing backend deliberately accepts only the Docker dashboard's local origins.
 // Translate ONLY after enforcing the actual local browser origin above.
 const headers=new Headers({'Accept':'application/json'});
 if(request.method==='POST'){headers.set('Origin','http://localhost:3000');headers.set('Content-Type',request.headers.get('Content-Type')||'');}
 try{
  const response=await transport(new URL(url.pathname+url.search,origin),{method:request.method,headers,body:request.method==='POST'?await request.text():undefined,redirect:'manual'});
  if(response.status>=300&&response.status<400)return error(502,'UPSTREAM_REDIRECT_REJECTED');
  return new Response(response.body,{status:response.status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
 }catch{return error(502,'API_UNAVAILABLE');}
}
