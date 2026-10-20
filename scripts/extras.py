"""Extra rows and helper series for the Prices in Gold widget (CPI for the real-dollar mode, yield curve,
credit/GDP, gold:silver, gold:oil, NBER recessions). Called from build_data.py just before data.json is written."""
import csv, io, os, json, math

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
    # Case-Shiller national home price index relative to gold: both rebased to 100 in January 2000, shown as one fixed index row in every unit mode
    cs = dict(fred("CSUSHPINSA"))
    base = "2000-01-01"
    pts = []
    for d in sorted(cs):
        if d[:7] < cur and d in g and g[d] and base in cs and base in g:
            pts.append((d, (cs[d] / cs[base]) / (g[d] / g[base]) * 100, g[d]))
    if pts:
        more.append(dict(id="cshomegold", label="US home price index vs gold, Jan 2000 = 100", unit="index pt", freq="monthly (3-month average, published about two months late)",
                         asof=pts[-1][0][:7], usd=round(pts[-1][1], 3), goldusd=pts[-1][2], ozau=0, ozag=0, fixed=1,
                         note="US home price index vs gold: the S&P CoreLogic Case-Shiller US National Home Price Index (repeat sales of single-family homes, FRED CSUSHPINSA, from 1987) divided by the monthly average gold price, with both set to 100 in January 2000. It is an index, not ounces per home, and it is shown in index points in every unit mode. Case-Shiller is a three-month average and is revised.",
                         points=[[a, round(b, 3), round(b, 3), round(b, 3)] for a, b, _ in pts]))
    # NBER recession months (USREC), merged into [start, end] month ranges
    rec, start, prev = [], None, None
    for d, v in fred("USREC"):
        if v == 1 and start is None: start = d
        if v == 0 and start is not None: rec.append([start[:7], prev[:7]]); start = None
        prev = d
    if start: rec.append([start[:7], prev[:7]])
    doc["recessions"] = [r for r in rec if r[0] >= "1857"]
    extend_dxy(doc, get)
    extend_usd(doc)
    extend_v3(doc, get)
    return doc


DXY_W = dict(EUR=-0.576, JPY=0.136, GBP=-0.119, CAD=0.091, SEK=0.042, CHF=0.036)  # ICE DXY formula exponents
DXY_NOTE = ("US Dollar Index (DXY) is rebuilt from FRED exchange rates with the ICE DXY formula (from 1980) and spliced to the Fed major "
            "currencies index before 1980. It is shown in index points in every unit mode and is not the ICE-published series.")

def extend_dxy(doc, get):
    """US Dollar Index for the Compare menu only. Non-fatal: on any failure the previous dxy row is kept (or none) and a warning is printed.
    1980-01 on: ICE DXY formula (50.14348112 * EURUSD^-0.576 * USDJPY^0.136 * GBPUSD^-0.119 * USDCAD^0.091 * USDSEK^0.042 * USDCHF^0.036)
    on FRED G.5 monthly averages; euro = 1.95583 / DEM before 1999. Before 1980 (back to 1973-01): Fed major currencies index (DTWEXM,
    static monthly averages in scripts/dxy_pre1980.csv, Mar 1973 = 100, same base as ICE) multiplied by DXY(1980-01)/DTWEXM(1980-01)."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        def fred(sid):
            t = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}").decode()
            return {r[0][:7]: float(r[1]) for r in list(csv.reader(io.StringIO(t)))[1:] if len(r) > 1 and r[1] not in ("", ".")}
        eu, jp, uk, ca, sw, ch, dem = (fred(s) for s in ("EXUSEU", "EXJPUS", "EXUSUK", "EXCAUS", "EXSDUS", "EXSZUS", "EXGEUS"))
        cur = doc["updated"][:7]
        byid = {i["id"]: i for i in doc["items"]}
        g = {p[0][:7]: p[2] for p in byid["gold"]["points"]}
        sv = {p[0][:7]: p[2] for p in byid["silver"]["points"]}
        dxy = {}
        for m in sorted(jp):
            if m < "1980-01" or m >= cur: continue
            e = eu.get(m) or (1.95583 / dem[m] if m in dem and m < "1999-01" else None)
            if e is None or not all(m in x for x in (uk, ca, sw, ch)): continue
            dxy[m] = 50.14348112 * e ** DXY_W["EUR"] * jp[m] ** DXY_W["JPY"] * uk[m] ** DXY_W["GBP"] * ca[m] ** DXY_W["CAD"] * sw[m] ** DXY_W["SEK"] * ch[m] ** DXY_W["CHF"]
        if "1980-01" not in dxy or len(dxy) < 500: raise ValueError("too few DXY months: %d" % len(dxy))
        fed = {r["month"]: float(r["dtwexm_monthly_avg"]) for r in csv.DictReader(open(os.path.join(here, "dxy_pre1980.csv")))}
        k = dxy["1980-01"] / fed["1980-01"]
        series = [(m, fed[m] * k) for m in sorted(fed) if m < "1980-01"] + sorted(dxy.items())
        pts = []
        for m, v in series:
            if m not in g or m not in sv or not sv[m]: continue
            v = round(v, 3)
            pts.append([m + "-01", float(f"{v / g[m]:.5g}"), v, float(f"{v / sv[m]:.5g}")])
        if pts[0][0] != "1973-01-01" or not all(math.isfinite(x) and x > 0 for p in pts for x in p[1:]): raise ValueError("bad DXY series")
        last = pts[-1]
        doc["more"].append(dict(id="dxy", label="US Dollar Index", unit="index pt", freq="monthly avg", asof=last[0][:7], usd=last[2],
                                goldusd=g[last[0][:7]], ozau=last[1], ozag=last[3], fixed=1, points=pts, note=DXY_NOTE))
    except Exception as e:
        print("WARNING: DXY skipped, previous row kept if any:", e)
        try:
            old = json.load(open(os.path.join(here, "..", "data.json")))
            prev = [r for r in old.get("more", []) if r["id"] == "dxy"]
            doc["more"].extend(prev)
        except Exception as e2:
            print("WARNING: no previous DXY row:", e2)


USD_NOTE = ("US dollar priced in gold: 1 USD = 1 / gold price in USD. Derived from this page's gold row "
            "(same sources and dates: World Bank monthly averages, MeasuringWorth annual history before 1960); not a separate data series.")

def extend_usd(doc):
    """US dollar as a row: reciprocal of the gold row (oz Au and oz Ag per $1). Added to "more" so old cards
    ignore it. Non-fatal: on any failure the previous usd row is kept (or none) and a warning is printed."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        byid = {i['id']: i for i in doc['items']}
        r5 = lambda x: float(f'{x:.5g}')
        pts = []
        for p in byid['gold']['points']:
            dt, gu, ag = p[0], p[2], (p[3] if len(p) > 3 else None)
            if not gu: continue
            pts.append([dt, r5(1.0 / gu), 1.0, r5(ag / gu) if ag else None])
        if len(pts) < 100 or pts[-1][1] <= 0: raise ValueError('bad USD series: %d points' % len(pts))
        doc['more'].append(dict(id='usd', label='US dollar', unit='$1', freq='monthly avg', asof=byid['gold']['asof'],
                                usd=1.0, goldusd=byid['gold']['usd'], ozau=pts[-1][1], ozag=pts[-1][3], points=pts, note=USD_NOTE))
    except Exception as e:
        print('WARNING: USD row skipped, previous row kept if any:', e)
        try:
            old = json.load(open(os.path.join(here, '..', 'data.json')))
            doc['more'].extend([r for r in old.get('more', []) if r['id'] == 'usd'])
        except Exception as e2:
            print('WARNING: no previous USD row:', e2)


