import unittest
from october_safe_merge import merge,PRICE_FIELDS
class Safety(unittest.TestCase):
 def row(self,time,price):return {'currency_name':'USD','publish_date':'2026.10.03 '+time,**{f:price for f in PRICE_FIELDS}}
 def runmerge(self,s,e,review=False):return merge(s,e,'USD','20261003',max(r['publish_date'] for r in s),review)[0]
 def test_correct_time_and_idempotent(self):
  s=[self.row('00:00:05',1),self.row('01:00:00',1),self.row('02:00:00',2)];r=self.runmerge(s,[s[1],s[2]]);self.assertEqual([v['publish_date'] for v in r],[s[0]['publish_date'],s[2]['publish_date']]);self.assertEqual(r,self.runmerge(s,r))
 def test_recurrence_retained(self):
  s=[self.row('00:00:05',1),self.row('01:00:00',2),self.row('02:00:00',1)];self.assertEqual(len(self.runmerge(s,[])),3)
 def test_concurrent_later_price_preserved(self):
  s=[self.row('00:00:05',1)];tail=self.row('03:00:00',2);r=self.runmerge(s,[s[0],tail]);self.assertEqual(r[-1]['publish_date'],tail['publish_date']);self.assertEqual(len(r),2)
 def test_unknown_old_price_stops(self):
  s=[self.row('00:00:05',1),self.row('02:00:00',2)]
  with self.assertRaises(ValueError):self.runmerge(s,[self.row('01:00:00',7)])
 def test_conflict_requires_review_then_retains_both(self):
  s=[self.row('00:00:05',1),self.row('00:00:05',2)]
  with self.assertRaises(ValueError):self.runmerge(s,[])
  self.assertEqual(len(self.runmerge(s,[],True)),2)
 def test_inputs_not_mutated(self):
  s=[self.row('00:00:05',1)];self.runmerge(s,[]);self.assertNotIn('publish_at_utc',s[0])
unittest.main()
