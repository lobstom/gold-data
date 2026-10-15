#!/usr/bin/env python3
"""Weekly immutable vintages. Legacy data.json is unchanged in shape and meaning.
Scheduled Mondays publish; manual runs default to an isolated test snapshot.
No weekly price series is inferred from a monthly source.
"""
import argparse, copy, datetime as dt, hashlib, json, math, os
from pathlib import Path
import subprocess, sys, tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo('America/Los_Angeles')
REQUIRED = {'gold','silver','uranium','wti','brent','gas','ttf','coal','elec','housing','m2','debt','ahe','sp500','dow','mortgage','fedfunds','ust10','real10'}
FRED = {'housing':'MSPUS','m2':'M2SL','debt':'GFDEBTN','ahe':'AHETPI','sp500':'SP500','dow':'DJIA','mortgage':'MORTGAGE30US','fedfunds':'FEDFUNDS','ust10':'DGS10','real10':'DFII10','curve':'T10Y2Y','credit':'TCMDO / GDP','cpi':'CPIAUCNS'}

def encode(x):
    return json.dumps(x, separators=(',', ':'), sort_keys=True, allow_nan=False).encode()

def digest(x):
    return hashlib.sha256(encode(x)).hexdigest()

def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(encode(value)); tmp.replace(path)

def rows(doc):
    return doc['items'] + doc.get('more', [])

def validate(doc):
    assert isinstance(doc.get('updated'), str), 'Missing update date'
    allrows = rows(doc)
    ids = [r['id'] for r in allrows]
    assert len(set(ids)) == len(ids), 'Duplicate row IDs'
    assert REQUIRED <= set(ids), 'Missing required legacy rows'
    for r in allrows:
        assert r.get('asof') and r.get('freq') and r.get('unit'), 'Missing row metadata'
        assert math.isfinite(r['usd']), 'Non-finite latest value'
        pts = r['points']
        assert pts, 'Empty series'
        dates = [p[0] for p in pts]
        assert dates == sorted(set(dates)), 'Unsorted or duplicate observation dates: ' + r['id']
        for p in pts:
            dt.date.fromisoformat(p[0])
            assert len(p) == (2 if r.get('kind') else 4), 'Legacy tuple shape changed'
            assert all(isinstance(v, (int, float)) and math.isfinite(v) for v in p[1:]), 'Invalid observation'
        if not r.get('kind'):
            assert r['usd'] > 0 and r['goldusd'] > 0 and r['ozau'] > 0 and r['ozag'] > 0, 'Non-positive price'
    return doc

def status(cur, prev):
    if prev is None: return 'baseline'
    if cur['points'][-1][0] != prev['points'][-1][0]: return 'new_observation'
    if digest(cur) != digest(prev): return 'revised'
    return 'unchanged'

