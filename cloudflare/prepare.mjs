/** Stage only frontend sources; never copy .env, data or provider configuration. */
import {cpSync,mkdirSync,symlinkSync,existsSync,writeFileSync,readFileSync,lstatSync,unlinkSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const production=process.argv.includes('--production');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const stage=path.join(root,'.local/cloudflare/frontend');
mkdirSync(stage,{recursive:true});
for(const name of ['app','lib','public','package.json','package-lock.json','tsconfig.json','next-env.d.ts']){
 if(existsSync(path.join(root,'frontend',name)))cpSync(path.join(root,'frontend',name),path.join(stage,name),{recursive:true});
}
// Next tracing follows real paths: copy dependencies so it never traces outside this staged app.
const modules=path.join(stage,'node_modules');
if(existsSync(modules)&&lstatSync(modules).isSymbolicLink())unlinkSync(modules);
if(!existsSync(modules))cpSync(path.join(root,'frontend/node_modules'),modules,{recursive:true,verbatimSymlinks:true});
// npm's entry point must resolve against the staged dependency tree, not the original.
const nextBin=path.join(modules,'.bin/next');
if(existsSync(nextBin)&&lstatSync(nextBin).isSymbolicLink())unlinkSync(nextBin);
if(!existsSync(nextBin))symlinkSync('../next/dist/bin/next',nextBin);
const toolsLink=path.dirname(stage)+'/node_modules';
if(!existsSync(toolsLink))symlinkSync(path.join(root,'cloudflare/node_modules'),toolsLink,'dir');
cpSync(path.join(root,'cloudflare/open-next.config.ts'),path.join(stage,'open-next.config.ts'));
for(const [source,target] of (production? [['wrangler.production.jsonc','wrangler.jsonc'],['production-entry.mjs','entry.mjs'],['production-gateway.mjs','gateway.mjs']]:[['wrangler.jsonc','wrangler.jsonc'],['entry.mjs','entry.mjs'],['gateway.mjs','gateway.mjs']]))cpSync(path.join(root,'cloudflare',source),path.join(stage,target));
writeFileSync(path.join(stage,'next.config.ts'),`import type {NextConfig} from 'next';\nconst config:NextConfig={poweredByHeader:false,images:{unoptimized:true}};export default config;\n`);
mkdirSync(path.join(stage,'tests'),{recursive:true});
for(const name of ['dashboard.spec.ts','live-investigation.spec.ts']){
 const source=path.join(root,'frontend/tests',name);
 const text=readFileSync(source,'utf8').replaceAll('127.0.0.1:3000','127.0.0.1:8787').replaceAll('localhost:3000','localhost:8787').replaceAll('expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();','await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();');
 writeFileSync(path.join(stage,'tests',name),text);
}
console.log('Staged isolated frontend under .local/cloudflare/frontend');
