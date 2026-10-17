"""Small real AMD Token Factory smoke test; writes no authentication material."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from _bootstrap import ROOT
from investigation.amd_client import AMDTokenFactoryClient, matches_token_factory_model
from investigation.models import Settings

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'.local/token-factory/smoke.json')
    args = parser.parse_args()
    # Runtime evidence is confined to the ignored local directory.
    output = args.output.resolve()
    if not output.is_relative_to((ROOT/'.local').resolve()):
        parser.error('Save runtime evidence under .local/')
    settings = Settings.from_env('amd_token_factory')
    start = time.monotonic()
    content, metadata = AMDTokenFactoryClient(settings).complete([{'role':'user','content':
        'Return only JSON: {"status":"ok","provider":"amd_token_factory"}'}], {})
    answer = json.loads(content)
    if answer != {'status':'ok','provider':'amd_token_factory'} or metadata.get('finish_reason') != 'stop' or not matches_token_factory_model(metadata.get('response_model'), settings.model):
        raise SystemExit('Token Factory smoke test failed; no verification recorded')
    receipt = {'provider':'amd_token_factory','model':settings.model,'served_model':metadata.get('response_model'),'base_url':settings.base_url,
        'timestamp':datetime.now(timezone.utc).isoformat(),'latency_seconds':round(time.monotonic()-start,3),
        'response':answer,'request_id':metadata.get('request_id'),'usage':metadata.get('usage')}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
    print('PASS: real AMD Token Factory JSON inference; model='+settings.model+'; seconds='+str(receipt['latency_seconds']))
