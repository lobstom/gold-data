#!/usr/bin/env python3
"""Weekly immutable vintages. Legacy data.json is unchanged in shape and meaning.
Scheduled Mondays publish; manual runs default to an isolated test snapshot.
No weekly price series is inferred from a monthly source.
"""
import argparse, copy, datetime as dt, hashlib, json, math, os
from pathlib import Path
import subprocess, sys, tempfile, csv, io, urllib.request
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
            for j, v in enumerate(p[1:], start=1):
                if v is None and j == 3 and not r.get('kind'):
                    continue  # weekly point without a weekly silver source: oz Ag stays monthly
                assert isinstance(v, (int, float)) and math.isfinite(v), 'Invalid observation'
        if not r.get('kind') and not r.get('fixed'):
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
        elif rid == 'dxy':
            source = 'Derived: ICE DXY formula on FRED G.5 monthly exchange rates (1980+); Fed major currencies index DTWEXM before 1980'; url = 'https://fred.stlouisfed.org/series/DTWEXM'
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

def weekly_prices(now):
    result = dict(status='partial')
    def entry(points, source, url, unit, frequency):
        points=sorted(points)
        assert points and all(math.isfinite(v) and v>0 for _,v in points)
        d,v=points[-1]
        out=dict(status='available', value=v, unit=unit, observation_date=d, source=source, source_url=url, frequency=frequency, checked_at=now.isoformat())
        if len(points)>1:
            pd,pv=points[-2]; gap=(dt.date.fromisoformat(d)-dt.date.fromisoformat(pd)).days
            out.update(previous_observation_date=pd,previous_value=pv,days_between_observations=gap,
                       change_pct=(v/pv-1)*100,change_basis='week_over_week' if gap==7 else 'since_previous_observation')
        else: out.update(change_pct=None,change_basis='baseline')
        out['age_days']=(now.date()-dt.date.fromisoformat(d)).days
        if out['age_days']>14: out['status']='overdue'
        return out
    # Short daily window avoids chart-level long-range sampling. Only complete weeks.
    start=now.date()-dt.timedelta(days=70)
    stamp=int(dt.datetime.combine(start,dt.time(),tzinfo=dt.timezone.utc).timestamp()*1000)
    url='https://fsapi.gold.org/api/goldprice/v11/chart/price/usd/oz/'+str(stamp)+','
    try:
        run=subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','90',url],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=100)
        response=json.loads(run.stdout); raw=response['chartData']['USD']
        days={dt.datetime.fromtimestamp(t/1000,dt.timezone.utc).date():float(v) for t,v in raw if v is not None}
        cutoff=now.date()-dt.timedelta(days=(now.weekday()-4 if now.weekday()>=5 else now.weekday()+3))  # most recent completed Friday
        groups={}
        for day,value in sorted(days.items()):
            if day.weekday()>4 or day>cutoff: continue
            friday=day+dt.timedelta(days=4-day.weekday())
            groups.setdefault(friday,[]).append((day,value))
        weeks=[(day.isoformat(),sum(v for _,v in values)/len(values)) for day,values in sorted(groups.items()) if len(values)>=3]
        assert len(weeks)>=2, 'Insufficient complete daily coverage for two weeks'
        result['gold']=entry(weeks,'World Gold Council gold price',url,'USD/troy oz','completed-week average of available daily observations, Monday-Friday')
        latest=dt.date.fromisoformat(weeks[-1][0]); values=groups[latest]
        result['gold'].update(week_start=(latest-dt.timedelta(days=4)).isoformat(),daily_observation_dates=[d.isoformat() for d,_ in values],daily_observation_count=len(values),source_asof=response['chartData'].get('asOfDate'),
            note='World Gold Council chart data, not identified here as the LBMA fixing. Weekly average includes available business-day observations (at least 3); holidays reduce count. Short daily window avoids long-range chart sampling. No intraday quote or monthly gold substitution.')
    except Exception as e:
        result['gold']=dict(status='unavailable',source='World Gold Council gold price',source_url=url,error=str(e),checked_at=now.isoformat())
        print('::warning::Weekly WGC gold unavailable: '+str(e))
    for rid,code,title in [('wti','RWTC','WTI Cushing spot'),('brent','RBRTE','Europe Brent spot')]:
        url='https://www.eia.gov/dnav/pet/hist_xls/'+code+'w.xls'
        try:
            import xlrd
            req=urllib.request.Request(url,headers={'User-Agent':'gold-data weekly research snapshot'})
            data=urllib.request.urlopen(req,timeout=90).read()
            book=xlrd.open_workbook(file_contents=data); sheet=book.sheet_by_name('Data 1')
            points=[(xlrd.xldate_as_datetime(sheet.cell_value(i,0),book.datemode).date().isoformat(),float(sheet.cell_value(i,1))) for i in range(3,sheet.nrows) if sheet.cell_type(i,0)==xlrd.XL_CELL_DATE and isinstance(sheet.cell_value(i,1),(float,int))]
            result[rid]=entry(points,'EIA '+title+' weekly average',url,'USD/bbl','weekly average, week ending Friday')
            result[rid]['note']='Latest source-published completed week; not necessarily the immediately preceding Friday. No carry-forward or monthly gold denominator.'
        except Exception as e:
            result[rid]=dict(status='unavailable',source_url=url,error=str(e),checked_at=now.isoformat())
            print('::warning::Weekly '+rid+' unavailable: '+str(e))
    try:
        with (ROOT/'scripts'/'uranium.csv').open() as f:
            points=[(r['date'],float(r['usd_per_lb'])) for r in csv.DictReader(f)]
        result['uranium']=entry(points,'UxC free-account weekly quote, authenticated retrieval stored in CSV','https://www.uxc.com/p/price','USD/lb','weekly quote; latest available at Monday cut')
        result['uranium']['note']='Input file, not fetched by this build. Separate authenticated weekly retrieval is required before the run. Free quote can lag 72h; not Monday evening release. Do not describe as week-ending Friday.'
    except Exception as e:
        result['uranium']=dict(status='unavailable',error=str(e),checked_at=now.isoformat())
        print('::warning::Weekly uranium input unavailable: '+str(e))
    for rid in ('wti','brent'):
        oil,gold=result[rid],result['gold']
        if oil.get('status')=='available' and gold.get('status')=='available' and oil['observation_date']==gold['observation_date'] and oil.get('previous_observation_date')==gold.get('previous_observation_date'):
            ratio=oil['value']/gold['value']; previous=oil['previous_value']/gold['previous_value']
            oil['in_gold']=dict(value=ratio,unit='oz Au/bbl',previous_value=previous,change_pct=(ratio/previous-1)*100,
                observation_date=oil['observation_date'],previous_observation_date=oil['previous_observation_date'],
                convention='ratio of EIA weekly oil average to WGC same-week gold average, not average of daily ratios')
    # Extended weekly set (2026-10-21): genuine weekly/daily sources only; rates report percentage-point moves
    import weekly_overlay as wo
    def rate_entry(points, source, url, unit, frequency):
        points=sorted(points)
        assert points and all(math.isfinite(v) for _,v in points)
        d,v=points[-1]
        out=dict(status='available', value=v, unit=unit, observation_date=d, source=source, source_url=url, frequency=frequency, checked_at=now.isoformat())
        if len(points)>1:
            pd,pv=points[-2]
            out.update(previous_observation_date=pd,previous_value=pv,
                       change_points=round(v-pv,4),change_basis='week_over_week_percentage_points',
                       note='Rates move in percentage points (100 bp = 1 pp), not percent.')
        out['age_days']=(now.date()-dt.date.fromisoformat(d)).days
        if out['age_days']>14: out['status']='overdue'
        return out
    extra=[
        ('gas','USD/MMBtu','EIA Henry Hub natural gas spot weekly average','https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDw.xls','weekly average, week ending Friday',lambda: wo.eia_weekly('RNGWHHD'),False),
        ('sp500','index points','S&P 500 daily closes (FRED SP500), completed-week average','https://fred.stlouisfed.org/series/SP500','completed-week average of daily closes, min 3 business days',lambda: wo.fred_daily_weekly('SP500'),False),
        ('dow','index points','Dow Jones daily closes (FRED DJIA), completed-week average','https://fred.stlouisfed.org/series/DJIA','completed-week average of daily closes, min 3 business days',lambda: wo.fred_daily_weekly('DJIA'),False),
        ('debt','USD trillion','US Treasury Debt to the Penny, end-of-week total public debt outstanding','https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/','end-of-week observation of a daily stock',wo.debt_weekly,False),
        ('fedassets','USD trillion','Fed total assets (FRED WALCL), source weekly stock','https://fred.stlouisfed.org/series/WALCL','source-published weekly stock',lambda: [(d,v/1e6) for d,v in wo.fred_weekly('WALCL')],False),
        ('fedtreas','USD trillion','Treasuries held by the Fed (FRED TREAST), source weekly stock','https://fred.stlouisfed.org/series/TREAST','source-published weekly stock',lambda: [(d,v/1e6) for d,v in wo.fred_weekly('TREAST')],False),
        ('mortgage','%','Freddie Mac PMMS 30Y fixed (FRED MORTGAGE30US)','https://fred.stlouisfed.org/series/MORTGAGE30US','source-published weekly average',lambda: wo.fred_weekly('MORTGAGE30US'),True),
        ('fedfunds','%','Fed funds effective rate (FRED DFF), completed-week average','https://fred.stlouisfed.org/series/DFF','completed-week average of daily data',lambda: wo.fred_daily_weekly('DFF'),True),
        ('ust10','%','US 10Y Treasury yield (FRED DGS10), completed-week average','https://fred.stlouisfed.org/series/DGS10','completed-week average of daily data',lambda: wo.fred_daily_weekly('DGS10'),True),
        ('real10','%','US 10Y TIPS real yield (FRED DFII10), completed-week average','https://fred.stlouisfed.org/series/DFII10','completed-week average of daily data',lambda: wo.fred_daily_weekly('DFII10'),True),
        ('curve','pp','10Y minus 2Y Treasury (FRED T10Y2Y), completed-week average','https://fred.stlouisfed.org/series/T10Y2Y','completed-week average of daily data',lambda: wo.fred_daily_weekly('T10Y2Y'),True),
    ]
    for rid,unit,source,url,frequency,fetch,is_rate in extra:
        try:
            pts=wo._cached(rid, fetch)
            result[rid]=rate_entry(pts,source,url,unit,frequency) if is_rate else entry(pts,source,url,unit,frequency)
        except Exception as e:
            result[rid]=dict(status='unavailable',source=source,source_url=url,error=str(e),checked_at=now.isoformat())
            print('::warning::Weekly '+rid+' unavailable: '+str(e))
    CORE=('gold','wti','brent','uranium')
    result['status']='available' if all(result.get(k,{}).get('status')=='available' for k in CORE) else 'partial'
    result['extended_coverage']='Extended weekly set covers rows with genuine weekly/daily free sources. Silver, TTF, coal, electricity, housing, M2, wages, CPI, credit/GDP, Case-Shiller, DXY and the gold/silver ratio stay monthly/quarterly: no genuine free weekly source. Weekly silver conversion does not exist, so weekly points carry no oz Ag value.'
    return result

