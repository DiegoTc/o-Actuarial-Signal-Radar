"""Explicit upload of curated documentation excerpts to a configured Evolus library."""
import argparse
import sys
from _bootstrap import ROOT
from investigation.package import build_package
from investigation.context import load_knowledge
from investigation.evolus_client import EvolusClient,EvolusSettings
from investigation.models import ProviderError
from investigation.io import save_json

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',action='append',default=[])
    parser.add_argument('--upload',action='store_true',help='Perform external library uploads; default is a local plan only')
    args=parser.parse_args()
    try:
        chunks={}
        for case in args.case or ['market_claims_2025_09','market_ratio_2025_03']:
            for chunk in load_knowledge(build_package(case))[0]:chunks[chunk['id']]=chunk
        if not args.upload:
            print('LOCAL PLAN ONLY — no Evolus requests')
            for c in chunks.values():print(c['id'],len(c['text']),c['sha256'])
        else:
            client=EvolusClient(EvolusSettings.from_env(library=True))
            results=[]
            for c in chunks.values():
                result=client.upload_document(c['id'].split(':',1)[1],c['text'])
                results.append({'id':c['id'],'sha256':c['sha256'],'upload_response':result})
                # Persist each success; a later failure must not erase prior external changes.
                save_json(ROOT/'reports/investigations/evolus_knowledge_uploads.json',{'status':'UPLOADED_INDEXING_NOT_VERIFIED','documents':results})
            print('Uploaded; inspect Evolus document indexing status before running a workflow')
    except (ValueError,OSError,KeyError,ProviderError) as exc:
        print('Knowledge sync failed: '+str(exc),file=sys.stderr);sys.exit(1)
