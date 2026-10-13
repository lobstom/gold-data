#!/usr/bin/env python3
"""Builds data.json for the Priced in Gold widget. Keyless sources only:
World Bank Pink Sheet (monthly xlsx), FRED MSPUS CSV, EIA bulk ELEC.zip."""
import csv, io, json, re, urllib.request, zipfile, datetime
import openpyxl

def get(url, timeout=300):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8.0"}), timeout=timeout).read()

page = get("https://www.worldbank.org/en/research/commodity-markets").decode("utf8", "ignore")
url = re.search(r"https://thedocs\.worldbank\.org[^\"' )<>]+Monthly\.xlsx", page).group(0)
ws = openpyxl.load_workbook(io.BytesIO(get(url)), read_only=True, data_only=True)["Monthly Prices"]
rows = list(ws.iter_rows(values_only=True))
hdr = rows[4]; data = rows[6:]
def col(name):  # exact header match, e.g. 'Gold'
    return hdr.index(name)
def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
gc = col("Gold")
gold = {r[0]: num(r[gc]) for r in data if r[0] and num(r[gc])}
d = lambda k: f"{k[:4]}-{k[5:]}-01"

def series(c, mult=1.0):
    pts = []
    for r in data:
        v = num(r[c]) if r[0] else None
        if v and gold.get(r[0]): pts.append((d(r[0]), v * mult / gold[r[0]], v * mult, gold[r[0]]))
    return pts

items = []
def add(id, label, unit, freq, pts):
    items.append(dict(id=id, label=label, unit=unit, freq=freq, asof=pts[-1][0][:7], usd=pts[-1][2],
                      goldusd=pts[-1][3], ozau=pts[-1][1], points=[[a, b] for a, b, _, _ in pts]))
# gold first: priced in USD (its oz Au value is 1 by definition), so the chart shows the USD price
gp = [(d(k), 1.0, v, v) for k, v in gold.items()]
add("gold", "Gold", "oz", "monthly avg", gp)
items[-1]["usdchart"] = True
items[-1]["points"] = [[a, c] for a, _, c, _ in gp]
for id, label, unit, name in [("silver", "Silver", "oz", "Silver"), ("wti", "Crude oil (WTI)", "bbl", "Crude oil, WTI"),
        ("brent", "Crude oil (Brent)", "bbl", "Crude oil, Brent"),
        ("gas", "Natural gas (US)", "MMBtu", "Natural gas, US"), ("ttf", "Natural gas (Europe, TTF)", "MMBtu", "Natural gas, Europe"),
        ("coal", "Coal (Australian, Newcastle)", "tonne", "Coal, Australian")]:
    add(id, label, unit, "monthly avg", series(col(name)))

# housing: FRED MSPUS quarterly, gold = mean of the quarter's three monthly averages
pts = []
for dt, v in list(csv.reader(io.StringIO(get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=MSPUS").decode())))[1:]:
    if not v or v == ".": continue
    y, m, _ = dt.split("-"); m = int(m)
    g = [gold[k] for k in (f"{y}M{mm:02d}" for mm in (m, m + 1, m + 2)) if k in gold]
    if len(g) == 3: pts.append((dt, float(v) / (sum(g) / 3), float(v), sum(g) / 3))
add("housing", "US median home price", "home", "quarterly", pts)

# electricity: EIA bulk, cents/kWh -> $/MWh
z = zipfile.ZipFile(io.BytesIO(get("https://www.eia.gov/opendata/bulk/ELEC.zip")))
pts = []
with z.open("ELEC.txt") as f:
    for line in f:
        if line.startswith(b'{"series_id":"ELEC.PRICE.US-ALL.M"'):
            for k, v in sorted(json.loads(line)["data"]):
                g = gold.get(f"{k[:4]}M{k[4:]}")
                if v is not None and g: pts.append((f"{k[:4]}-{k[4:]}-01", v * 10 / g, v * 10, g))
            break
add("elec", "US electricity (all sectors)", "MWh", "monthly avg", pts)

# rates (percent, not priced in gold): Federal Reserve H.15 via FRED, monthly averages of daily data
today = datetime.date.today().strftime("%Y-%m")
for id, label, sid in [("fedfunds", "Fed funds rate (effective)", "FEDFUNDS"), ("ust10", "US 10Y Treasury yield", "DGS10"),
                       ("real10", "US 10Y real yield (TIPS)", "DFII10")]:
    pts = []
    for dt, v in list(csv.reader(io.StringIO(get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&fq=Monthly&fam=avg").decode())))[1:]:
        if v and v != "." and dt[:7] < today: pts.append((dt, float(v), float(v), 0))
    items.append(dict(id=id, kind="rate", label=label, unit="%", freq="monthly avg", asof=pts[-1][0][:7], usd=pts[-1][1], goldusd=0, ozau=0,
                      prev=pts[-13][1] if len(pts) > 12 else None, points=[[a, b] for a, b, _, _ in pts]))

# uranium: manual weekly entries in scripts/uranium.csv (date,usd_per_lb), typed in by the account holder
import os
up = os.path.join(os.path.dirname(__file__), "uranium.csv")
if os.path.exists(up):
    last_gold = gold[max(gold)]; pts = []
    for row in csv.reader(open(up)):
        if not row or not row[0][:1].isdigit(): continue
        dt, v = row[0], float(row[1]); g = gold.get(f"{dt[:4]}M{dt[5:7]}", last_gold)
        pts.append((dt, v / g, v, g))
    if pts: add("uranium", "Uranium U3O8 (UxC weekly)", "lb", "weekly, delayed up to 72h", sorted(pts))

json.dump({"updated": datetime.date.today().isoformat(), "items": items}, open("data.json", "w"), separators=(",", ":"))
print("ok", [(i["id"], i["asof"]) for i in items])
