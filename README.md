# Prices data: weekly capture, native-frequency series

## Timing and safe operation
- Scheduled Monday 04:17 America/Los_Angeles, before the Monday 06:30 brief.
- Existing monthly/quarterly chart definitions and data.json schema stay unchanged.
- A manual run defaults to an isolated test snapshot. It does not replace data.json or the production manifest.
- Manual `publish=true` is allowed only on Mondays. A published dated snapshot is never overwritten, even on rerun. Corrections need a separately reviewed version and note.
- Build/validation failure leaves the last committed live data and snapshots untouched. GitHub run status is the failure signal. A newsletter reader must check the expected Monday date and must not assume an old manifest means a successful new pull.
- Authenticated UxC retrieval is a separate Monday task before the build. This repo contains no account credentials. The builder checks the dated input, not the UxC website. Input older than 14 days is explicitly overdue.

## Published contract
`snapshots/latest.json` points to `snapshots/YYYY-MM-DD.json` after the first successful scheduled Monday. It contains `path`, `previous_snapshot`, `snapshot_date`, `captured_at`, `kind`, `complete`, `data_sha256` and `snapshot_sha256`.

The immutable snapshot contains:
- `data`: full legacy payload, without changing field meanings, IDs or point tuples.
- `series`: native frequency, observation period, source, checked time, source status, change status and row digest. Quarterly quarter-start labels are rendered as Q1/Q2/Q3/Q4, not single-month values.
- `weekly_prices`: separate weekly EIA WTI/Brent averages and dated UxC input. Each has actual observation date, previous date, days between observations and percentage change. Only 7-day gaps are labeled week-over-week. Gold uses the World Gold Council gold price feed, labeled exactly that way, not LBMA. Gold is a completed-week average of at least three actual business-day observations, with each date retained. Oil-in-gold is calculated only when current and previous oil/gold week-end dates match, and explicitly labeled a ratio of weekly averages. No monthly gold denominator or mismatched uranium/gold ratio is used.

`series.change_status` is baseline, new_observation, revised or unchanged. New monthly/quarterly releases are not weekly market moves. Baseline means no prior frozen snapshot, not zero change. `source_status` distinguishes retrieved data, manual input and overdue input. Per-source weekly fetch failures are unavailable, not carried forward as fresh data.

Tests use `snapshots/test-latest.json` and `snapshots/tests/<timestamp>.json`, with `kind=test`. Never use those as a Monday issue cut.

## Newsletter reader
1. Read latest.json and require `complete=true`, `kind=monday` and this Monday's date. If missing/old, flag it and explicitly label any prior successful cut.
2. Read the exact `path` and `previous_snapshot`. Verify digests using Python `json.dumps(value, separators=(',', ':'), sort_keys=True, allow_nan=False)` encoded as UTF-8, then SHA256. `data_sha256` covers `data`; `snapshot_sha256` covers the whole snapshot. Retain the manifest and selected paths/checksums in the Monday draft.
3. Head the section `Data checked Monday [date]`. Include actual source periods. Wednesday text and chart must use the same frozen Monday data, not floating data.json.
4. Separate new releases, revisions and actual weekly observations. If nothing new arrived, say so. Failed/overdue/pending sources stay visibly excluded from claims.
5. Rate deltas use percentage points/basis points, price deltas use percent. Percentiles need mode/history window and original proxy-history caveats. The long source/history and rights notes stay with any chart.

## Sources and conventions
- Legacy prices retain World Bank monthly averages, EIA monthly electricity, FRED native/monthly aggregates, quarterly housing/debt/credit and existing historical proxies.
- Oil: EIA published weekly WTI Cushing and Europe Brent spot averages. Date is the source's week-ending Friday, not necessarily the latest calendar Friday.
- Weekly overlay rows use direct sources because FRED blocks this pipeline's automated fredgraph.csv requests: S&P 500 and Dow daily closes from CNBC (completed-week averages; Yahoo Finance fallback), Treasury daily par yield curve CSVs (10Y nominal, 10Y real TIPS, 10Y-2Y spread), NY Fed EFFR API (fed funds), Fed H.4.1 data download (total assets Table 5; Treasuries held outright Table 1, Wednesday levels) and Freddie Mac PMMS xlsx (30Y mortgage). FRED remains the monthly-build source; its block does not hold up these weekly rows.
- Uranium: UxC latest available weekly quote. Monday-evening publication and free-site delay up to 72h mean the Monday-morning cut uses the last available quote. Cameco remains month-end history. Original uranium gold conversions can use the last available monthly gold average, not same-week gold.
- Gold: World Gold Council chart daily data, short window, aggregated to completed Monday-Friday weeks. Feed access uses curl headers. This is not labeled an LBMA fixing; an undocumented site API may change and fail explicitly.

Run local checks with `python scripts/weekly_snapshot.py --self-test`. A normal invocation fetches/validates all legacy data, captures weekly sources and saves an isolated test. Only `--publish` writes the production Monday cut.

## Lumber addition (29 October 2026)
- Lumber is CME LBR rolling-nearby futures via Yahoo Finance LBR=F, quoted in USD per 1,000 board feet. The 27,500-board-foot contract size is not the row unit.
- Daily closes are averaged by completed calendar month, then divided by the same month’s model gold/silver averages. First full month is September 2022; launch-partial August and unfinished current months are excluded.
- Legacy LBS was delisted May 2023. It is not spliced into this row. Different contract/delivery terms and futures rolling can affect comparisons. This is not a spot or retail lumber price or an investable total-return series.
- The existing Monday refresh fetches lumber; failure leaves the validated live cut unchanged. A manual lumber-only workflow can update just this row without refreshing other observations or altering immutable Monday snapshots. The model-wide updated date is not advanced by the isolated addition; row source_checked_at records its own retrieval.
- Source history https://finance.yahoo.com/quote/LBR%3DF/history/ ; contract https://www.cmegroup.com/articles/faqs/lumber-futures-faq.html ; transition https://www.cmegroup.com/notices/ser/2023/04/SER-9183.html .