"""Staged v3 additions. Never modifies existing items/more, so v1/v2 cards ignore them.
Stock values: last weekly observation in each completed calendar month, or quarter end.
Gold/silver denominators: same end-month monthly averages, never future/backfilled prices.
USD trillion / billion troy ounces. Not physical gold holdings or reserve coverage.
"""
import csv, io, calendar, datetime

TIC = 'https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/'
def tic_quarters(get):
    """{'YYYY-MM-DD': {'tot': $bn, 'off': $bn}} for quarter-end months. slt_table5 (recent, latest revisions) overrides mfhhis01 (history)."""
    mon = ['Dec','Nov','Oct','Sep','Aug','Jul','Jun','May','Apr','Mar','Feb','Jan']
    qe = {'Mar': '03-31', 'Jun': '06-30', 'Sep': '09-30', 'Dec': '12-31'}
    out = {}
    rows = list(csv.reader(io.StringIO(get(TIC + 'mfhhis01.csv').decode('latin-1'))))
    yr = None
    for r in rows:
        if not r: continue
        k = r[0].strip()
        if k == 'Country' and len(r) > 1 and r[1].strip().isdigit(): yr = int(r[1])
        key = {'Grand Total': 'tot', 'For. Official': 'off'}.get(k)
        if key and yr:
            for m, v in zip(mon, r[1:13]):
                if m in qe:
                    try: out.setdefault(f'{yr}-{qe[m]}', {})[key] = float(v)
                    except ValueError: pass
    lines = [l.split('\t') for l in get(TIC + 'slt_table5.txt').decode('latin-1').splitlines()]
    hdr = next(l for l in lines if l[0] == 'Country')
    for l in lines:
        key = {'Grand Total': 'tot', 'Of Which: Foreign Official': 'off'}.get(l[0].strip())
        if not key: continue
        for d, v in zip(hdr[1:], l[1:]):
            d = d.strip()
            if len(d) == 7 and d[5:] in ('03', '06', '09', '12'):
                y, m = int(d[:4]), int(d[5:])
                try: out.setdefault(f'{y}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}', {})[key] = float(v)
                except ValueError: pass
    return out

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
    # Foreign holders: Treasury TIC "Major Foreign Holders of Treasury Securities" (Grand Total and Foreign Official),
    # quarter-end months, $ trillion. Appended as parts[6]=foreign official, parts[7]=foreign private/other.
    # The card reorders these and shows other domestic = other public - foreign. Failure is non-fatal (card handles rows without them).
    try:
        tic = tic_quarters(get)
        for r in debt['parts']:
            k = tic.get(r[0])
            if k and 'tot' in k and 'off' in k:
                r.extend([round(k['off']/1000, 4), round((k['tot']-k['off'])/1000, 4)])
                if r[3] - r[6] - r[7] < 0: raise ValueError('Foreign holdings exceed other public holders')
    except Exception as e:
        print('WARNING: TIC foreign holdings skipped:', e)
    debt['label'] = 'Who owns the federal debt (and the Fed\'s balance sheet)'
    debt['stack'] = True
    debt['note'] = 'Ownership split: approximate quarter end. Fed stocks use the last Wednesday in the quarter-end month. Foreign holders are US Treasury TIC estimates of foreign holdings of Treasury securities at quarter-end months (official vs private/other). Other domestic holders are a residual: total debt minus government accounts minus Fed Treasuries minus TIC foreign holdings. TIC and Treasury/Fed debt definitions differ, so the residual is approximate. Non-Treasury Fed assets are NOT federal debt. Dollar-equivalent gold, not gold owned.'
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
