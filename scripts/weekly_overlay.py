#!/usr/bin/env python3
"""Weekly overlay for the Prices in Gold widget.

Appends genuine completed-week observations (Friday-labeled; at least 3 business
days for averages) to supported rows after their monthly/quarterly history. No
weekly point is ever inferred from a monthly source: rows without a true
weekly/daily source keep their existing cadence.

Conventions:
- Gold conversion uses the same week's World Gold Council weekly average
  (completed-week average of available daily observations), never a
  forward-filled monthly average.
- Silver conversion: there is no free weekly silver source, so weekly points
  carry null for oz Ag. The widget skips null point values, so silver
  denomination honestly ends at the last monthly point. Row-level ozag keeps
  the last monthly conversion. This is stated in doc['weekly_notes'].
- Stocks (debt, Fed balance sheet) are end-of-week or source-published weekly
  observations, not averages.

Imported by weekly_snapshot.py after build_data.py; also runnable standalone:
    python scripts/weekly_overlay.py path/to/data.json
"""
import csv, datetime as dt, io, json, math, os, subprocess, sys, urllib.request

MIN_OBS = 3  # business days required for a completed week


def _get(url, timeout=120, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "gold-data weekly overlay"})
    data = urllib.request.urlopen(req, timeout=timeout).read()
    return data if binary else data.decode("utf8", "ignore")


def _fred(sid, cosd=None, min_rows=8, never_flat=False):
    """FRED fredgraph.csv -> [(date, value)] with bot-block/garbage guards.

    Raises (so the caller skips the row and keeps known-good history) when the
    response looks like a block page or degraded content instead of a real
    series: malformed rows, too few usable rows, or - only for series that
    cannot legitimately be flat - a single distinct value across the window.
    """
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
    if cosd:
        url += "&cosd=" + cosd
    out = []
    for r in list(csv.reader(io.StringIO(_get(url))))[1:]:
        if len(r) < 2 or r[1] in ("", "."):
            continue
        try:
            out.append((dt.date.fromisoformat(r[0].strip()), float(r[1])))
        except ValueError:
            raise ValueError(f"FRED {sid}: malformed row {r[:2]!r} (possible bot-block page)")
    if len(out) < min_rows:
        raise ValueError(f"FRED {sid}: only {len(out)} usable rows, expected >= {min_rows} (possible bot-block page)")
    if never_flat and len({v for _, v in out}) < 2:
        raise ValueError(f"FRED {sid}: single distinct value across window (possible bot-block page)")
    return out


def _weeks(daily):
    """Sorted daily (date, value) -> [(friday_iso, avg, n_obs)] for completed weeks."""
    groups = {}
    for d, v in daily:
        if d.weekday() > 4:
            continue
        friday = d + dt.timedelta(days=4 - d.weekday())
        groups.setdefault(friday, []).append(v)
    today = dt.date.today()
    return [(f.isoformat(), sum(v) / len(v), len(v)) for f, v in sorted(groups.items())
            if f < today and len(v) >= MIN_OBS]


def wgc_weekly_gold(since):
    """WGC daily gold -> [(friday_iso, weekly_avg)] for completed weeks from `since` (date)."""
    start = since - dt.timedelta(days=10)
    stamp = int(dt.datetime.combine(start, dt.time(), tzinfo=dt.timezone.utc).timestamp() * 1000)
    url = f"https://fsapi.gold.org/api/goldprice/v11/chart/price/usd/oz/{stamp},"
    raw = json.loads(subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--location", "--max-time", "90", url],
        check=True, stdout=subprocess.PIPE, text=True, timeout=100).stdout)
    days = {}
    for t, v in raw["chartData"]["USD"]:
        if v is not None:
            days[dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).date()] = float(v)
    return [(f, a) for f, a, _ in _weeks(sorted(days.items()))]


def eia_weekly(code):
    """EIA weekly xls (RWTC, RBRTE under /pet/; RNGWHHD under /ng/) -> [(date_iso, value)]."""
    import xlrd
    base = "https://www.eia.gov/dnav/ng/hist_xls/" if code == "RNGWHHD" else "https://www.eia.gov/dnav/pet/hist_xls/"
    book = xlrd.open_workbook(file_contents=_get(base + code + "w.xls", binary=True))
    sheet = book.sheet_by_name("Data 1")
    pts = []
    for i in range(3, sheet.nrows):
        if sheet.cell_type(i, 0) == xlrd.XL_CELL_DATE and isinstance(sheet.cell_value(i, 1), (float, int)):
            pts.append((xlrd.xldate_as_datetime(sheet.cell_value(i, 0), book.datemode).date().isoformat(),
                        float(sheet.cell_value(i, 1))))
    return pts


