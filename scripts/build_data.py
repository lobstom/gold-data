#!/usr/bin/env python3
"""Builds data.json for the Priced in Gold widget. Keyless sources only:
World Bank Pink Sheet (monthly xlsx), FRED MSPUS CSV, EIA bulk ELEC.zip."""
import csv, io, json, os, re, urllib.request, zipfile, datetime
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
                      goldusd=pts[-1][3], ozau=pts[-1][1], points=[[a, b, c] for a, b, c, _ in pts]))
# gold first: priced in USD (its oz Au value is 1 by definition), so the chart shows the USD price
gp = [(d(k), 1.0, v, v) for k, v in gold.items()]
add("gold", "Gold", "oz", "monthly avg", gp)
items[-1]["usdchart"] = True
items[-1]["points"] = [[a, 1.0, c] for a, _, c, _ in gp]
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
pts_housing = pts
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

# mortgage rate: Freddie Mac PMMS 30Y fixed via FRED, weekly (publishing permission is the site owner's to arrange)
pts = []
for dt, v in list(csv.reader(io.StringIO(get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US").decode())))[1:]:
    if v and v != ".": pts.append((dt, float(v)))
items.append(dict(id="mortgage", kind="rate", label="US 30Y mortgage rate (Freddie Mac)", unit="%", freq="weekly", asof=pts[-1][0], usd=pts[-1][1], goldusd=0, ozau=0,
                  prev=pts[-53][1] if len(pts) > 52 else None, points=[[a, b] for a, b in pts]))

# uranium: Cameco month-end spot history (scraped, no login; snapshot in scripts/cameco.csv as fallback)
# + latest UxC weekly readings from scripts/uranium.csv (typed in by the account holder)
import os
here = os.path.dirname(os.path.abspath(__file__))
cam = {}
try:
    html = get("https://www.cameco.com/invest/markets/uranium-price", 60).decode("utf8", "ignore")
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        tds = [re.sub(r"<[^>]+>", "", t).strip() for t in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) >= 2 and re.match(r"\d{4}/\d{2}/\d{2}$", tds[0]):
            try: cam[tds[0].replace("/", "-")] = float(tds[1])
            except ValueError: pass
    if len(cam) > 400:
        with open(os.path.join(here, "cameco.csv"), "w") as f:
            f.write("date,usd_per_lb\n" + "".join(f"{k},{v}\n" for k, v in sorted(cam.items())))
    else: cam = {}
except Exception as e:
    print("cameco scrape failed:", e); cam = {}
if not cam:
    for row in csv.reader(open(os.path.join(here, "cameco.csv"))):
        if row and row[0][:1].isdigit(): cam[row[0]] = float(row[1])
last_gold = gold[max(gold)]
mon = {k[:7]: (k, v) for k, v in cam.items()}
latest = None
up = os.path.join(here, "uranium.csv")
if os.path.exists(up):
    ux = sorted((r[0], float(r[1])) for r in csv.reader(open(up)) if r and r[0][:1].isdigit())
    last_cam = max(mon)
    for dt, v in ux:
        if dt[:7] > last_cam: mon[dt[:7]] = (dt, v)  # last UxC weekly reading in each month after Cameco's last
    if ux: latest = ux[-1]
pts = []
for m, (dt, v) in sorted(mon.items()):
    g = gold.get(f"{m[:4]}M{m[5:7]}", last_gold); pts.append((dt, v / g, v, g))
if pts:
    add("uranium", "Uranium U3O8 (spot)", "lb", "month-end history, latest UxC weekly", pts)
    if latest: items[-1]["asof"] = latest[0]
# long-run history (annual early points, fixed files built once; see footer for sources), prepended before each series starts
H = json.load(open(os.path.join(here, "history.json")))
gann = {}
for k, v in gold.items(): gann.setdefault(int(k[:4]), []).append(v)
gann = {y: sum(v) / len(v) for y, v in gann.items()}
for dt, v in H["gold"]: gann.setdefault(int(dt[:4]), v)
byid = {i["id"]: i for i in items}
for id in ("gold", "silver", "wti", "brent", "gas", "elec"):
    it = byid[id]; first = it["points"][0][0]
    hp = [[dt, 1.0 if id == "gold" else v / gann[int(dt[:4])], v] for dt, v in H[id] if dt < first]
    it["points"] = hp + it["points"]
hs = byid["housing"]; first = hs["points"][0][0]
idx = [(dt, v) for dt, v in H["housing_index"] if dt < first]
scale = hs["usd"] and None
mspus_first = [p for p in pts_housing if p[0] == first][0][2]
scale = mspus_first / idx[-1][1]
hs["points"] = [[dt, v * scale / gann[int(dt[:4])], v * scale] for dt, v in idx] + hs["points"]
u = byid["ust10"]; first = u["points"][0][0]
u["points"] = [[dt, v] for dt, v in H["ust10"] if dt < first] + u["points"]
# priced in silver: oz Ag per unit for the latest value (silver from the same Pink Sheet month, quarter average for housing)
sc = col("Silver")
silv = {r[0]: num(r[sc]) for r in data if r[0] and num(r[sc])}
last_silv = silv[max(silv)]
for it in items:
    if it.get("kind"): continue
    a = it["asof"]; y, m = a[:4], int(a[5:7])
    ks = [f"{y}M{mm:02d}" for mm in ((m, m + 1, m + 2) if it["id"] == "housing" else (m,))]
    sv = [silv[k] for k in ks if k in silv]
    it["ozag"] = it["usd"] / (sum(sv) / len(sv) if len(sv) == len(ks) else last_silv)
# per-point oz Ag and compact rounding: points are [date, oz Au, USD, oz Ag]
sp = {p[0]: p[2] for p in byid["silver"]["points"]}
def silv_at(dt, quarter):
    if quarter:
        y, m = int(dt[:4]), int(dt[5:7]); ks = [f"{y}-{mm:02d}-01" for mm in (m, m + 1, m + 2)]
        v = [sp[k] for k in ks if k in sp]
        if len(v) == len(ks): return sum(v) / len(v)
    if dt in sp: return sp[dt]
    k = dt[:7] + "-01"
    return sp.get(k, last_silv)
r5 = lambda x: float(f"{x:.5g}")
for it in items:
    if it.get("kind"): continue
    q = it["id"] == "housing"
    it["points"] = [[dt, r5(o), r5(u), r5(u / silv_at(dt, q))] for dt, o, u in it["points"]]
order = ["gold", "silver", "uranium", "wti", "brent", "gas", "ttf", "coal", "elec", "housing", "mortgage", "fedfunds", "ust10", "real10"]
items.sort(key=lambda i: order.index(i["id"]) if i["id"] in order else 99)
json.dump({"updated": datetime.date.today().isoformat(), "items": items}, open("data.json", "w"), separators=(",", ":"))
print("ok", [(i["id"], i["asof"]) for i in items])
