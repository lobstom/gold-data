import unittest,datetime as dt,copy
import copper
class CopperTests(unittest.TestCase):
 def data(self):
  d={'items':[{'id':rid,'freq':'monthly avg; weekly since 2024-03-01','points':[[f'2023-{m:02}-01',1,v] for m in range(1,13)]+[['2024-03-01',1,1]]} for rid,v in [('gold',2000),('silver',20)]]}
  r=[[],[],[],[],[None,'Copper'],[None,'($/mt)']]+[[f'2023M{m:02}',8000] for m in range(1,13)]+[['2024M03',9000],['2024M04',99999]]
  return d,r
 def test_months_units_and_other_rows(self):
  d,r=self.data();old=copy.deepcopy(d);x=copper.apply(d,r,'source',dt.datetime(2024,4,20,tzinfo=dt.timezone.utc),lambda m:None)
  self.assertEqual(x['points'][-1],['2023-12-01',4,8000,400]);self.assertEqual(len(x['points']),12);self.assertEqual(x['unit'],'tonne');self.assertEqual([i for i in d['items'] if i['id']!='copper'],old['items'])
 def test_bad_unit(self):
  d,r=self.data();r[5][1]='cents/lb'
  with self.assertRaises(AssertionError):copper.make_row(d,r,'source')
 def test_missing_metal_fails(self):
  d,r=self.data();d['items'][1]['points']=[]
  with self.assertRaises(AssertionError):copper.make_row(d,r,'source')
if __name__=='__main__':unittest.main()
