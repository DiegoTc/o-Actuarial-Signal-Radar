"""Scan Git candidates, staged bundles and local runtime evidence without printing secrets."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'deployment/railway'))
from prepare_bundle import secret_values
values=[v.encode() for v in secret_values() if len(v)>12]
credential=Path.home()/'Library/Preferences/.wrangler/config/default.toml'
if credential.exists():
 match=re.search(r'^oauth_token\s*=\s*"([^"]+)"',credential.read_text(),re.M)
 if match:values.append(match.group(1).encode())
candidates=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
groups={'repository':[ROOT/p for p in candidates if p and (ROOT/p).is_file()],
 'bundle':[p for p in (ROOT/'.local/cloudflare/frontend/.open-next').rglob('*') if p.is_file()],
 'evidence':[p for p in (ROOT/'.local/cloudflare-production').glob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.txt'} and p.name not in {'worker-secrets.json','protected.json','git-status.txt'}]}
results={}
for name,paths in groups.items():
 hits=[str(p.relative_to(ROOT)) for p in paths if any(v in p.read_bytes() for v in values)]
 results[name]={'checked':len(paths),'secret_values_found':bool(hits),'affected_paths':hits}
manifest=json.loads((ROOT/'.local/cloudflare-production/protected.json').read_text())
changed=[name for name,digest in manifest.items() if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
results['preservation']={'checked':len(manifest),'changed':changed}
(ROOT/'.local/cloudflare-production/final-security.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results));raise SystemExit(int(bool(changed) or any(v.get('secret_values_found') for v in results.values())))
