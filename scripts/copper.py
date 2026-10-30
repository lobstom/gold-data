#!/usr/bin/env python3
"""World Bank Pink Sheet copper, unchanged USD/metric-tonne monthly benchmark."""
import datetime as dt,io,json,math,re,urllib.request
SOURCE='https://www.worldbank.org/en/research/commodity-markets'
NOTE='World Bank Pink Sheet copper monthly average, in USD per metric tonne. LME grade A copper, minimum 99.9935% purity, cathodes and wire bar shapes, settlement benchmark. History starts January 1960. Not a live quote, retail or scrap-copper price. Gold and silver use matching monthly averages.'
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read()
def fetch():
    import openpyxl
    page=get(SOURCE).decode('utf8','ignore')
    url=re.search(r'https://thedocs\.worldbank\.org[^"\x27 )<>]+Monthly\.xlsx',page).group(0)
    rows=list(openpyxl.load_workbook(io.BytesIO(get(url)),read_only=True,data_only=True)['Monthly Prices'].values)
    return rows,url
def make_row(doc,rows,url,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    c=rows[4].index('Copper');assert rows[5][c]=='($/mt)', 'Unexpected copper unit'
    def metal(rid):
        row=next(r for r in doc['items'] if r['id']==rid)
        cutoff=row.get('freq','').split('weekly since ')[-1] if 'weekly since ' in row.get('freq','') else '9999-12-31'
        return {p[0]:p[2] for p in row['points'] if p[0].endswith('-01') and p[0]<cutoff}
    gold,silver=metal('gold'),metal('silver');points=[];r5=lambda n:float(f'{n:.5g}')
    for r in rows[6:]:
        k=r[0]
        if not isinstance(k,str) or not re.fullmatch(r'\d{4}M\d{2}',k):continue
        day=k[:4]+'-'+k[5:]+'-01';u=r[c]
        if day[:7]>=now.strftime('%Y-%m') or day not in gold or day not in silver or not isinstance(u,(int,float)):continue
        g,s=gold[day],silver[day]
        assert all(math.isfinite(v) and v>0 for v in (u,g,s))
        points.append([day,r5(u/g),r5(u),r5(u/s)])
    points.sort();assert len(points)>=12 and len({p[0] for p in points})==len(points)
    p=points[-1]
    return dict(id='copper',label='Copper (LME grade A)',unit='tonne',freq='monthly avg',asof=p[0][:7],usd=p[2],goldusd=gold[p[0]],ozau=p[1],ozag=p[3],points=points,source='World Bank Pink Sheet',source_url=SOURCE,retrieval_url=url,source_note=NOTE,source_checked_at=now.isoformat())
def apply(doc,rows=None,url=None,now=None,log=print):
    if rows is None:rows,url=fetch()
    row=make_row(doc,rows,url,now)
    doc['items']=[r for r in doc['items'] if r['id']!='copper']
    pos=next((i+1 for i,r in enumerate(doc['items']) if r['id']=='silver'),len(doc['items']))
    doc['items'].insert(pos,row);log('Copper: '+row['asof']+', '+str(len(row['points']))+' matched completed months')
    return row
if __name__=='__main__':
    import sys
    p=sys.argv[1] if len(sys.argv)>1 else 'data.json';d=json.load(open(p));apply(d)
    with open(p,'w') as f:json.dump(d,f,separators=(',',':'),allow_nan=False)
