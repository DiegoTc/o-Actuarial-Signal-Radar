import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const stage=fileURLToPath(new URL('../.local/cloudflare/frontend/',import.meta.url));
const cli=fileURLToPath(new URL('./node_modules/@opennextjs/cloudflare/dist/cli/index.js',import.meta.url));
const result=spawnSync(process.execPath,[cli,'build'],{cwd:stage,stdio:'inherit',env:{...process.env,NEXT_TELEMETRY_DISABLED:'1',WRANGLER_SEND_METRICS:'false'}});
process.exit(result.status??1);
