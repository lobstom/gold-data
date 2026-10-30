#!/usr/bin/env python3
"""LBR-only lumber monthly average. No LBS splice or index/retail proxy."""
import datetime as dt
import json, math, urllib.request
from zoneinfo import ZoneInfo
SOURCE = 'https://query1.finance.yahoo.com/v8/finance/chart/LBR=F'
HISTORY = 'https://finance.yahoo.com/quote/LBR%3DF/history/'
SPEC = 'https://www.cmegroup.com/articles/faqs/lumber-futures-faq.html'

def fetch_daily(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    start = int(dt.datetime(2022,8,8,tzinfo=dt.timezone.utc).timestamp())
    url = SOURCE + f'?period1={start}&period2={int(now.timestamp())}&interval=1d'
    req = urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=60) as r: x=json.load(r)['chart']['result'][0]
    assert x['meta']['symbol']=='LBR=F' and x['meta']['currency']=='USD'
    assert x['meta']['dataGranularity']=='1d', 'Daily data required; reject Yahoo downsampling'
    closes = x['indicators']['quote'][0]['close']; out={}
    for stamp,value in zip(x['timestamp'],closes):
        day=dt.datetime.fromtimestamp(stamp,ZoneInfo('America/New_York')).date()
        if day < dt.date(2022,8,8) or value is None: continue
        value=float(value)
        assert math.isfinite(value) and value>0
        if day.weekday()<5: out[day.isoformat()]=value
    assert len(out)>100, 'Insufficient LBR daily history'
    return out,url

def make_row(doc,daily,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    def monthly_metal(rid):
        row=next(r for r in doc['items'] if r['id']==rid)
        # A completed-week Friday can fall on the first of a month. Do not
        # mistake it for a monthly average if a failed base build is reused.
        cutoff=row.get('freq','').split('weekly since ')[-1] if 'weekly since ' in row.get('freq','') else '9999-12-31'
        return {p[0][:7]:p[2] for p in row['points'] if p[0].endswith('-01') and p[0]<cutoff}
    gold=monthly_metal('gold');silver=monthly_metal('silver')
    groups={}
    for day,v in sorted(daily.items()):
        month=day[:7]
        # Aug2022 is launch-partial; exclude it along with unfinished month.
        if month < '2022-09' or month>=now.strftime('%Y-%m'): continue
        groups.setdefault(month,[]).append(v)
    points=[]; counts={};r5=lambda v:float(f'{v:.5g}')
    for month,values in sorted(groups.items()):
        if len(values)<10 or month not in gold or month not in silver: continue
        g,s=gold[month],silver[month];u=sum(values)/len(values)
        assert g>0 and s>0
        points.append([month+'-01',r5(u/g),r5(u),r5(u/s)]);counts[month]=len(values)
    assert len(points)>=12, 'Insufficient matched complete-month LBR/metal history'
    last=points[-1];m=last[0][:7]
    note=('Yahoo Finance LBR=F rolling nearby lumber futures daily closes, averaged by completed month. '
          'USD per 1,000 board feet, NOT per 27,500-board-foot contract. Current CME LBR contract only; '
          'history starts September 2022, first full launch month. Legacy LBS ended May 2023 and is NOT spliced. '
          'Futures roll changes can affect returns; not a spot/retail lumber quote or investable total-return series. '
          'Gold and silver denominators are matching monthly model averages; no weekly metal substitution.')
    return dict(id='lumber',label='Lumber (LBR rolling futures; since Sep 2022)',unit='1,000 board ft',freq='monthly avg',
                asof=m,usd=last[2],goldusd=gold[m],ozau=last[1],ozag=last[3],points=points,
                source='Yahoo Finance LBR=F; CME lumber contract specifications',source_url=HISTORY,
                source_checked_at=now.isoformat(),source_note=note,monthly_daily_counts=counts)

def apply(doc,log=print,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    daily,url=fetch_daily(now);row=make_row(doc,daily,now);row['retrieval_url']=url
    old=next((r for r in doc['items'] if r['id']=='lumber'),None)
    # Atomic row replacement after complete fetch/validation only.
    doc['items']=[r for r in doc['items'] if r['id']!='lumber']
    pos=next((i+1 for i,r in enumerate(doc['items']) if r['id']=='coal'),len(doc['items']))
    doc['items'].insert(pos,row)
    log('Lumber: '+row['asof']+', '+str(len(row['points']))+' completed months; LBR only, no LBS splice')
    return row

if __name__=='__main__':
    import sys
    from pathlib import Path
    p=Path(sys.argv[1] if len(sys.argv)>1 else 'data.json');d=json.loads(p.read_text());apply(d)
    p.write_text(json.dumps(d,separators=(',',':'),allow_nan=False))
