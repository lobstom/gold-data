# Prices in Gold Ounces - model summary

No Time For Bull prices commodities, energy, housing, markets, money and debt in troy ounces of gold.
This file is a compact, dated summary of that model. It is generated from the frozen dataset; it is not real-time data.

- Interactive model: https://www.notimeforbull.com/prices/
- Full dataset (JSON): https://lobstom.github.io/gold-data/data.json
- Machine-readable version of this summary: https://lobstom.github.io/gold-data/summary.json
- Frozen Monday snapshot manifest: https://lobstom.github.io/gold-data/snapshots/latest.json
- Dataset last built: 2026-11-12. Summary generated: 2026-11-12.

## Money

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Gold | $4,018 per oz | 1.000 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| Silver | $57.00 per oz | 0.01389 oz | 2026-10 | monthly avg |
| US dollar | $1.00 | 0.0002489 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| US Dollar Index | 102.1 pts | not priced in gold | 2026-10 | monthly avg |

US dollar priced in gold: 1 USD = 1 / gold price in USD. Derived from this page's gold row (same sources and dates: World Bank monthly averages, MeasuringWorth annual history before 1960); not a separate data series.

US Dollar Index (DXY) is rebuilt from FRED exchange rates with the ICE DXY formula (from 1980) and spliced to the Fed major currencies index before 1980. It is shown in index points in every unit mode and is not the ICE-published series.

## Commodities and energy

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Copper (LME grade A) | $14,508 per tonne | 3.534 oz | 2026-10 | monthly avg |
| Uranium U3O8 (spot) | $91.55 per lb | 0.0223 oz | 2026-10-30 | month-end spot average (UxC/TradeTech via Cameco) |
| Crude oil (WTI) | $97.70 per bbl | 0.0238 oz | 2026-10 | monthly avg |
| Crude oil (Brent) | $125.00 per bbl | 0.03045 oz | 2026-10 | monthly avg |
| Natural gas (US) | $2.96 per MMBtu | 0.0007211 oz | 2026-10 | monthly avg |
| Natural gas (Europe, TTF) | $28.50 per MMBtu | 0.006943 oz | 2026-10 | monthly avg |
| Coal (Australian, Newcastle) | $152.30 per tonne | 0.0371 oz | 2026-10 | monthly avg |
| Lumber (LBR rolling futures; since Sep 2022) | $525.05 per 1,000 board ft | 0.1279 oz | 2026-10 | monthly avg |
| US electricity (all sectors) | $148.70 per MWh | 0.03371 oz | 2026-08 | monthly avg |

## Housing

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| US median new-home price | $393,300 per home | 92.2 oz | 2026-07 | quarterly |
| US home price index vs gold, Jan 2000 = 100 | 21.7 pts | not priced in gold | 2026-08 | monthly (3-month average, published about two months late) |

US median new-home price: Census median sales price of new houses sold (FRED MSPUS, nominal dollars, quarterly) from 1963. Before 1963 the row is a Shiller-based nominal US home price index (1890-1962, closely tracking but not an exact copy of the Robert Shiller series) rescaled to the 1963 Census level, so those values are approximate and are not observed median prices. From 1963 the series covers new homes only; the earlier part is a rescaled all-home index. For existing-home price changes see the US home price index vs gold row.

US home price index vs gold: the S&P CoreLogic Case-Shiller US National Home Price Index (repeat sales of single-family homes, FRED CSUSHPINSA, from 1987) divided by the monthly average gold price, with both set to 100 in January 2000. It is an index, not ounces per home, and it is shown in index points in every unit mode. Case-Shiller is a three-month average and is revised.

## Markets

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| S&P 500 (price index) | 7,505.9 pts | 1.868 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| Dow Jones Industrial Average | 51,987.0 pts | 12.9 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| Avg hourly earnings (production workers) | $32.75 per hour | 0.007978 oz | 2026-10 | monthly |
| US M2 money supply | $23.41 trillion | 5.42 billion oz | 2026-09 | monthly, seasonally adjusted |

