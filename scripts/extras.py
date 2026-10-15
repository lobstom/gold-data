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
    return doc
