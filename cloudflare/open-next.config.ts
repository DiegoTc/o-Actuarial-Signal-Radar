import {defineCloudflareConfig} from '@opennextjs/cloudflare';
// No ISR/data cache, R2, KV, service creation or deployment in this experiment.
export default defineCloudflareConfig();
