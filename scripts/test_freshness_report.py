import copy,datetime as dt,json,unittest
from pathlib import Path
from freshness_report import build,describe_period,effective_rows
class FreshnessTests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime.fromisoformat('2026-10-29T08:40:00-07:00');self.row={'id':'wti','label':'WTI','asof':'2026-10-16','freq':'monthly avg; weekly since 2026-10-02','points':[['2026-10-16',1,2,None]],'goldusd':2,'usd':2};self.doc={'items':[self.row],'updated':'2026-10-26'}
 def test_not_live(self):
  r=build(self.doc,{},self.now)['rows'][0];self.assertFalse(r['source_rechecked_now']);self.assertIsNone(r['last_evidenced_source_check_at']);self.assertIsNone(r['next_release_at'])
 def test_not_same_as_build(self):self.assertEqual(build(self.doc,{},self.now)['rows'][0]['observation_period'],'2026-10-16')
 def test_override(self):
  d=copy.deepcopy(self.doc);d['overrides_v3']={'wti':dict(self.row,asof='2026-10-23')};self.assertEqual(effective_rows(d)['wti']['asof'],'2026-10-23')
 def test_quarter_label(self):self.assertEqual(describe_period(dict(self.row,asof='2026-04',freq='quarterly'))[0],'2026-Q2')
 def test_mismatched_provenance(self):
  s={'weekly_prices':{'wti':{'observation_date':'2026-10-23','source':'newsource','status':'available','checked_at':'today'}}};self.assertIsNone(build(self.doc,s,self.now)['rows'][0]['source'])
 def test_matched_provenance(self):
  s={'weekly_prices':{'wti':{'observation_date':'2026-10-16','source':'EIA','value':2,'status':'available','checked_at':'2026-10-26'}}};self.assertEqual(build(self.doc,s,self.now)['rows'][0]['source'],'EIA')
 def test_old_review_not_missed_release(self):
  r=build(self.doc,{},self.now+dt.timedelta(days=10))['rows'][0];self.assertEqual(r['age_review_status'],'review_old_vintage');self.assertIsNone(r['next_release_at'])
 def test_future_error(self):self.assertEqual(build(self.doc,{},self.now-dt.timedelta(days=20))['rows'][0]['age_review_status'],'future_date_error')
 def test_old_retrieved_claim_not_reused(self):
  d={'items':[dict(self.row,freq='monthly',asof='2026-09')],'updated':'2026-10-26'};s={'data':d,'series':{'wti':{'source':'EIA','checked_at':'today','fetched_at':'today'}}};self.assertIsNone(build(d,s,self.now)['rows'][0]['last_evidenced_source_check_at'])
 def test_display_rounding(self):
  d=copy.deepcopy(self.doc);d['items'][0]['usd']=4092.2
  s={'weekly_prices':{'wti':{'observation_date':'2026-10-16','source':'WGC','value':4092.25,'status':'available'}}}
  self.assertEqual(build(d,s,self.now)['rows'][0]['source'],'WGC')
 def test_value_mismatch(self):
  s={'weekly_prices':{'wti':{'observation_date':'2026-10-16','source':'EIA','value':99,'status':'available'}}}
  self.assertIsNone(build(self.doc,s,self.now)['rows'][0]['source'])
 def test_uranium_file_not_upstream_check(self):
  d={'items':[dict(self.row,id='uranium')]};s={'weekly_prices':{'uranium':{'observation_date':'2026-10-16','value':2,'status':'available','checked_at':'now'}}}
  self.assertIsNone(build(d,s,self.now)['rows'][0]['last_evidenced_source_check_at'])
 def test_quarter_end_label(self):self.assertEqual(describe_period(dict(self.row,asof='2026-06-30',freq='quarter-end stock'))[0],'2026-Q2')
 def test_weekly_override_not_quarter(self):self.assertEqual(describe_period(dict(self.row,asof='2026-10-23',freq='quarter-end stock; weekly since 2026-08-28'))[0],'2026-10-23')
 def test_all_effective_rows_included(self):
  d=copy.deepcopy(self.doc);d['more_v3']=[dict(self.row,id='extra')];d['overrides_v3']={'wti':dict(self.row,usd=99)}
  rs=build(d,{},self.now)['rows'];self.assertEqual(len(rs),2)
if __name__=='__main__':unittest.main()
