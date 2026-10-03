import json,hashlib,datetime
from pathlib import Path
root=Path('october-final-three-recheck');t=json.loads((root/'transfer-manifest.json').read_text());assert t['counts_as_new_unique_source'] is False
for m in t['files']:
 b=(root/m['filename']).read_bytes();assert len(b)==m['size_bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
results=[]
for c in ['AED','MUR','USD']:
 p=root/f'{c}-20261003.raw.json';a=json.loads(p.read_text());old=json.loads((Path('october-cloud-source')/p.name).read_text());meta=json.loads(p.with_name(f'{c}-20261003.metadata.json').read_text());assert a['pages']==old['pages'];hashes={r['page']:r['sha256'] for r in meta['page_sha256']};flat=[];rows=[]
 for page in a['pages']:
  assert hashlib.sha256(json.dumps(page,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==hashes[page['page']]
  for cell in page['rows']:flat.append(str(page['page'])+'\t'+'\t'.join(cell));rows.append(tuple(cell))
 assert (root/f'{c}_2026-10-03_raw.tsv').read_text().splitlines()[1:]==flat
 assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'] and len(rows)==meta['raw_rows'] and len(set(rows))==meta['distinct_rows']
 assert not meta['same_second_conflicts'] and a['captured_at_utc']>old['captured_at_utc']
 results.append({'code':c,'date':'20261003','captured_at_utc':a['captured_at_utc'],'original_captured_at_utc':old['captured_at_utc'],'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'raw_rows':len(rows),'distinct_rows':len(set(rows)),'pages_equal_original':True,'latest_quote_shanghai':max(r[6] for r in rows),'day_status':'intraday observation snapshot, not completed day'})
assert sum(a['raw_rows'] for a in results)==20 and sum(a['distinct_rows'] for a in results)==12
out={'source_dir':str(root),'zip_sha256':'722b523305495a24e89cf316a05e74b14e984e5d6b53322b07ffc770ab66816f','verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_three_raw_pages_equal_original':True,'all_three_sha_page_tsv_verified':True,'counts_as_new_unique_pairs':False,'unchanged_unique_coverage':135,'results':results};Path('october-final-three-recheck-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