def period(r):
    a = r['asof']
    if r['id'] in {'housing','debt','credit'}:
        return a[:4] + '-Q' + str((int(a[5:7])-1)//3+1)
    return a

def metadata(doc, prev, now, log):
    old = {r['id']:r for r in rows(prev['data'])} if prev else {}
    out = {}
    for r in rows(doc):
        rid = r['id']; source = 'World Bank Pink Sheet'
        url = 'https://www.worldbank.org/en/research/commodity-markets'
        if rid in FRED:
            source = 'FRED: ' + FRED[rid]; url = 'https://fred.stlouisfed.org/series/' + FRED[rid].split(' / ')[0]
        elif rid == 'elec':
            source = 'EIA Electric Power Monthly'; url = 'https://www.eia.gov/electricity/monthly/'
        elif rid == 'uranium':
            source = 'Cameco month-end history; UxC latest available weekly CSV input'; url = 'https://www.uxc.com/p/price'
        elif rid in {'gsr','goldoil'}:
            source = 'Derived from World Bank monthly gold and silver / WTI'
        source_status = 'retrieved'
        note = 'No new observation is normal between scheduled source releases.'
        if rid == 'uranium':
            source_status = 'manual_input'
            note = 'UxC weekly free-account quote may lag 72h; Monday morning cannot include that Monday evening release. Gold conversion uses last available monthly average, NOT same-week gold.'
            a = dt.date.fromisoformat(r['asof'])
            if (now.date()-a).days > 14: source_status = 'input_overdue'
            if 'cameco scrape failed:' in log: note += ' Cameco scrape failed; saved Cameco history used.'
        out[rid] = dict(observation_period=period(r), observation_date=r['points'][-1][0], frequency=r['freq'], source=source, source_url=url,
                        fetched_at=now.isoformat() if source_status == 'retrieved' else None,
                        checked_at=now.isoformat(), source_status=source_status,
                        change_status=status(r, old.get(rid)), series_sha256=digest(r), note=note)
        if not r.get('kind'):
            out[rid]['gold_conversion'] = dict(usd_per_oz=r['goldusd'], convention='quarter average' if rid=='housing' else 'source-month average; uranium latest may use last available month',
                caveat='Historical/proxy segments retain original series conventions; not a synchronized weekly spot ratio.')
    return out

def create(doc, prev, now, kind, source_commit, log=''):
    validate(doc)
    return dict(schema_version=1, kind=kind, snapshot_date=now.date().isoformat(), captured_at=now.isoformat(), timezone=str(TZ),
        complete=True, source_commit=source_commit, data_sha256=digest(doc), previous_snapshot=prev.get('_path') if prev else None,
        data=doc, series=metadata(doc,prev,now,log),
        weekly_prices=dict(status='not_configured', note='Separate verified weekly gold/oil sources pending. Do not describe monthly data as weekly price moves.'),
        notes=['Monday observation vintage for Wednesday issue. Use this exact snapshot for chart and text.',
               'New source observation, revision, unchanged and retrieval failure are different states.',
               'Baseline has no prior frozen Monday. Never infer zero weekly movement from unchanged monthly data.',
               'Percentage rates change in percentage points or basis points, not price percent.',
               'Quarterly dates are quarter-start labels, not single-month values. Proxy history and rights notices remain in the widget.'])

def self_test():
    doc = validate(json.loads((ROOT/'data.json').read_text()))
    now = dt.datetime(2026,10,19,4,17,tzinfo=TZ)
    snap = create(doc,None,now,'test','test')
    assert all(x['change_status']=='baseline' for x in snap['series'].values())
    prev = dict(snap,_path='baseline.json')
    snap2 = create(doc,prev,now,'test','test')
    assert all(x['change_status']=='unchanged' for x in snap2['series'].values())
    x=copy.deepcopy(doc); x['items'][0]['points'][-1][2] += 1
    assert create(x,prev,now,'test','test')['series']['gold']['change_status']=='revised'
    broken=copy.deepcopy(doc); broken['items'][0]['points'][-1][2]=float('nan')
    try: validate(broken)
    except AssertionError: pass
    else: raise AssertionError('NaN accepted')
    assert snap['data_sha256']==digest(doc)
    print('PASS: legacy schema, finite values, baseline, unchanged, revision, digest, NaN rejection')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--publish',action='store_true'); p.add_argument('--self-test',action='store_true'); args=p.parse_args()
    if args.self_test: self_test(); return
    now=dt.datetime.now(TZ); monday=now.date()-dt.timedelta(days=now.weekday())
    if args.publish and now.weekday()!=0: raise SystemExit('Publishing allowed on Monday only; use manual test for other days')
    dest = ROOT/'snapshots'/(monday.isoformat()+'.json') if args.publish else ROOT/'snapshots'/'tests'/(now.strftime('%Y-%m-%dT%H%M%S')+'.json')
    # Never replace a published vintage, including manual reruns.
    if dest.exists():
        print('Snapshot already frozen, leaving data and manifest unchanged:',dest.relative_to(ROOT)); return
    prev=None
    candidates=sorted((ROOT/'snapshots').glob('????-??-??.json'))
    if candidates:
        prev=json.loads(candidates[-1].read_text()); prev['_path']=str(candidates[-1].relative_to(ROOT))
    with tempfile.TemporaryDirectory() as tmp:
        run=subprocess.run([sys.executable,str(ROOT/'scripts'/'build_data.py')],cwd=tmp,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=1500)
        print(run.stdout)
        if run.returncode: raise SystemExit('Builder failed; last valid live data/snapshots retained')
        doc=validate(json.loads((Path(tmp)/'data.json').read_text()))
    snap=create(doc,prev,now,'monday' if args.publish else 'test',os.environ.get('GITHUB_SHA','local'),run.stdout)
    manifest=dict(schema_version=1, snapshot_date=snap['snapshot_date'],captured_at=snap['captured_at'], complete=True, kind=snap['kind'],
        path=str(dest.relative_to(ROOT)), data_sha256=snap['data_sha256'],snapshot_sha256=digest(snap),previous_snapshot=snap['previous_snapshot'])
    atomic(dest,snap)
    if args.publish:
        atomic(ROOT/'data.json',doc); atomic(ROOT/'snapshots'/'latest.json',manifest)
    else: atomic(ROOT/'snapshots'/'test-latest.json',manifest)
    print('SNAPSHOT',json.dumps(manifest))

if __name__=='__main__': main()
