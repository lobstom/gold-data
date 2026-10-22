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
import csv, datetime as dt, io, json, math, os, re, subprocess, sys, urllib.request

MIN_OBS = 3  # business days required for a completed week


def _get(url, timeout=45, binary=False):  # 45s: FRED tarpits blocked IPs; normal responses are ~1s
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



def _yahoo_daily(symbol):
    """Yahoo Finance daily closes -> [(date, close)]. Recent ~6 months only.
    Retries across the two public query hosts: Yahoo rate-limits (429) often."""
    import time
    raw = None
    last_err = None
    for attempt, host in enumerate(("query1.finance.yahoo.com", "query2.finance.yahoo.com",
                                    "query1.finance.yahoo.com", "query2.finance.yahoo.com")):
        url = (f"https://{host}/v8/finance/chart/{symbol}"
               "?range=6mo&interval=1d&includePrePost=false")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"})
            raw = json.loads(urllib.request.urlopen(req, timeout=45).read().decode("utf8", "ignore"))
            break
        except Exception as e:
            last_err = e
            time.sleep(3 * (attempt + 1))
    if raw is None:
        raise ValueError(f"Yahoo {symbol}: fetch failed after retries: {last_err}")
    result = raw.get("chart", {}).get("result")
    if not result:
        raise ValueError(f"Yahoo {symbol}: no chart result (possible block): {str(raw)[:120]!r}")
    r0 = result[0]
    ts = r0.get("timestamp") or []
    closes = (r0.get("indicators", {}).get("quote", [{}])[0]).get("close") or []
    out = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).date(), float(c)))
    if len(out) < 30:
        raise ValueError(f"Yahoo {symbol}: only {len(out)} usable closes (possible block page)")
    return out


def _treasury_csv(kind, years):
    """Treasury daily par yield curve CSV -> list of rows (header, data rows)."""
    import csv as _csv
    rows = []
    for y in years:
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
               f"daily-treasury-rates.csv/{y}/all?type={kind}&field_tdr_date_value={y}&page&_format=csv")
        text = _get(url)
        rdr = list(_csv.reader(io.StringIO(text)))
        if len(rdr) < 10:
            raise ValueError(f"Treasury {kind} {y}: only {len(rdr)} rows (possible block page)")
        rows.append((rdr[0], rdr[1:]))
    return rows


def _treasury_daily(kind, column):
    """Treasury daily par yield curve -> [(date, value)] for a column like '10 Yr'."""
    today = dt.date.today()
    years = [today.year] if today.month > 3 else [today.year, today.year - 1]
    out = []
    for hdr, data in _treasury_csv(kind, years):
        try:
            j = hdr.index(column)
        except ValueError:
            raise ValueError(f"Treasury {kind}: column {column!r} missing from header {hdr[:8]!r}")
        for r in data:
            if len(r) <= j or not r[j].strip():
                continue
            try:
                out.append((dt.datetime.strptime(r[0].strip(), "%m/%d/%Y").date(), float(r[j])))
            except ValueError:
                raise ValueError(f"Treasury {kind}: malformed row {r[:2]!r} (possible block page)")
    cutoff = today - dt.timedelta(days=75)
    out = [(d, v) for d, v in out if d >= cutoff]
    if len(out) < 40:
        raise ValueError(f"Treasury {kind} {column}: only {len(out)} usable rows (possible block page)")
    return sorted(out)


def treasury_daily_weekly(column, kind="daily_treasury_yield_curve"):
    """Treasury daily yield column -> completed-week averages [(friday_iso, avg)]."""
    return [(f, a) for f, a, _ in _weeks(_treasury_daily(kind, column))]


