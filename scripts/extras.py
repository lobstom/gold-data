"""Extra rows and helper series for the Prices in Gold widget (CPI for the real-dollar mode, yield curve,
credit/GDP, gold:silver, gold:oil, NBER recessions). Called from build_data.py just before data.json is written."""
import csv, io

def extend(doc, get):
    def fred(sid, extra=""):
        t = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}{extra}").decode()
        return [(r[0], float(r[1])) for r in list(csv.reader(io.StringIO(t)))[1:] if len(r) > 1 and r[1] not in ("", ".")]
    items = doc["items"]; byid = {i["id"]: i for i in items}
    more = doc["more"] = []  # kept apart from "items" so the older widget card ignores the new rows
    cur = doc["updated"][:7]
    def rate(id, label, unit, freq, pts, sfx="%", dec=2):
        pts = [(d, v) for d, v in pts if d[:7] < cur]
        if not pts: return
        more.append(dict(id=id, kind="rate", label=label, unit=unit, freq=freq, asof=pts[-1][0][:7], usd=pts[-1][1], goldusd=0, ozau=0,
                          prev=pts[-13][1] if len(pts) > 12 else None, sfx=sfx, dec=dec, points=[[a, round(b, 4)] for a, b in pts]))
    # yield curve: 10Y minus 2Y, monthly average of daily data, from 1976
    rate("curve", "Yield curve: 10Y minus 2Y Treasury (pp)", "pp", "monthly avg", fred("T10Y2Y", "&fq=Monthly&fam=avg"), sfx=" pp")
    # total credit market debt (Fed Z.1, $ million) over GDP (BEA, $ billion), quarterly
    gdp = dict(fred("GDP"))
    rate("credit", "US total credit market debt / GDP", "%", "quarterly", [(d, v / 1000 / gdp[d] * 100) for d, v in fred("TCMDO") if d in gdp], sfx="%", dec=0)
    # CPI (all items, NSA, from 1913); also drives the real-dollar mode
    rate("cpi", "US CPI (all items, 1982-84=100)", "index", "monthly", fred("CPIAUCNS"), sfx="", dec=1)
    # ratios computed from rows already built
    def usd(id): return {p[0]: p[2] for p in byid[id]["points"]}
    g, s, o = usd("gold"), usd("silver"), usd("wti")
    rate("gsr", "Gold / silver ratio (oz Ag per oz Au)", "ratio", "monthly avg", [(d, g[d] / s[d]) for d in sorted(g) if d in s and s[d]], sfx="", dec=1)
    rate("goldoil", "Gold / oil ratio (WTI bbl per oz Au)", "ratio", "monthly avg", [(d, g[d] / o[d]) for d in sorted(g) if d in o and o[d]], sfx="", dec=1)
    # NBER recession months (USREC), merged into [start, end] month ranges
    rec, start, prev = [], None, None
    for d, v in fred("USREC"):
        if v == 1 and start is None: start = d
        if v == 0 and start is not None: rec.append([start[:7], prev[:7]]); start = None
        prev = d
    if start: rec.append([start[:7], prev[:7]])
    doc["recessions"] = [r for r in rec if r[0] >= "1857"]
    extend_v3(doc, get)
    return doc


"""Staged v3 additions. Never modifies existing items/more, so v1/v2 cards ignore them.
Stock values: last weekly observation in each completed calendar month, or quarter end.
Gold/silver denominators: same end-month monthly averages, never future/backfilled prices.
USD trillion / billion troy ounces. Not physical gold holdings or reserve coverage.
"""
import csv, io, calendar, datetime

