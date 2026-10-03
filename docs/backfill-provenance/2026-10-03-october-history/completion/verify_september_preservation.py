import json,hashlib,subprocess,datetime
from pathlib import Path
from october_safe_merge import REPO
old=json.load(open('/Users/zning/LocalCodes/Codex/2026-10-02/task-4/history-capture/production-full-verification-1080.json'));assert len(old['results'])==1080
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
paths=[f"docs/BOC_CURRENCY_PRICE/{r['code']}/{r['date'].replace('-','')}.json" for r in old['results']]
refs=''.join(head+':'+p+'\n' for p in paths).encode();proc=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=refs,capture_output=True,check=True);blob=proc.stdout;offset=0;rows=[]
for r,p in zip(old['results'],paths):
 end=blob.index(b'\n',offset);header=blob[offset:end].split();assert header[1]==b'blob';size=int(header[2]);start=end+1;b=blob[start:start+size];assert blob[start+size:start+size+1]==b'\n';offset=start+size+1;sha=hashlib.sha256(b).hexdigest();assert sha==r['expected_sha256'];rows.append({'path':p,'sha256':sha,'matches_september_full_cdn_audit':True})
assert offset==len(blob)
out={'main_sha':head,'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'september_pairs':1080,'all1080_git_bytes_sha_preserved':True,'prior_full_cdn_audit_completed_at_utc':old['verified_at_utc'],'verification_mode':'All1080 current Git blobs freshly hashed against completed September full CDN audit; CDN not refetched in this preservation check','results':rows};Path('september-preservation-after-october.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='results'})