def curve_daily_weekly():
    """10Y minus 2Y from Treasury daily par yield curve -> completed-week average spread."""
    today = dt.date.today()
    years = [today.year] if today.month > 3 else [today.year, today.year - 1]
    out = []
    for hdr, data in _treasury_csv("daily_treasury_yield_curve", years):
        try:
            j10, j2 = hdr.index("10 Yr"), hdr.index("2 Yr")
        except ValueError:
            raise ValueError(f"Treasury curve: 10 Yr/2 Yr missing from header {hdr[:8]!r}")
        for r in data:
            if len(r) <= j10 or not r[j10].strip() or not r[j2].strip():
                continue
            try:
                out.append((dt.datetime.strptime(r[0].strip(), "%m/%d/%Y").date(),
                            float(r[j10]) - float(r[j2])))
            except ValueError:
                raise ValueError(f"Treasury curve: malformed row {r[:2]!r} (possible block page)")
    cutoff = today - dt.timedelta(days=75)
    out = [(d, v) for d, v in out if d >= cutoff]
    if len(out) < 40:
        raise ValueError(f"Treasury curve: only {len(out)} usable rows (possible block page)")
    return [(f, a) for f, a, _ in _weeks(sorted(out))]


def effr_daily_weekly():
    """NY Fed EFFR daily -> completed-week averages [(friday_iso, avg)]."""
    start = (dt.date.today() - dt.timedelta(days=75)).isoformat()
    end = dt.date.today().isoformat()
    url = f"https://markets.newyorkfed.org/api/rates/all/search.json?startDate={start}&endDate={end}"
    raw = json.loads(_get(url))
    out = []
    for r in raw.get("refRates", []):
        if r.get("type") == "EFFR" and r.get("percentRate") is not None:
            try:
                out.append((dt.date.fromisoformat(r["effectiveDate"]), float(r["percentRate"])))
            except (KeyError, ValueError):
                raise ValueError(f"NY Fed EFFR: malformed row {str(r)[:80]!r} (possible block page)")
    if len(out) < 30:
        raise ValueError(f"NY Fed EFFR: only {len(out)} usable rows (possible block page)")
    return [(f, a) for f, a, _ in _weeks(sorted(out))]


H41_T1 = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H41&series=f52e72511be65e16f71d4f5858951312&lastobs=60&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
H41_T5 = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H41&series=95f48646a08920cfaebeeb8eae925dea&lastobs=60&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"


def _h41_weekly(url, exact_desc):
    """Fed H.4.1 data download -> [(date_iso, $millions)] for one exact series description."""
    import csv as _csv
    rdr = list(_csv.reader(io.StringIO(_get(url))))
    if len(rdr) < 14:
        raise ValueError(f"H41: only {len(rdr)} rows (possible block page)")
    desc, dates = rdr[0], rdr[6:]
    try:
        j = next(i for i, d in enumerate(desc) if d.strip() == exact_desc)
    except StopIteration:
        raise ValueError(f"H41: series {exact_desc!r} not found (release layout changed?)")
    out = []
    for r in dates:
        if len(r) <= j or not re.match(r"^\d{4}-\d{2}-\d{2}$", r[0].strip()):
            continue
        try:
            out.append((r[0].strip(), float(r[j])))
        except ValueError:
            raise ValueError(f"H41: malformed row {r[:2]!r} (possible block page)")
    if len(out) < 8:
        raise ValueError(f"H41 {exact_desc[:40]}: only {len(out)} usable rows (possible block page)")
    return out


def fedassets_weekly():
    """Fed total assets, H.4.1 Table 5 Wednesday level -> [(date, $trillion)]."""
    return [(d, v / 1e6) for d, v in _h41_weekly(
        H41_T5, "Assets: Total Assets: Total assets: Wednesday level")]


def fedtreas_weekly():
    """Treasuries held outright by the Fed, H.4.1 Table 1 Wednesday level -> [(date, $trillion)]."""
    return [(d, v / 1e6) for d, v in _h41_weekly(
        H41_T1, "Assets: Securities Held Outright: U.S. Treasury securities: Wednesday level")]


def pmms_weekly():
    """Freddie Mac PMMS 30Y fixed xlsx -> [(date_iso, rate)]. Source-published weekly."""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(_get(
        "https://www.freddiemac.com/pmms/docs/historicalweeklydata.xlsx", binary=True)), read_only=True)
    ws = wb["Full History"]
    out = []
    for r in ws.iter_rows(min_row=7, values_only=True):
        if isinstance(r[0], dt.datetime) and isinstance(r[1], (int, float)):
            out.append((r[0].date().isoformat(), float(r[1])))
    if len(out) < 8:
        raise ValueError(f"PMMS: only {len(out)} usable rows (possible block page)")
    return out



