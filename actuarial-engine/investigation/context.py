"""Small checksummed knowledge excerpts; raw datasets never enter model context."""
import re
from pathlib import Path
from ingestion.cnbs import checksum
from investigation.models import ROOT
from investigation.io import strict_json

MANIFEST=ROOT/'evolus/knowledge/manifest.json'


def excerpt(text,sections):
    lines=text.splitlines()
    captured=[]
    for heading in sections:
        marker='## '+heading
        if marker not in lines: raise ValueError('Missing knowledge heading: '+heading)
        start=lines.index(marker)
        end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('## ')),len(lines))
        captured.append('\n'.join(lines[start:end]).strip())
    return '\n\n'.join(captured)+'\n'


def load_knowledge(package, root=ROOT):
    root=Path(root)
    manifest_path=root/'evolus/knowledge/manifest.json'
    manifest=strict_json(manifest_path.read_text())
    chunks=[]
    for doc in manifest['documents']:
        if doc.get('case_id') and doc['case_id']!=package['signal_id']:continue
        path=(root/doc['path']).resolve()
        if root.resolve() not in path.parents or path.suffix!='.md' or not doc['path'].startswith(('docs/','reports/')):
            raise ValueError('Knowledge sources must be repository Markdown documentation')
        source=path.read_bytes()
        if checksum(source)!=doc['source_sha256']: raise ValueError('Knowledge source checksum mismatch: '+doc['id'])
        text=excerpt(source.decode('utf-8'),doc['sections'])
        if checksum(text.encode())!=doc['excerpt_sha256']: raise ValueError('Knowledge excerpt checksum mismatch')
        if len(text)>doc['max_characters']: raise ValueError('Knowledge excerpt exceeds declared context limit')
        chunks.append({'id':'knowledge:'+doc['id'],'path':doc['path'],'text':text,'sha256':doc['excerpt_sha256'],
                       'source_sha256':doc['source_sha256'],'evidence_type':'METHODOLOGY_OR_STATISTICAL_REPORT_NOT_EXTERNAL_CAUSE'})
    if sum(len(c['text']) for c in chunks)>24000: raise ValueError('Knowledge context exceeds 24000 characters')
    return chunks,{'manifest_path':'evolus/knowledge/manifest.json','manifest_sha256':checksum(manifest_path.read_bytes()),
                   'retrieval':'LOCAL_MANIFEST_EXCERPTS_NOT_EVOLUS','documents':[{'id':c['id'],'sha256':c['sha256']} for c in chunks]}


def evidence_ids(package, chunks):
    # JSON-pointer references to immutable supplied fields, plus registered knowledge chunks.
    return {'signal:/'+k for k in package} | {c['id'] for c in chunks}
