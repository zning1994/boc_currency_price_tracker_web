import copy, hashlib, json, unittest
from pathlib import Path
from boc_currency_price import PRICE_FIELDS, enrich_iso8601, dedup_by_price_tuple
from history_dedup import dedup_history_rows
ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parents[2]
def rows_for(capture):
    return [enrich_iso8601(dict(currency_name=capture['code'],**dict(zip(PRICE_FIELDS,[float(v) if v else None for v in cells[1:6]])),publish_date=cells[6].replace('/','.'))) for page in capture['pages'] for cells in page['rows']]
class HistoryDedupTests(unittest.TestCase):
    def test_all_archive_bytes_and_unchanged_nonconflict_policy(self):
        for capture in json.loads((ROOT/'manifest.json').read_text())['captures']:
            raw=(ROOT/capture['capture_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),capture['capture_sha256'])
            rows=rows_for(json.loads(raw));generated=json.dumps(dedup_history_rows(rows),ensure_ascii=False,indent=4).encode()
            self.assertEqual(generated,(REPO/capture['archive_path']).read_bytes(),capture['capture_path'])
            self.assertEqual(hashlib.sha256(generated).hexdigest(),capture['archive_sha256'])
            if not capture.get('different_price_timestamp_count'):self.assertEqual(dedup_history_rows(rows),dedup_by_price_tuple(rows))
    def test_real_same_second_quotes_source_order_and_exact_repeats(self):
        for code in ['USD','AED','EUR']:
            raw=json.loads((ROOT/'raw'/f'{code}-20260928.raw.json').read_text());review=json.loads((ROOT/'raw'/f'{code}-20260928.review.json').read_text())
            self.assertEqual(raw['pages'],review['pages']);self.assertNotEqual(raw['captured_at_utc'],review['captured_at_utc'])
            rows=rows_for(raw);stamp='2026.09.28 10:10:54';expected=[r for r in rows if r['publish_date']==stamp]
            self.assertEqual(len(expected),2);result=dedup_history_rows(rows)
            self.assertEqual([r for r in result if r['publish_date']==stamp],expected)
            self.assertEqual(result,dedup_history_rows(rows+copy.deepcopy(rows)))
    def test_conflict_not_swallowed_by_adjacent_same_price_run(self):
        raw=json.loads((ROOT/'raw/USD-20260928.raw.json').read_text());same=[r for r in rows_for(raw) if r['publish_date']=='2026.09.28 10:10:54']
        earlier=copy.deepcopy(same[0]);earlier['publish_date']='2026.09.28 10:10:53'
        self.assertEqual(dedup_history_rows([*same,copy.deepcopy(same[0]),earlier]),[earlier,*same])
if __name__=='__main__':unittest.main()
