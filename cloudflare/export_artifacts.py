"""Build-time serialization of the existing normalizer; never fits or scores data."""
import sys
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actuarial-engine'))
from dashboard.data import Artifacts

def main():
    store=Artifacts(ROOT)
    output=ROOT/'.local/cloudflare/artifacts'
    docs={'api/summary':store.summary(),'api/signals':{'signals':store.signals},'api/cases':{'cases':store.cases()}}
    for case in store.selected:
        for language in ('es','en'):
            # Spanish is the probe's default; English lives alongside for inspection.
            docs[f'api/cases/{case}'+('' if language=='es' else '.en')]=store.detail(case,language)
    sizes={}
    for name,value in docs.items():
        path=output/(name+'.json');path.parent.mkdir(parents=True,exist_ok=True)
        data=json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
        path.write_bytes(data);sizes[name]=len(data)
    receipt={'source_path':str(store.root/'data/processed/cnbs/expected-behavior/primary_dynamic.csv'),
        'source_sha256':store.source_sha256,'files':sizes,'total_bytes':sum(sizes.values())}
    (output/'manifest.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({'files':len(docs),'total_bytes':receipt['total_bytes'],'source_sha256':store.source_sha256}))
if __name__=='__main__':main()