def fred_daily_weekly(sid):
    """FRED daily series -> completed-week averages [(friday_iso, avg)]. Recent window only."""
    cosd = (dt.date.today() - dt.timedelta(days=75)).isoformat()
    volatile = sid in ("SP500", "DJIA")  # equity indexes are never flat for 75 days
    return [(f, a) for f, a, _ in _weeks(_fred(sid, cosd, min_rows=40, never_flat=volatile))]


def fred_weekly(sid):
    """FRED weekly series, source-published observations [(date_iso, value)]."""
    return [(d.isoformat(), v) for d, v in _fred(sid, min_rows=8)]


def debt_weekly():
    """Treasury Debt to the Penny (daily stock) -> last observation per completed week, $ trillion."""
    out, page = {}, 1
    while True:
        url = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny"
               f"?sort=-record_date&fields=record_date,tot_pub_debt_out_amt&page[size]=400&page[number]={page}")
        rows = json.loads(_get(url)).get("data", [])
        if not rows:
            break
        for r in rows:
            d = dt.date.fromisoformat(r["record_date"])
            if d.weekday() > 4:
                continue
            friday = d + dt.timedelta(days=4 - d.weekday())
            out.setdefault(friday, float(r["tot_pub_debt_out_amt"]))  # newest first: last obs of week
        if len(rows) < 400 or dt.date.fromisoformat(rows[-1]["record_date"]) < dt.date.today() - dt.timedelta(days=120):
            break
        page += 1
    today = dt.date.today()
    return [(f.isoformat(), v / 1e12) for f, v in sorted(out.items()) if f < today]


def _r5(x):
    return float(f"{x:.5g}")


# price rows: weekly points [date, ozAu, USD, null]. big rows price in billion oz (USD in $T).
# each: (source description, fetcher -> [(friday_iso, usd_value)])
PRICE_ROWS = {
    "wti": ("EIA WTI Cushing spot weekly average", lambda: eia_weekly("RWTC")),
    "brent": ("EIA Europe Brent spot weekly average", lambda: eia_weekly("RBRTE")),
    "gas": ("EIA Henry Hub natural gas spot weekly average", lambda: eia_weekly("RNGWHHD")),
    "sp500": ("S&P 500 daily closes (FRED SP500), completed-week average", lambda: fred_daily_weekly("SP500")),
    "dow": ("Dow Jones daily closes (FRED DJIA), completed-week average", lambda: fred_daily_weekly("DJIA")),
    "debt": ("US Treasury Debt to the Penny, end-of-week total public debt outstanding", debt_weekly),
    "fedassets": ("Fed total assets (FRED WALCL), source weekly stock", lambda: [(d, v / 1e6) for d, v in fred_weekly("WALCL")]),
    "fedtreas": ("Treasuries held by the Fed (FRED TREAST), source weekly stock", lambda: [(d, v / 1e6) for d, v in fred_weekly("TREAST")]),
}
# rate rows (kind=rate, 2-tuples): no gold conversion
RATE_ROWS = {
    "fedfunds": ("Fed funds effective rate (FRED DFF), completed-week average", lambda: fred_daily_weekly("DFF")),
    "ust10": ("US 10Y Treasury yield (FRED DGS10), completed-week average", lambda: fred_daily_weekly("DGS10")),
    "real10": ("US 10Y TIPS real yield (FRED DFII10), completed-week average", lambda: fred_daily_weekly("DFII10")),
    "curve": ("10Y minus 2Y Treasury (FRED T10Y2Y), completed-week average", lambda: fred_daily_weekly("T10Y2Y")),
}


CACHE = {}

def _cached(key, fetch):
    if key not in CACHE:
        t0 = dt.datetime.now()
        CACHE[key] = fetch()
        print(f"fetch {key}: {len(CACHE[key])} points in {(dt.datetime.now()-t0).total_seconds():.1f}s", flush=True)
    return CACHE[key]


def _month_end(iso):
    y, m = int(iso[:4]), int(iso[5:7])
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return (dt.date(ny, nm, 1) - dt.timedelta(days=1)).isoformat()


