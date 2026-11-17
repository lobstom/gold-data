import copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
import treasury
from treasury_quotes import decimal_quote,select_contract,completed_week

class TreasuryTests(unittest.TestCase):
    def test_quotes(self):
        self.assertEqual(decimal_quote("105'140",'ZN'),105.4375)
        self.assertEqual(decimal_quote("105'145",'ZN'),105.453125)
        self.assertEqual(decimal_quote("105'17",'ZB'),105.53125)
    def test_bad_quotes(self):
        for s,sym in [("105'325",'ZN'),("105'141",'ZN'),("105'140B",'ZN'),('NaN','ZN'),("105'175",'ZB'),("105'17",'XX')]:
            with self.assertRaises(ValueError):decimal_quote(s,sym)
    def test_roll_full_week(self):
        for day in range(16,21):self.assertEqual(select_contract('ZN',dt.date(2026,11,day)),'ZNZ26')
        for day in range(23,28):self.assertEqual(select_contract('ZN',dt.date(2026,11,day)),'ZNH27')
        self.assertEqual(select_contract('ZB',dt.date(2026,12,31)),'ZBH27')
    def test_roll_marker(self):
        obs=[(dt.date(2026,11,d),"105'140")for d in [23,24,25]]
        x=completed_week('ZN',dt.date(2026,11,27),obs,4000,dt.date(2026,11,28))
        self.assertTrue(x['roll']);self.assertEqual(x['contract'],'ZNH27');self.assertEqual(x['decimal_per_100_face'],105.4375)
    def test_week_guards(self):
        obs=[(dt.date(2026,11,d),"105'140")for d in [9,10]]
        with self.assertRaises(ValueError):completed_week('ZN',dt.date(2026,11,13),obs,4000,dt.date(2026,11,14))
        obs.append(obs[0])
        with self.assertRaises(ValueError):completed_week('ZN',dt.date(2026,11,13),obs,4000,dt.date(2026,11,14))
    def setUp(self):
        self.doc=json.loads((treasury.ROOT/'data.json').read_text())
        self.src=json.loads((treasury.ROOT/'inputs/treasury/2026-11-13.json').read_text())
        self.now=dt.datetime(2026,11,17,21,tzinfo=dt.timezone.utc)
    def run_input(self,src,doc=None):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'test.json').write_text(json.dumps(src))
            target=doc if doc is not None else copy.deepcopy(self.doc)
            treasury.apply(target,log=lambda x:None,now=self.now,inputs_dir=d)
            return target
    def test_real_golden_and_preservation(self):
        d=self.run_input(self.src)
        for key in ['items','more','overrides_v3','recessions','updated','weekly_notes']:self.assertEqual(d[key],self.doc[key])
        r={r['id']:r for r in d['more_v3']};self.assertAlmostEqual(r['zn']['quote_per_100_face'],105.996875);self.assertAlmostEqual(r['zb']['quote_per_100_face'],106.80625)
        for rid in ['zn','zb']:
            self.assertEqual(r[rid]['goldusd'],3988.6);self.assertEqual(r[rid]['weeks'][0]['daily_count'],5)
            self.assertAlmostEqual(r[rid]['ozau'],r[rid]['usd']/3988.6)
            self.assertIsNone(r[rid]['ozag']);self.assertFalse(r[rid]['weeks'][0]['roll'])
    def test_partial_rejected(self):
        s=copy.deepcopy(self.src);s['records'][0]['data']['reportType']='Preliminary'
        with self.assertRaises(AssertionError):self.run_input(s)
    def test_inactive_rejected(self):
        s=copy.deepcopy(self.src);s['records'][0]['data']['settlements'][0]['volume']='0'
        with self.assertRaises(AssertionError):self.run_input(s)
    def test_conflicting_duplicate_rejected(self):
        s=copy.deepcopy(self.src);x=copy.deepcopy(s['records'][0]);x['data']['settlements'][0]['settle']="108'000";s['records'].append(x)
        with self.assertRaises(AssertionError):self.run_input(s)
    def test_missing_gold_retains_existing(self):
        d=copy.deepcopy(self.doc);gold=next(r for r in d['items']if r['id']=='gold');gold['points']=[p for p in gold['points']if p[0]!='2026-11-13'];before=copy.deepcopy(d['more_v3']);self.run_input(self.src,d);self.assertEqual(d['more_v3'],before)
    def test_repeat_exact(self):
        d=self.run_input(self.src);self.assertEqual(d,self.run_input(self.src,d))

if __name__=='__main__':unittest.main()
