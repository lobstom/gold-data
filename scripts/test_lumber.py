import unittest,datetime as dt
import lumber
class LumberTests(unittest.TestCase):
 def test_month_matching(self):
  d={'items':[{'id':'gold','points':[['2022-09-01',1,2000],['2022-10-01',1,2500]]},{'id':'silver','points':[['2022-09-01',1,20],['2022-10-01',1,25]]}]}
  # 12 matched monthly periods, not a synthetic production observation.
  for y in range(2023,2024):
   for m in range(1,13):
    d['items'][0]['points'].append([f'{y}-{m:02}-01',1,2000]);d['items'][1]['points'].append([f'{y}-{m:02}-01',1,20])
  daily={f'2023-{m:02}-{day:02}':600 for m in range(1,13) for day in range(1,15)}
  daily.update({f'2024-01-{day:02}':999 for day in range(1,15)})
  r=lumber.make_row(d,daily,dt.datetime(2024,1,20,tzinfo=dt.timezone.utc))
  self.assertEqual(len(r['points']),12);self.assertEqual(r['points'][-1],['2023-12-01',0.3,600,30]);self.assertEqual(r['asof'],'2023-12')
 def test_reject_unmatched(self):
  with self.assertRaises(AssertionError):lumber.make_row({'items':[{'id':'gold','points':[]},{'id':'silver','points':[]}]},{'2023-01-01':600})
 def test_weekly_first_excluded(self):
  d={'items':[{'id':rid,'freq':'monthly avg; weekly since 2024-03-01','points':[[f'2023-{m:02}-01',1,v] for m in range(1,13)]+[['2024-03-01',1,1]]} for rid,v in [('gold',2000),('silver',20)]]}
  daily={f'2023-{m:02}-{day:02}':600 for m in range(1,13) for day in range(1,15)}
  daily.update({f'2024-03-{day:02}':600 for day in range(1,15)})
  r=lumber.make_row(d,daily,dt.datetime(2024,4,20,tzinfo=dt.timezone.utc))
  self.assertEqual(r['asof'],'2023-12');self.assertEqual(r['points'][-1][1],0.3)
if __name__=='__main__':unittest.main()
