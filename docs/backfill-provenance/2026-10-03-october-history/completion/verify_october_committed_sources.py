import json,hashlib,subprocess,datetime
from pathlib import Path
from october_safe_merge import REPO
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip();records=[]
for i in range(1,46):
 batch=f'batch-{i:03d}';root=Path('october-cloud-source') if i==1 else Path(f'october-source-batch{i:03d}');prefix='docs/backfill-provenance/2026-10-03-october-history/'+('source-evidence/batch-001' if i==1 else 'batches/'+batch+'/source-evidence')
 for f in root.iterdir():
  if f.is_file():records.append({'batch':batch,'local_path':str(f),'path':prefix+'/'+f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
query=''.join(head+':'+r['path']+'\n' for r in records).encode();blob=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=query,capture_output=True,check=True).stdout;offset=0
for r in records:
 end=blob.index(b'\n',offset);h=blob[offset:end].split();assert h[1]==b'blob';size=int(h[2]);start=end+1;b=blob[start:start+size];assert b==Path(r['local_path']).read_bytes();r['git_byte_sha_match']=True;offset=start+size+1
assert offset==len(blob)
out={'main_sha':head,'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':len(records),'all_committed_source_bytes_equal_verified_transfer_files':True,'results':records};Path('october-committed-source-verification.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='results'})