def create(doc, prev, now, kind, source_commit, log=''):
    validate(doc)
    return dict(schema_version=1, kind=kind, snapshot_date=now.date().isoformat(), captured_at=now.isoformat(), timezone=str(TZ),
        complete=True, source_commit=source_commit, data_sha256=digest(doc), previous_snapshot=prev.get('_path') if prev else None,
        data=doc, series=metadata(doc,prev,now,log),
        weekly_prices=dict(status='not_collected'),
        notes=['Monday observation vintage for Wednesday issue. Use this exact snapshot for chart and text.',
               'New source observation, revision, unchanged and retrieval failure are different states.',
               'Baseline has no prior frozen Monday. Never infer zero weekly movement from unchanged monthly data.',
               'Percentage rates change in percentage points or basis points, not price percent.',
               'Quarterly dates are quarter-start labels, not single-month values. Proxy history and rights notices remain in the widget.',
               "Rows with 'weekly since' in their frequency carry genuine completed-week observations after their monthly history; silver denomination of those weekly points does not exist (no weekly silver source) and stays on the monthly cadence."])

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
        print('build_data.py starting', dt.datetime.now(TZ).isoformat(), flush=True)
        run=subprocess.run([sys.executable,str(ROOT/'scripts'/'build_data.py')],cwd=tmp,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=1500)
        print('build_data.py finished rc=%s' % run.returncode, dt.datetime.now(TZ).isoformat(), flush=True)
        print(run.stdout)
        if run.returncode: raise SystemExit('Builder failed; last valid live data/snapshots retained')
        doc=json.loads((Path(tmp)/'data.json').read_text())
        sys.path.insert(0,str(ROOT/'scripts'))
        import weekly_overlay
        print('weekly overlay starting', dt.datetime.now(TZ).isoformat(), flush=True)
        weekly_overlay.apply(doc, log=lambda m: print(m, flush=True))
        print('weekly overlay done', dt.datetime.now(TZ).isoformat(), flush=True)
        doc=validate(doc)
    snap=create(doc,prev,now,'monday' if args.publish else 'test',os.environ.get('GITHUB_SHA','local'),run.stdout)
    print('weekly_prices starting', dt.datetime.now(TZ).isoformat(), flush=True)
    snap['weekly_prices']=weekly_prices(now)
    print('weekly_prices done', dt.datetime.now(TZ).isoformat(), flush=True)
    manifest=dict(schema_version=1, snapshot_date=snap['snapshot_date'],captured_at=snap['captured_at'], complete=True, kind=snap['kind'],
        path=str(dest.relative_to(ROOT)), data_sha256=snap['data_sha256'],snapshot_sha256=digest(snap),previous_snapshot=snap['previous_snapshot'])
    atomic(dest,snap)
    if args.publish:
        atomic(ROOT/'data.json',doc); atomic(ROOT/'snapshots'/'latest.json',manifest)
    else: atomic(ROOT/'snapshots'/'test-latest.json',manifest)
    print('SNAPSHOT',json.dumps(manifest))

if __name__=='__main__': main()
