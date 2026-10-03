"""October-only merge. Never writes to production; builds reviewed plans."""
import sys,json,hashlib,subprocess,copy
from pathlib import Path
sys.path[:0]=['/Users/zning/LocalCodes/Codex/2026-10-02/task-4/history-capture','/Users/zning/LocalCodes/Codex/2026-10-02/task-4/boc-fix']
from history_dedup import dedup_history_rows
from boc_currency_price import PRICE_FIELDS,enrich_iso8601
REPO=Path('/Users/zning/LocalCodes/Codex/2026-10-02/task-4/boc-backfill-web')
def identity(r):return (r['publish_date'],tuple(r.get(f) for f in PRICE_FIELDS))
def merge(source,existing,code,day,cutoff,reviewed_conflicts=False):
 def normalize(rows):
  out=[]
  for row in rows:
   r=enrich_iso8601(copy.deepcopy(row));assert r['currency_name']==code and r['publish_date'][:10].replace('.','')==day;out.append(r)
  return out
 source=normalize(source);existing=normalize(existing)
 assert source and max(r['publish_date'] for r in source)==cutoff
 assert day in ['20261001','20261002','20261003']
 ids={identity(r) for r in source}
 unsupported=[r for r in existing if r['publish_date']<=cutoff and identity(r) not in ids]
 if unsupported:raise ValueError('Existing records absent from complete source window: independent review required')
 tail=[r for r in existing if r['publish_date']>cutoff]
 union=source+tail
 times={}
 for r in union:times.setdefault(r['publish_date'],set()).add(identity(r)[1])
 conflicts=[t for t,p in times.items() if len(p)>1]
 if conflicts and not reviewed_conflicts:raise ValueError('Same-second differing prices require independent full-page review')
 result=dedup_history_rows(union)
 assert merge_identity(result)==merge_identity(dedup_history_rows(result))
 return result,{'cutoff':cutoff,'source_raw_rows':len(source),'existing_rows':len(existing),'result_rows':len(result),'preserved_post_cutoff_raw_rows':len(tail),'removed_existing_rows_after_price_compression':[r for r in existing if identity(r) not in {identity(v) for v in result}],'same_second_conflicts':conflicts}
def merge_identity(rows):return [identity(r) for r in rows]
def gitbytes(head,path):return subprocess.check_output(['git','-C',str(REPO),'show',head+':'+path])
def plan():
 head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip();base=Path('october-backup')/head;base.mkdir(parents=True,exist_ok=True)
 codes=sorted({r['code'] for r in json.load(open('october-files-api-audit.json'))['files']});backups=[]
 for code in codes:
  for day in ['20261001','20261002','20261003']:
   rel=f'docs/BOC_CURRENCY_PRICE/{code}/{day}.json';b=gitbytes(head,rel);p=base/code/(day+'.json');p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():assert p.read_bytes()==b
   else:p.write_bytes(b)
   backups.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 (base/'manifest.json').write_text(json.dumps({'head':head,'files':backups},indent=2)+'\n')
 report={'base_head':head,'backed_up_pairs':135,'planned_pairs':[],'scope':'October data only; no production writes; Oct3 observation cutoff per source'}
 root=Path('october-cloud-source');dest=Path('october-merge-plan')/head;dest.mkdir(parents=True,exist_ok=True)
 for p in sorted(root.glob('*.raw.json')):
  raw=json.loads(p.read_text());code=raw['code'];day=raw['date'].replace('-','');source=[]
  for page in raw['pages']:
   for cells in page['rows']:
    r={'currency_name':code,'publish_date':cells[6].replace('/','.')};r.update({f:float(v) if v.strip() else None for f,v in zip(PRICE_FIELDS,cells[1:6])});source.append(enrich_iso8601(r))
  existing=json.loads((base/code/(day+'.json')).read_bytes());cutoff=max(r['publish_date'] for r in source);rows,audit=merge(source,existing,code,day,cutoff)
  again,_=merge(source,rows,code,day,cutoff);assert rows==again
  oldbytes=(base/code/(day+'.json')).read_bytes();b=oldbytes if rows==existing else (json.dumps(rows,ensure_ascii=False,indent=2)+'\n').encode();(dest/(code+'-'+day+'.json')).write_bytes(b)
  report['planned_pairs'].append({'code':code,'day':day,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'result_sha256':hashlib.sha256(b).hexdigest(),'changed':b!=(base/code/(day+'.json')).read_bytes(),**audit})
 (dest/'plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'base_head':head,'backup_pairs':135,'planned':len(report['planned_pairs']),'changed':sum(r['changed'] for r in report['planned_pairs'])}))
if __name__=='__main__':plan()