def apply(doc, log=print):
    """Append weekly points to supported rows of a built data.json doc. Returns applied row ids.
    Weekly points start after the month of each row's last existing point, so a weekly
    observation never duplicates a period its monthly/quarterly history already covers.
    The debt row the widget displays is overrides_v3['debt']; that copy gets the overlay."""
    byid = {r["id"]: r for r in doc["items"] + doc.get("more", []) + doc.get("more_v3", [])}
    byid.update(doc.get("overrides_v3", {}))
    gold_row = byid["gold"]
    last_monthly_gold_date = gold_row["points"][-1][0]

    gw = wgc_weekly_gold(dt.date.fromisoformat(last_monthly_gold_date))
    if not gw:
        raise ValueError("WGC weekly gold unavailable; refusing to overlay without a gold anchor")
    gold_weekly = dict(gw)
    log(f"weekly gold anchor: {len(gw)} completed weeks, latest {gw[-1][0]} = {gw[-1][1]:.2f}")

    applied = []

    # gold row itself: [date, 1.0, USD, null] (no weekly silver for oz Ag)
    gold_cutoff = _month_end(last_monthly_gold_date)
    new = [(f, a) for f, a in gw if f > gold_cutoff]
    if new:
        gold_row["points"] += [[f, 1.0, _r5(a), None] for f, a in new]
        gold_row.update(asof=new[-1][0], usd=_r5(new[-1][1]), goldusd=_r5(new[-1][1]),
                        freq="monthly avg; weekly since " + new[0][0])
        applied.append("gold")

    for rid, (src, fetch) in PRICE_ROWS.items():
        row = byid.get(rid)
        if not row:
            log(f"::warning::{rid}: row not found, skipped")
            continue
        try:
            pts = _cached(rid, fetch)
        except Exception as e:
            log(f"::warning::{rid} weekly fetch failed ({src}): {e}; row left on existing cadence")
            continue
        big = 1000.0 if row.get("big") else 1.0  # big rows: USD in $T, oz in billions
        cutoff = _month_end(row["points"][-1][0])
        new = [(f, v * big / gold_weekly[f], v) for f, v in pts if f in gold_weekly and f > cutoff]
        if not new:
            log(f"{rid}: no new completed weeks")
            continue
        row["points"] += [[f, _r5(o), _r5(u), None] for f, o, u in new]
        row.update(asof=new[-1][0], usd=_r5(new[-1][2]), goldusd=_r5(gold_weekly[new[-1][0]]),
                   ozau=_r5(new[-1][1]),
                   freq=row["freq"] + "; weekly since " + new[0][0])
        applied.append(rid)

    for rid, (src, fetch) in RATE_ROWS.items():
        row = byid.get(rid)
        if not row:
            log(f"::warning::{rid}: row not found, skipped")
            continue
        try:
            pts = fetch()
        except Exception as e:
            log(f"::warning::{rid} weekly fetch failed ({src}): {e}; row left on existing cadence")
            continue
        cutoff = _month_end(row["points"][-1][0])
        new = [(f, v) for f, v in pts if f > cutoff]
        if not new:
            log(f"{rid}: no new completed weeks")
            continue
        row["points"] += [[f, round(v, 4)] for f, v in new]
        row.update(asof=new[-1][0], usd=round(new[-1][1], 4),
                   freq=row["freq"] + "; weekly since " + new[0][0])
        applied.append(rid)

    # derived weekly: US dollar row (inverse of weekly gold); oz Ag leg stays null
    usd_row = byid.get("usd")
    if usd_row and "gold" in applied:
        usd_cutoff = _month_end(usd_row["points"][-1][0])
        new = [(f, 1.0 / a) for f, a in gw if f > usd_cutoff]
        if new:
            usd_row["points"] += [[f, _r5(o), 1.0, None] for f, o in new]
            usd_row.update(asof=new[-1][0], ozau=_r5(new[-1][1]),
                           freq="monthly avg; weekly since " + new[0][0])
            applied.append("usd")
    # gold/oil ratio from two genuine weekly series
    go_row = byid.get("goldoil")
    if go_row:
        try:
            wti_w = dict(_cached("wti", PRICE_ROWS["wti"][1]))
            go_cutoff = _month_end(go_row["points"][-1][0])
            new = [(f, gold_weekly[f] / wti_w[f]) for f in sorted(set(gold_weekly) & set(wti_w))
                   if f > go_cutoff]
            if new:
                go_row["points"] += [[f, round(v, 4)] for f, v in new]
                go_row.update(asof=new[-1][0], usd=round(new[-1][1], 4),
                              freq="monthly avg; weekly since " + new[0][0])
                applied.append("goldoil")
        except Exception as e:
            log(f"::warning::goldoil weekly skipped: {e}")

    if "debt" in applied:
        log("note: weekly debt points went to overrides_v3['debt'] (the displayed row); items debt keeps its original quarterly shape")
    doc["weekly_notes"] = {
        "basis": "Points after each row's monthly/quarterly history are genuine completed-week observations (Friday-labeled; at least 3 business days for averages). Priced in gold using the same week's World Gold Council weekly average. Stocks (debt, Fed balance sheet) are end-of-week or source-published weekly observations, not averages. Nothing is forward-filled from monthly data; rows without a weekly source keep their existing cadence.",
        "silver": "No free weekly silver source exists, so weekly points carry no oz Ag value: silver denomination of weekly points ends at the last monthly point, and row-level oz Ag keeps the last monthly conversion. Gold and USD denominations are genuine weekly.",
        "sources": {k: v[0] for k, v in list(PRICE_ROWS.items()) + list(RATE_ROWS.items())},
    }
    log("weekly overlay applied: " + ", ".join(applied))
    return applied


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    doc = json.load(open(path))
    apply(doc)
    json.dump(doc, open(path, "w"), separators=(",", ":"))
    print("written", path)