## Debt and the Fed's balance sheet

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Who owns the federal debt (and the Fed's balance sheet) | $40.55 trillion | 10.09 billion oz | 2026-11-06 | quarter-end stock (annual before 1966); weekly since 2026-09-25 |
| Federal debt held by the public | $31.71 trillion | 7.50 billion oz | 2026-06-30 | quarter-end stock |
| Federal debt held by government accounts | $7.76 trillion | 1.83 billion oz | 2026-06-30 | quarter-end stock |
| Fed total assets | $6.75 trillion | 1.68 billion oz | 2026-11-04 | month-end: last weekly stock; weekly since 2026-11-04 |
| Treasuries held by the Fed | $4.58 trillion | 1.14 billion oz | 2026-11-04 | month-end: last weekly stock; weekly since 2026-11-04 |
| US total credit market debt / GDP | 365% | not priced in gold | 2026-04 | quarterly |

Who owns the federal debt (and the Fed's balance sheet): Ownership split: approximate quarter end. Fed stocks use the last Wednesday in the quarter-end month. Foreign holders are US Treasury TIC estimates of foreign holdings of Treasury securities at quarter-end months (official vs private/other). Other domestic holders are a residual: total debt minus government accounts minus Fed Treasuries minus TIC foreign holdings. TIC and Treasury/Fed debt definitions differ, so the residual is approximate. Non-Treasury Fed assets are NOT federal debt. Dollar-equivalent gold, not gold owned.

Federal debt held by the public: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

Federal debt held by government accounts: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

Fed total assets: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

Treasuries held by the Fed: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

## Interest rates (percent, not priced in gold)

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| 30Y mortgage (PMMS); all-term MIRS proxy before 1971 | 7.18% | not priced in gold | 2026-11-05 | weekly PMMS; annual all-term proxy 1963-1970 |
| Fed funds (effective); discount rate before 1954 | 3.88% | not priced in gold | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| US 10Y Treasury yield | 4.892% | not priced in gold | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| US 10Y real yield (TIPS) | 2.628% | not priced in gold | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| Yield curve: 10Y minus 2Y Treasury (pp) | 0.34 pp | not priced in gold | 2026-11-06 | monthly avg; weekly since 2026-11-06 |

## Ratios and price indexes

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Gold / silver ratio (oz Ag per oz Au) | 72.0 | not priced in gold | 2026-10 | monthly avg |
| Gold / oil ratio (WTI bbl per oz Au) | 42.0 | not priced in gold | 2026-10 | monthly avg |
| US CPI (all items, 1982-84=100) | 337.5 | not priced in gold | 2026-10 | monthly |

## Sources and conventions

- Weekly gold: World Gold Council gold price feed, completed-week averages. Monthly gold history before that: World Bank monthly averages.
- Oil, gas, coal, uranium history: World Bank monthly commodities; EIA weekly WTI/Brent; UxC weekly uranium; Cameco month-end uranium history.
- Housing: Census median new-home price (quarterly, FRED MSPUS) from 1963; rescaled Shiller-based index before that. Case-Shiller national index relative to gold, both rebased to 100 in January 2000.
- Rates: Freddie Mac 30Y mortgage (weekly); Fed funds effective rate (discount rate before 1954); Treasury 10Y nominal and 10Y TIPS real yields.
- Markets: S&P 500 and Dow monthly averages plus weekly closes; average hourly earnings; M2 (monthly, seasonally adjusted).
- Debt: federal debt and ownership split from Treasury/Fed sources; Fed balance sheet from H.4.1.
- US Dollar Index rebuilt from Fed G.5 exchange rates with ICE weights, spliced with the Fed major-currencies index before 1980; levels before 1998 are approximate.
- Fed Treasuries are part of Fed assets and public debt; public debt includes Fed and foreign holders. Government-account debt plus public debt equals total debt at matching dates. Do not add overlapping rows.
- Latest uranium may use an earlier month's average metal price. This is not a same-day spot ratio.
- Points after each row's monthly/quarterly history are genuine completed-week observations (Friday-labeled; at least 3 business days for averages). Priced in gold using the same week's World Gold Council weekly average. Stocks (debt, Fed balance sheet) are end-of-week or source-published weekly observations, not averages. Nothing is forward-filled from monthly data; rows without a weekly source keep their existing cadence.
- No free weekly silver source exists, so weekly points carry no oz Ag value: silver denomination of weekly points ends at the last monthly point, and row-level oz Ag keeps the last monthly conversion. Gold and USD denominations are genuine weekly.
- Weekly row sources: EIA Europe Brent spot weekly average; 10Y minus 2Y Treasury (Treasury daily par yield curve), completed-week average; US Treasury Debt to the Penny, end-of-week total public debt outstanding; Dow Jones daily closes (CNBC), completed-week average; Fed total assets (H.4.1 Table 5, Wednesday level), source weekly stock; Fed funds effective rate (NY Fed EFFR), completed-week average; Treasuries held outright by the Fed (H.4.1 Table 1, Wednesday level), source weekly stock; EIA Henry Hub natural gas spot weekly average; Freddie Mac PMMS 30Y fixed, source-published weekly average; US 10Y TIPS real yield (Treasury daily real par yield curve), completed-week average; S&P 500 daily closes (CNBC), completed-week average; US 10Y Treasury yield (Treasury daily par yield curve), completed-week average; EIA WTI Cushing spot weekly average

Values priced in gold use the gold price of the same period as each row (weekly rows use weekly averages; monthly rows use monthly averages). Rows carry their own as-of dates and update at their native frequency. Republication rights for underlying sources remain with those sources.
