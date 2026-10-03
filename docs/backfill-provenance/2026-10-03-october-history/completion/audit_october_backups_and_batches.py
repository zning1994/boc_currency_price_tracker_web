import json,hashlib,subprocess,datetime
from pathlib import Path
from october_safe_merge import REPO
base='ac8811eef05f765aba6f1220e55c44cc78a7aca3';plans=[Path('october-merge-plan')/base/'plan.json']+sorted(Path('october-merge-plan').glob('batch-*/plan.json'));assert len(plans)==45
records=[];seen=set();changed=0
for i,p in enumerate(plans,1):
 plan=json.loads(p.read_text());head=plan['base_head'];root=Path('october-backup')/head;manifest=json.loads((root/'manifest.json').read_text());assert len(manifest['files'])==135
 for r in manifest['files']:
  c,d=r['path'].split('/')[-2:];b=(root/c/d).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 batch=f'batch-{i:03d}';pub=json.load(open('october-'+batch+'-publication.json'));assert pub['base_main_sha']==head and pub['pages_conclusion']=='success' and pub['scope_preservation_verified'];assert pub.get('cdn_all_verified',pub.get('cdn_all_seven_http200_byte_sha_match'))
 prefix=REPO/'docs/backfill-provenance/2026-10-03-october-history';dest=prefix if i==1 else prefix/'batches'/batch
 committed_manifest=json.loads((dest/('backup-manifest-135.json' if i>1 else 'backup-manifest-135.json')).read_text());assert committed_manifest==manifest
 for r in plan['planned_pairs']:
  pair=(r['code'],r['day']);assert pair not in seen;seen.add(pair);b=p.with_name(r['code']+'-'+r['day']+'.json').read_bytes();assert hashlib.sha256(b).hexdigest()==r['result_sha256']
  actual=subprocess.check_output(['git','-C',str(REPO),'show',pub['main_sha']+f':docs/BOC_CURRENCY_PRICE/{r["code"]}/{r["day"]}.json']);assert actual==b
  if r['changed']:
   prior=(dest/('before-batch-001' if i==1 else 'before')/r['code']/(r['day']+'.json')).read_bytes();assert prior==(root/r['code']/(r['day']+'.json')).read_bytes();changed+=1
 records.append({'batch':batch,'base_main_sha':head,'main_sha':pub['main_sha'],'pairs':len(plan['planned_pairs']),'backup_pairs_sha_verified':135,'pages_run_id':pub['pages_run_id'],'pages_conclusion':pub['pages_conclusion'],'fetch_conclusion':pub['fetch_conclusion'],'cdn_verified':True,'tests':pub['tests']})
assert len(seen)==135 and changed==85
out={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batches':45,'unique_pairs':135,'changed_quote_files':changed,'backups_verified':6075,'all_changed_file_original_bytes_preserved':True,'all_batch_pages_and_cdn_passed':True,'results':records};Path('october-backup-batch-audit.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='results'})
