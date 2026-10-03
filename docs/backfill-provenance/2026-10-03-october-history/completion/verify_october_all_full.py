import json,subprocess,hashlib,collections,concurrent.futures,datetime
from pathlib import Path
from october_safe_merge import REPO,PRICE_FIELDS,enrich_iso8601
from history_dedup import dedup_history_rows
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
assert subprocess.check_output(['git','-C',str(REPO),'ls-remote','origin','refs/heads/main'],text=True).split()[0]==head
files=list(Path('october-cloud-source').glob('*.raw.json'))+[p for folder in sorted(Path('.').glob('october-source-batch*')) for p in folder.glob('*.raw.json')]
for folder in {p.parent for p in files}:
 for member in json.loads((folder/'transfer-manifest.json').read_text())['files']:
  payload=(folder/member['filename']).read_bytes();assert len(payload)==member['size_bytes'] and hashlib.sha256(payload).hexdigest()==member['sha256']
expected_pairs={(a['code'],a['date']) for a in json.load(open('october-files-api-audit.json'))['files']}
assert len(files)==135
reports=[];seen=set();totals=collections.defaultdict(collections.Counter)
for path in files:
 a=json.loads(path.read_text());c=a['code'];d=a['date'].replace('-','');assert (c,d) not in seen;seen.add((c,d));raw=[];cells=[]
 meta=json.loads(path.with_name(f'{c}-{d}.metadata.json').read_text());pagehashes=meta['page_sha256'];hashes={v['page']:v['sha256'] for v in pagehashes} if isinstance(pagehashes[0],dict) else dict(enumerate(pagehashes,1));tsv=[]
 for page in a['pages']:
  assert hashlib.sha256(json.dumps(page,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==hashes[page['page']]
  for cell in page['rows']:
   cells.append(tuple(cell));tsv.append(str(page['page'])+'\t'+'\t'.join(cell));r={'currency_name':c,'publish_date':cell[6].replace('/','.')};r.update({f:float(v) if v.strip() else None for f,v in zip(PRICE_FIELDS,cell[1:6])});raw.append(enrich_iso8601(r))
 if path.parent.name=='october-cloud-source':
  lines=path.with_name(f'{c}-{d}.tsv').read_text().splitlines()[1:];assert lines==['\t'.join(cell) for cell in cells]
  assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['full_json_sha256']
 else:assert next(path.parent.glob(c+'*'+a['date']+'*raw.tsv')).read_text().splitlines()[1:]==tsv
 assert len(raw)==meta['raw_rows'] and len(set(cells))==meta['distinct_rows']
 times=collections.defaultdict(set)
 for r in raw:times[r['publish_date']].add(tuple(r[f] for f in PRICE_FIELDS))
 assert not any(len(v)>1 for v in times.values())
 expected=dedup_history_rows(raw);b=subprocess.check_output(['git','-C',str(REPO),'show',head+f':docs/BOC_CURRENCY_PRICE/{c}/{d}.json']);assert json.loads(b)==expected
 totals[d].update(pages=len(a['pages']),raw_rows=len(raw),distinct_rows=len(set(cells)),stored_rows=len(expected),currency_days=1)
 reports.append({'code':c,'date':d,'pages':len(a['pages']),'raw_rows':len(raw),'distinct_rows':len(set(cells)),'stored_rows':len(expected),'sha256':hashlib.sha256(b).hexdigest(),'source_raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_captured_at_utc':a['captured_at_utc'],'latest_source_quote_shanghai':max(r['publish_date'] for r in raw),'day_status':'observation snapshot, not completed day' if d=='20261003' else 'complete historical query','source_archive_exact':True})
assert seen==expected_pairs
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def get(a):
 c=a['code'];d=a['date'];p=Path('october-audit-evidence')/f'cdn-full-final-{c}-{d}.json';r=subprocess.run(['curl','-sS','--connect-timeout','10','--max-time','40','-o',str(p),'-w','%{http_code}',f'https://data-bocurrencyprice.techina.science/BOC_CURRENCY_PRICE/{c}/{d}.json'],capture_output=True,text=True);b=p.read_bytes();return dict(a,status=r.stdout,cdn_sha256=hashlib.sha256(b).hexdigest(),cdn_byte_sha_match=hashlib.sha256(b).hexdigest()==a['sha256'])
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:results=list(ex.map(get,reports))
assert all(a['status']=='200' and a['cdn_byte_sha_match'] for a in results)
base='ac8811eef05f765aba6f1220e55c44cc78a7aca3';names=subprocess.check_output(['git','-C',str(REPO),'diff','--name-only',base,head],text=True).splitlines();assert all(n.startswith('docs/backfill-provenance/2026-10-03-october-history/') or n.startswith('docs/BOC_CURRENCY_PRICE/') and n.split('/')[-1] in ('20261001.json','20261002.json','20261003.json') for n in names)
assert not subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'])
assert subprocess.check_output(['git','-C',str(REPO),'ls-remote','origin','refs/heads/main'],text=True).split()[0]==head
changed=[n for n in names if n.startswith('docs/BOC_CURRENCY_PRICE/')]
snapshots=[a for a in results if a['date']=='20261003']
report={'main_sha':head,'currency_days':135,'source_coverage':'135/135','remaining':0,'october_3_status':'intraday observation snapshots only; not full-day completion','october_3_capture_range_utc':[min(a['source_captured_at_utc'] for a in snapshots),max(a['source_captured_at_utc'] for a in snapshots)],'by_date':dict(totals),'same_second_conflicts':0,'changed_quote_files':len(changed),'changed_quote_paths':changed,'cdn_started_at_utc':start,'cdn_completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all135_source_archive_and_fresh_cdn_verified':True,'september_and_realtime_api_workflow_unchanged':True,'worktree_clean':True,'results':sorted(results,key=lambda a:(a['date'],a['code']))}
Path('october-all-135-full-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ('results','changed_quote_paths')})