def _cnbc_daily(symbol):
    """CNBC daily bars -> [(date, close)]. Server-friendly, no account.
    Undocumented endpoint (same caveat class as the WGC feed)."""
    url = f"https://ts-api.cnbc.com/harmony/app/charts/3M.json?symbol={symbol}"
    raw = json.loads(_get(url))
    bars = raw.get("barData", {}).get("priceBars")
    if not bars:
        raise ValueError(f"CNBC {symbol}: no priceBars (possible block/change): {str(raw)[:120]!r}")
    out = []
    for b in bars:
        try:
            out.append((dt.datetime.strptime(b["tradeTime"], "%Y%m%d%H%M%S").date(), float(b["close"])))
        except (KeyError, ValueError):
            raise ValueError(f"CNBC {symbol}: malformed bar {str(b)[:80]!r} (possible block page)")
    if len(out) < 30:
        raise ValueError(f"CNBC {symbol}: only {len(out)} usable bars (possible block page)")
    return out


def index_daily(symbol_cnbc, symbol_yahoo):
    """Index daily closes: CNBC primary (verified server-friendly), Yahoo fallback."""
    try:
        return _cnbc_daily(symbol_cnbc)
    except Exception as e:
        print(f"::warning::CNBC {symbol_cnbc} failed ({e}); trying Yahoo fallback", flush=True)
        return _yahoo_daily(symbol_yahoo)


def _r5(x):
    return float(f"{x:.5g}")


# price rows: weekly points [date, ozAu, USD, null]. big rows price in billion oz (USD in $T).
# each: (source description, fetcher -> [(friday_iso, usd_value)])
PRICE_ROWS = {
    "wti": ("EIA WTI Cushing spot weekly average", lambda: eia_weekly("RWTC")),
    "brent": ("EIA Europe Brent spot weekly average", lambda: eia_weekly("RBRTE")),
    "gas": ("EIA Henry Hub natural gas spot weekly average", lambda: eia_weekly("RNGWHHD")),
    "sp500": ("S&P 500 daily closes (CNBC), completed-week average", lambda: [(f, a) for f, a, _ in _weeks(index_daily(".SPX", "%5EGSPC"))]),
    "dow": ("Dow Jones daily closes (CNBC), completed-week average", lambda: [(f, a) for f, a, _ in _weeks(index_daily(".DJI", "%5EDJI"))]),
    "debt": ("US Treasury Debt to the Penny, end-of-week total public debt outstanding", debt_weekly),
    "fedassets": ("Fed total assets (H.4.1 Table 5, Wednesday level), source weekly stock", fedassets_weekly),
    "fedtreas": ("Treasuries held outright by the Fed (H.4.1 Table 1, Wednesday level), source weekly stock", fedtreas_weekly),
}
# rate rows (kind=rate, 2-tuples): no gold conversion
RATE_ROWS = {
    "fedfunds": ("Fed funds effective rate (NY Fed EFFR), completed-week average", effr_daily_weekly),
    "ust10": ("US 10Y Treasury yield (Treasury daily par yield curve), completed-week average", lambda: treasury_daily_weekly("10 Yr")),
    "real10": ("US 10Y TIPS real yield (Treasury daily real par yield curve), completed-week average", lambda: treasury_daily_weekly("10 YR", "daily_treasury_real_yield_curve")),
    "curve": ("10Y minus 2Y Treasury (Treasury daily par yield curve), completed-week average", curve_daily_weekly),
    "mortgage": ("Freddie Mac PMMS 30Y fixed, source-published weekly average", pmms_weekly),
}


CACHE = {}

def _cached(key, fetch):
    if key not in CACHE:
        t0 = dt.datetime.now()
        CACHE[key] = fetch()
        print(f"fetch {key}: {len(CACHE[key])} points in {(dt.datetime.now()-t0).total_seconds():.1f}s", flush=True)
    return CACHE[key]