def extend_v3(doc, get):
    byid = {i['id']: i for i in doc['items']}
    gold = {p[0][:7]: p[2] for p in byid['gold']['points'] if p[0] >= '1960-01-01'}
    silver = {p[0][:7]: p[2] for p in byid['silver']['points'] if p[0] >= '1960-01-01'}
    rows_out = doc['more_v3'] = []
    cur = doc['updated'][:7]
    def fred(sid):
        t = get('https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + sid).decode()
        return [(r[0], float(r[1])) for r in list(csv.reader(io.StringIO(t)))[1:] if len(r) > 1 and r[1] not in ('', '.')]
    def stock(id, label, sid, quarterly=False):
        observations = {}
        for d, millions in fred(sid):
            y, m = int(d[:4]), int(d[5:7])
            if quarterly: m += 2  # FRED labels end-quarter stocks with the quarter-start date
            month = f'{y:04d}-{m:02d}'
            if month >= cur or month not in gold or month not in silver: continue
            end = f'{month}-{calendar.monthrange(y,m)[1]:02d}'
            observations[month] = (end if quarterly else d, millions)
        pts = []
        for month,(d,v) in sorted(observations.items()):
            pts.append([d, v/1000/gold[month], v/1e6, v/1000/silver[month]])
        if not pts: raise ValueError('No matching metal history for ' + sid)
        p = pts[-1]
        rows_out.append(dict(id=id,label=label,unit='total',freq='quarter-end stock' if quarterly else 'month-end: last weekly stock',
            asof=p[0],usd=p[2],ozau=p[1],ozag=p[3],goldusd=gold[p[0][:7]],big=1,points=pts,source=sid,
            note='Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.'))
    stock('fedassets','Fed total assets','WALCL')
    stock('fedtreas','Treasuries held by the Fed','TREAST')
    stock('publicdebt','Federal debt held by the public','FYGFDPUN',True)
    stock('govdebt','Federal debt held by government accounts','FDHBATN',True)
    doc['v3_notes'] = {'uranium': 'Latest uranium may use an earlier month\'s average metal price. This is not a same-day spot ratio.',
        'overlap': 'Fed Treasuries are part of Fed assets and public debt; public debt includes Fed and foreign holders. Government-account debt plus public debt equals total debt at matching dates. Do not add overlapping rows.'}
    # Correct the pre-existing total debt's quarter-start labels only for v3 readers.
    # Keep original items byte-equivalent for the live v1 card and held v2 card.
    stock('debt','US federal debt','GFDEBTN',True)
    debt = rows_out.pop()
    debt['points'] = [p for p in byid['debt']['points'] if p[0] < '1966-01-01'] + debt['points']
    debt['freq'] = 'quarter-end stock (annual before 1966)'
    doc['overrides_v3'] = {'debt': debt}
    # Ownership split on shared quarter ends. Fed is the final Wednesday observation
    # in the quarter-end month: explicitly approximate, with actual dates preserved.
    fed = dict(fred('TREAST')); assets = dict(fred('WALCL'))
    monthly = {}
    for d in sorted(set(fed) & set(assets)):
        monthly[d[:7]] = (d, fed[d], assets[d])
    public = {p[0]:p[2] for p in next(i for i in rows_out if i['id']=='publicdebt')['points']}
    government = {p[0]:p[2] for p in next(i for i in rows_out if i['id']=='govdebt')['points']}
    debt['parts'] = []
    for p in debt['points']:
        d = p[0]
        if d not in public or d not in government or d[:7] not in monthly: continue
        fd, f, a = monthly[d[:7]]
        f /= 1e6; a /= 1e6
        rest = p[2]-government[d]-f  # residual against the authoritative displayed total
        if min(government[d],f,rest,a-f) < 0: raise ValueError('Negative ownership component')
        debt['parts'].append([d,government[d],f,rest,a-f,fd])
    debt['label'] = 'Who owns the federal debt (and the Fed\'s balance sheet)'
    debt['stack'] = True
    debt['note'] = 'Ownership split: approximate quarter end. Fed stocks use the last Wednesday in the quarter-end month; other public holders are residual total debt minus government accounts minus Fed Treasuries; historical source revisions may differ from the separately published public-debt series. Non-Treasury Fed assets are NOT federal debt. Dollar-equivalent gold, not gold owned.'
    # FHFA MIRS Table 9, annual all-term conventional contract rates, not PMMS.
    # Official workbook: https://www.fhfa.gov/sites/default/files/Table9-2018-by-Year.xls
    # Midyear dates represent annual means, not a dated weekly quote.
    mirs = [(1963,5.90),(1964,5.85),(1965,5.83),(1966,6.26),(1967,6.38),(1968,6.88),(1969,7.67),(1970,8.22)]
    mortgage = dict(byid['mortgage'])
    mortgage['points'] = [[f'{y}-07-01',v] for y,v in mirs] + mortgage['points']
    mortgage['label'] = '30Y mortgage (PMMS); all-term MIRS proxy before 1971'
    mortgage['freq'] = 'weekly PMMS; annual all-term proxy 1963-1970'
    mortgage['proxy_source'] = 'FHFA MIRS Table 9: annual conventional all-term contract rate, not effective rate or a 30-year rate'
    doc['overrides_v3']['mortgage'] = mortgage
