"""Read-only Cloudflare account/plan inspection using Wrangler's existing OAuth login.
Never print or copy the OAuth token; retain only non-secret deployment metadata.
"""
import argparse,json,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
parser=argparse.ArgumentParser();parser.add_argument('--account-id',required=True);account=parser.parse_args().account_id
if not re.fullmatch(r'[0-9a-f]{32}',account):raise SystemExit('Invalid account ID')
config=Path.home()/'Library/Preferences/.wrangler/config/default.toml'
match=re.search(r'^oauth_token\s*=\s*"([^"]+)"',config.read_text(),re.M)
if not match:raise SystemExit('Wrangler OAuth credential unavailable')
token=match.group(1)
result={}
for name,path in [('subscriptions','subscriptions'),('worker_settings','workers/account-settings'),('subdomain','workers/subdomain'),('entitlements','entitlements'),('deployment_settings','workers/scripts/actuarial-signal-radar/settings')]:
 try:
  with urlopen(Request(f'https://api.cloudflare.com/client/v4/accounts/{account}/{path}',headers={'Authorization':'Bearer '+token}),timeout=30) as r:value=json.load(r)
  result[name]=value.get('result') if value.get('success') else {'error_codes':[e.get('code') for e in value.get('errors',[])]}
 except HTTPError as e:result[name]={'http_status':e.code}
if isinstance(result.get('deployment_settings'),dict):
 settings=result['deployment_settings'];result['deployment_settings']={k:settings[k] for k in ['usage_model','limits','observability'] if k in settings};result['deployment_settings']['bindings']=[{'name':b.get('name'),'type':b.get('type')} for b in settings.get('bindings',[])]
Path('.local/cloudflare-production/account-status.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