def _weekly_cutoff(points):
    """Re-runnable append boundary: max(month end of the last first-of-month
    (monthly-cadence) point, date of the most recent point). Monthly points are
    never duplicated; already-appended weekly points continue from their last
    Friday instead of stalling until the next month."""
    last = points[-1][0]
    monthly = [p[0] for p in points if p[0].endswith("-01")]
    base = _month_end(monthly[-1]) if monthly else "0000-00-00"
    return max(base, last)


def _freq_weekly(freq, new_first):
    """Keep the original 'weekly since' start date across re-runs.
    Rows already natively weekly (PMMS) keep their frequency text unchanged."""
    if freq.strip().lower().startswith("weekly"):
        return freq
    base, _, since = freq.partition("; weekly since ")
    return base + "; weekly since " + (since or new_first)


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
    gold_cutoff = _weekly_cutoff(gold_row["points"])
    new = [(f, a) for f, a in gw if f > gold_cutoff]
    if new:
        gold_row["points"] += [[f, 1.0, _r5(a), None] for f, a in new]
        gold_row.update(asof=new[-1][0], usd=_r5(new[-1][1]), goldusd=_r5(new[-1][1]),
                        freq=_freq_weekly(gold_row["freq"], new[0][0]))
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
        cutoff = _weekly_cutoff(row["points"])
        # Gold conversion uses the source week's completed Friday average, whatever
        # weekday the source publishes on (EIA Friday, H.4.1 Wednesday level).
        new = []
        for d, v in pts:
            dd = dt.date.fromisoformat(d)
            if dd.weekday() > 4:
                continue
            wf = (dd + dt.timedelta(days=4 - dd.weekday())).isoformat()
            if wf in gold_weekly and d > cutoff:
                new.append((d, v * big / gold_weekly[wf], v))
        if not new:
            log(f"{rid}: no new completed weeks")
            continue
        row["points"] += [[d, _r5(o), _r5(u), None] for d, o, u in new]
        row.update(asof=new[-1][0], usd=_r5(new[-1][2]),
                   goldusd=_r5(gold_weekly[(dt.date.fromisoformat(new[-1][0]) + dt.timedelta(days=4 - dt.date.fromisoformat(new[-1][0]).weekday())).isoformat()]),
                   ozau=_r5(new[-1][1]),
                   freq=_freq_weekly(row["freq"], new[0][0]))
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
        cutoff = _weekly_cutoff(row["points"])
        new = [(f, v) for f, v in pts if f > cutoff]
        if not new:
            log(f"{rid}: no new completed weeks")
            continue
        row["points"] += [[f, round(v, 4)] for f, v in new]
        row.update(asof=new[-1][0], usd=round(new[-1][1], 4),
                   freq=_freq_weekly(row["freq"], new[0][0]))
        applied.append(rid)

    # derived weekly: US dollar row (inverse of weekly gold); oz Ag leg stays null
    usd_row = byid.get("usd")
    if usd_row and "gold" in applied:
        usd_cutoff = _weekly_cutoff(usd_row["points"])
        new = [(f, 1.0 / a) for f, a in gw if f > usd_cutoff]
        if new:
            usd_row["points"] += [[f, _r5(o), 1.0, None] for f, o in new]
            usd_row.update(asof=new[-1][0], ozau=_r5(new[-1][1]),
                           freq=_freq_weekly(usd_row["freq"], new[0][0]))
            applied.append("usd")
    # gold/oil ratio from two genuine weekly series
    go_row = byid.get("goldoil")
    if go_row:
        try:
            wti_w = dict(_cached("wti", PRICE_ROWS["wti"][1]))
            go_cutoff = _weekly_cutoff(go_row["points"])
            new = [(f, gold_weekly[f] / wti_w[f]) for f in sorted(set(gold_weekly) & set(wti_w))
                   if f > go_cutoff]
            if new:
                go_row["points"] += [[f, round(v, 4)] for f, v in new]
                go_row.update(asof=new[-1][0], usd=round(new[-1][1], 4),
                              freq=_freq_weekly(go_row["freq"], new[0][0]))
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
