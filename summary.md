# Prices in Gold Ounces - model summary

No Time For Bull prices commodities, energy, housing, markets, money and debt in troy ounces of gold.
This file is a compact, dated summary of that model. It is generated from the frozen dataset; it is not real-time data.

- Interactive model: https://www.notimeforbull.com/prices/
- Full dataset (JSON): https://data.notimeforbull.com/data.json
- Machine-readable version of this summary: https://data.notimeforbull.com/summary.json
- Frozen Monday snapshot manifest: https://data.notimeforbull.com/snapshots/latest.json
- Dataset last built: 2026-11-16. Summary generated: 2026-11-23.

## Money

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Gold | $3,989 per oz | 1.000 oz | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| Silver | $57.00 per oz | 0.01389 oz | 2026-10 | monthly avg |
| US dollar | $1.00 | 0.0002507 oz | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| US Dollar Index | 102.1 pts | not priced in gold | 2026-10 | monthly avg |

US dollar priced in gold: 1 USD = 1 / gold price in USD. Derived from this page's gold row (same sources and dates: World Bank monthly averages, MeasuringWorth annual history before 1960); not a separate data series.

US Dollar Index (DXY) is rebuilt from FRED exchange rates with the ICE DXY formula (from 1980) and spliced to the Fed major currencies index before 1980. It is shown in index points in every unit mode and is not the ICE-published series.

## Commodities and energy

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Copper (LME grade A) | $14,508 per tonne | 3.534 oz | 2026-10 | monthly avg |
| Uranium U3O8 (spot) | $91.55 per lb | 0.0223 oz | 2026-10-30 | month-end spot average (UxC/TradeTech via Cameco) |
| Crude oil (WTI) | $95.97 per bbl | 0.02388 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| Crude oil (Brent) | $100.41 per bbl | 0.02499 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
| Natural gas (US) | $2.61 per MMBtu | 0.0006495 oz | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
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
| S&P 500 (price index) | 7,568.9 pts | 1.898 oz | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| Dow Jones Industrial Average | 52,351.0 pts | 13.1 oz | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| 10Y Treasury futures (ZN reference quote) | 105.996875 per $100 face; $105,996.88 reference per $100k face | 26.6 oz | 2026-11-13 | completed-week average of final settlements; history from 2026-11-13 |
| Treasury bond futures (ZB reference quote) | 106.806250 per $100 face; $106,806.25 reference per $100k face | 26.8 oz | 2026-11-13 | completed-week average of final settlements; history from 2026-11-13 |
| Avg hourly earnings (production workers) | $32.75 per hour | 0.007978 oz | 2026-10 | monthly |
| US M2 money supply | $23.41 trillion | 5.42 billion oz | 2026-09 | monthly, seasonally adjusted |

10Y Treasury futures (ZN reference quote): CME final daily settlements, decimal quote per $100 face. Gold equivalent per $100,000 face = 1,000 x weekly mean decimal quote / same-week World Gold Council gold USD/oz. Futures reference quote only: not margin, invested capital, delivery invoice price, cash bond value or total return. Invoice pricing also uses a conversion factor and accrued interest. At least three dated final daily settlements per completed week. No silver or real-dollar conversion. Free browser history currently starts November 9, 2026; earlier requests were empty. The first weekly point is November 13, 2026. Switch to the next quarterly delivery contract on the first Monday on or after the 20th of the month before delivery; one contract for the full week. No back-adjustment. Roll weeks are marked; a level change at a roll is not an investment return.

Treasury bond futures (ZB reference quote): CME final daily settlements, decimal quote per $100 face. Gold equivalent per $100,000 face = 1,000 x weekly mean decimal quote / same-week World Gold Council gold USD/oz. Futures reference quote only: not margin, invested capital, delivery invoice price, cash bond value or total return. Invoice pricing also uses a conversion factor and accrued interest. At least three dated final daily settlements per completed week. No silver or real-dollar conversion. Free browser history currently starts November 9, 2026; earlier requests were empty. The first weekly point is November 13, 2026. Switch to the next quarterly delivery contract on the first Monday on or after the 20th of the month before delivery; one contract for the full week. No back-adjustment. Roll weeks are marked; a level change at a roll is not an investment return.

## Debt and the Fed's balance sheet

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Who owns the federal debt (and the Fed's balance sheet) | $40.61 trillion | 10.18 billion oz | 2026-11-13 | quarter-end stock (annual before 1966); weekly since 2026-09-25 |
| Federal debt held by the public | $31.71 trillion | 7.50 billion oz | 2026-06-30 | quarter-end stock |
| Federal debt held by government accounts | $7.76 trillion | 1.83 billion oz | 2026-06-30 | quarter-end stock |
| Fed total assets | $6.76 trillion | 1.69 billion oz | 2026-11-11 | month-end: last weekly stock; weekly since 2026-11-04 |
| Treasuries held by the Fed | $4.59 trillion | 1.15 billion oz | 2026-11-11 | month-end: last weekly stock; weekly since 2026-11-04 |
| US total credit market debt / GDP | 365% | not priced in gold | 2026-04 | quarterly |

Who owns the federal debt (and the Fed's balance sheet): Ownership split: approximate quarter end. Fed stocks use the last Wednesday in the quarter-end month. Foreign holders are US Treasury TIC estimates of foreign holdings of Treasury securities at quarter-end months (official vs private/other). Other domestic holders are a residual: total debt minus government accounts minus Fed Treasuries minus TIC foreign holdings. TIC and Treasury/Fed debt definitions differ, so the residual is approximate. Non-Treasury Fed assets are NOT federal debt. Dollar-equivalent gold, not gold owned.

Federal debt held by the public: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

Federal debt held by government accounts: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

Fed total assets: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

Treasuries held by the Fed: Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

## Interest rates (percent, not priced in gold)

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| 30Y mortgage (PMMS); all-term MIRS proxy before 1971 | 7.11% | not priced in gold | 2026-11-12 | weekly PMMS; annual all-term proxy 1963-1970 |
| Fed funds (effective); discount rate before 1954 | 3.88% | not priced in gold | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| US 10Y Treasury yield | 5.0275% | not priced in gold | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| US 10Y real yield (TIPS) | 2.8025% | not priced in gold | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |
| Yield curve: 10Y minus 2Y Treasury (pp) | 0.27 pp | not priced in gold | 2026-11-13 | completed-week average (2026-11-09 to 2026-11-13); not Friday close |

## Ratios and price indexes

| Series | Latest | In gold | As of | Frequency |
| --- | --- | --- | --- | --- |
| Gold / silver ratio (oz Ag per oz Au) | 72.0 | not priced in gold | 2026-10 | monthly avg |
| Gold / oil ratio (WTI bbl per oz Au) | 41.9 | not priced in gold | 2026-11-06 | monthly avg; weekly since 2026-11-06 |
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
- CME final daily settlements, decimal quote per $100 face. Gold equivalent per $100,000 face = 1,000 x weekly mean decimal quote / same-week World Gold Council gold USD/oz. Futures reference quote only: not margin, invested capital, delivery invoice price, cash bond value or total return. Invoice pricing also uses a conversion factor and accrued interest. At least three dated final daily settlements per completed week. No silver or real-dollar conversion. Free browser history currently starts November 9, 2026; earlier requests were empty. The first weekly point is November 13, 2026. Switch to the next quarterly delivery contract on the first Monday on or after the 20th of the month before delivery; one contract for the full week. No back-adjustment. Roll weeks are marked; a level change at a roll is not an investment return.
- Latest uranium may use an earlier month's average metal price. This is not a same-day spot ratio.
- Points after each row's monthly/quarterly history are genuine completed-week observations (Friday-labeled; at least 3 business days for averages). Priced in gold using the same week's World Gold Council weekly average. Stocks (debt, Fed balance sheet) are end-of-week or source-published weekly observations, not averages. Nothing is forward-filled from monthly data; rows without a weekly source keep their existing cadence.
- No free weekly silver source exists, so weekly points carry no oz Ag value: silver denomination of weekly points ends at the last monthly point, and row-level oz Ag keeps the last monthly conversion. Gold and USD denominations are genuine weekly.
- Weekly row sources: EIA Europe Brent spot weekly average; 10Y minus 2Y Treasury (Treasury daily par yield curve), completed-week average; US Treasury Debt to the Penny, end-of-week total public debt outstanding; Dow Jones daily closes (CNBC), completed-week average; Fed total assets (H.4.1 Table 5, Wednesday level), source weekly stock; Fed funds effective rate (NY Fed EFFR), completed-week average; Treasuries held outright by the Fed (H.4.1 Table 1, Wednesday level), source weekly stock; EIA Henry Hub natural gas spot weekly average; Freddie Mac PMMS 30Y fixed, source-published weekly average; US 10Y TIPS real yield (Treasury daily real par yield curve), completed-week average; S&P 500 daily closes (CNBC), completed-week average; US 10Y Treasury yield (Treasury daily par yield curve), completed-week average; EIA WTI Cushing spot weekly average

Values priced in gold use the gold price of the same period as each row (weekly rows use weekly averages; monthly rows use monthly averages). Rows carry their own as-of dates and update at their native frequency. Republication rights for underlying sources remain with those sources.


## Historical gold comparisons

Dated full-history comparisons use the time-weighted median, not an annual average. Histories differ and may contain proxies. Percentiles are not forecasts or rankings of investment merit.

### Gold

Gold priced in gold is the constant, not a valuation comparison.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Silver

As of 2026-10, Silver: 0.013886 troy oz of gold per oz, 58.6% below its 1791-07-01 to 2026-10-01 time-weighted median of 0.03358 troy oz of gold per oz (No Time For Bull model; monthly avg). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1960, annual or derived history.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US dollar

As of 2026-11-13, US dollar: 0.00025072 troy oz of gold per $1, 99.5% below its 1791-07-01 to 2026-11-13 time-weighted median of 0.048379 troy oz of gold per $1 (No Time For Bull model; completed-week average (2026-11-09 to 2026-11-13); not Friday close). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1960, annual history derived from the gold series.

US dollar priced in gold: 1 USD = 1 / gold price in USD. Derived from this page's gold row (same sources and dates: World Bank monthly averages, MeasuringWorth annual history before 1960); not a separate data series.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US Dollar Index

Native rate, ratio or index, not a price in gold ounces.

US Dollar Index (DXY) is rebuilt from FRED exchange rates with the ICE DXY formula (from 1980) and spliced to the Fed major currencies index before 1980. It is shown in index points in every unit mode and is not the ICE-published series.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Copper (LME grade A)

As of 2026-10, Copper (LME grade A): 3.5342 troy oz of gold per tonne, 42.8% below its 1960-01-01 to 2026-10-01 time-weighted median of 6.1825 troy oz of gold per tonne (No Time For Bull model; monthly avg). Full-history comparison; histories may include proxies. See this row's source and method notes.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Uranium U3O8 (spot)

As of 2026-10-30, Uranium U3O8 (spot): 0.022302 troy oz of gold per lb, 26.1% below its 1988-01-01 to 2026-10-30 time-weighted median of 0.030174 troy oz of gold per lb (No Time For Bull model; month-end spot average (UxC/TradeTech via Cameco)). Full-history comparison; histories may include proxies. See this row's source and method notes.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Crude oil (WTI)

As of 2026-11-06, Crude oil (WTI): 0.023882 troy oz of gold per bbl, 53.6% below its 1861-07-01 to 2026-11-06 time-weighted median of 0.051429 troy oz of gold per bbl (No Time For Bull model; monthly avg; weekly since 2026-11-06). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1982, annual oil history.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Crude oil (Brent)

As of 2026-11-06, Crude oil (Brent): 0.024987 troy oz of gold per bbl, 48.9% below its 1861-07-01 to 2026-11-06 time-weighted median of 0.048857 troy oz of gold per bbl (No Time For Bull model; monthly avg; weekly since 2026-11-06). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1960, annual oil proxy.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Natural gas (US)

As of 2026-11-06, Natural gas (US): 0.00064951 troy oz of gold per MMBtu, 82.6% below its 1922-07-01 to 2026-11-06 time-weighted median of 0.00373 troy oz of gold per MMBtu (No Time For Bull model; monthly avg; weekly since 2026-11-06). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1960, annual wellhead proxy.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Natural gas (Europe, TTF)

As of 2026-10, Natural gas (Europe, TTF): 0.0069428 troy oz of gold per MMBtu, 26.5% below its 1960-01-01 to 2026-10-01 time-weighted median of 0.0094398 troy oz of gold per MMBtu (No Time For Bull model; monthly avg). Full-history comparison; histories may include proxies. See this row's source and method notes. Before April 2015, European import-price proxy, not TTF.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Coal (Australian, Newcastle)

As of 2026-10, Coal (Australian, Newcastle): 0.037101 troy oz of gold per tonne, 60.0% below its 1970-01-01 to 2026-10-01 time-weighted median of 0.092857 troy oz of gold per tonne (No Time For Bull model; monthly avg). Full-history comparison; histories may include proxies. See this row's source and method notes.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Lumber (LBR rolling futures; since Sep 2022)

As of 2026-10, Lumber (LBR rolling futures; since Sep 2022): 0.1279 troy oz of gold per 1,000 board ft, 39.1% below its 2022-09-01 to 2026-10-01 time-weighted median of 0.20987 troy oz of gold per 1,000 board ft (No Time For Bull model; monthly avg). Full-history comparison; histories may include proxies. See this row's source and method notes.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US electricity (all sectors)

As of 2026-08, US electricity (all sectors): 0.033711 troy oz of gold per MWh, 80.7% below its 1960-07-01 to 2026-08-01 time-weighted median of 0.17512 troy oz of gold per MWh (No Time For Bull model; monthly avg). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 2001, annual history.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US median new-home price

As of 2026-07, US median new-home price: 92.158 troy oz of gold per home, 65.0% below its 1890-07-01 to 2026-07-01 time-weighted median of 263.44 troy oz of gold per home (No Time For Bull model; quarterly). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1963, a rescaled home-price index, not observed median new-home prices; full-history comparison is approximate.

US median new-home price: Census median sales price of new houses sold (FRED MSPUS, nominal dollars, quarterly) from 1963. Before 1963 the row is a Shiller-based nominal US home price index (1890-1962, closely tracking but not an exact copy of the Robert Shiller series) rescaled to the 1963 Census level, so those values are approximate and are not observed median prices. From 1963 the series covers new homes only; the earlier part is a rescaled all-home index. For existing-home price changes see the US home price index vs gold row.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US home price index vs gold, Jan 2000 = 100

Native rate, ratio or index, not a price in gold ounces.

US home price index vs gold: the S&P CoreLogic Case-Shiller US National Home Price Index (repeat sales of single-family homes, FRED CSUSHPINSA, from 1987) divided by the monthly average gold price, with both set to 100 in January 2000. It is an index, not ounces per home, and it is shown in index points in every unit mode. Case-Shiller is a three-month average and is revised.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### S&P 500 (price index)

As of 2026-11-13, S&P 500 price-index level: 1.8976 troy oz of gold per index pt, 284.2% above its 1871-01-01 to 2026-11-13 time-weighted median of 0.49395 troy oz of gold per index pt (No Time For Bull model; completed-week average (2026-11-09 to 2026-11-13); not Friday close). Full-history comparison; histories may include proxies. See this row's source and method notes.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Dow Jones Industrial Average

As of 2026-11-13, Dow Jones price-index level: 13.125 troy oz of gold per index pt, 128.3% above its 1885-02-01 to 2026-11-13 time-weighted median of 5.7489 troy oz of gold per index pt (No Time For Bull model; completed-week average (2026-11-09 to 2026-11-13); not Friday close). Full-history comparison; histories may include proxies. See this row's source and method notes.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### 10Y Treasury futures (ZN reference quote)

Fewer than 24 valid observations; no historical comparison.

CME final daily settlements, decimal quote per $100 face. Gold equivalent per $100,000 face = 1,000 x weekly mean decimal quote / same-week World Gold Council gold USD/oz. Futures reference quote only: not margin, invested capital, delivery invoice price, cash bond value or total return. Invoice pricing also uses a conversion factor and accrued interest. At least three dated final daily settlements per completed week. No silver or real-dollar conversion. Free browser history currently starts November 9, 2026; earlier requests were empty. The first weekly point is November 13, 2026. Switch to the next quarterly delivery contract on the first Monday on or after the 20th of the month before delivery; one contract for the full week. No back-adjustment. Roll weeks are marked; a level change at a roll is not an investment return.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Treasury bond futures (ZB reference quote)

Fewer than 24 valid observations; no historical comparison.

CME final daily settlements, decimal quote per $100 face. Gold equivalent per $100,000 face = 1,000 x weekly mean decimal quote / same-week World Gold Council gold USD/oz. Futures reference quote only: not margin, invested capital, delivery invoice price, cash bond value or total return. Invoice pricing also uses a conversion factor and accrued interest. At least three dated final daily settlements per completed week. No silver or real-dollar conversion. Free browser history currently starts November 9, 2026; earlier requests were empty. The first weekly point is November 13, 2026. Switch to the next quarterly delivery contract on the first Monday on or after the 20th of the month before delivery; one contract for the full week. No back-adjustment. Roll weeks are marked; a level change at a roll is not an investment return.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Avg hourly earnings (production workers)

As of 2026-10, Avg hourly earnings (production workers): 0.0079781 troy oz of gold per hour, 73.0% below its 1939-01-01 to 2026-10-01 time-weighted median of 0.029565 troy oz of gold per hour (No Time For Bull model; monthly). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1964, rescaled manufacturing earnings; full-history comparison is approximate.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US M2 money supply

As of 2026-09, US M2 money supply: 5.4211 billion troy oz of gold, 43.5% below its 1959-01-01 to 2026-09-01 time-weighted median of 9.6025 billion troy oz of gold (No Time For Bull model; monthly, seasonally adjusted). Full-history comparison; histories may include proxies. See this row's source and method notes. Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Who owns the federal debt (and the Fed's balance sheet)

As of 2026-11-13, Total federal debt: 10.181 billion troy oz of gold, 16.6% above its 1939-06-30 to 2026-11-13 time-weighted median of 8.73241 billion troy oz of gold (No Time For Bull model; quarter-end stock (annual before 1966); weekly since 2026-09-25). Full-history comparison; histories may include proxies. See this row's source and method notes. Before 1966, annual fiscal-year history. Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.

Ownership split: approximate quarter end. Fed stocks use the last Wednesday in the quarter-end month. Foreign holders are US Treasury TIC estimates of foreign holdings of Treasury securities at quarter-end months (official vs private/other). Other domestic holders are a residual: total debt minus government accounts minus Fed Treasuries minus TIC foreign holdings. TIC and Treasury/Fed debt definitions differ, so the residual is approximate. Non-Treasury Fed assets are NOT federal debt. Dollar-equivalent gold, not gold owned.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Federal debt held by the public

As of 2026-06-30, Federal debt held by the public: 7.49894 billion troy oz of gold, 4.5% below its 1970-03-31 to 2026-06-30 time-weighted median of 7.85497 billion troy oz of gold (No Time For Bull model; quarter-end stock). Full-history comparison; histories may include proxies. See this row's source and method notes. Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.

Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Federal debt held by government accounts

As of 2026-06-30, Federal debt held by government accounts: 1.83464 billion troy oz of gold, 48.4% below its 1981-03-31 to 2026-06-30 time-weighted median of 3.55837 billion troy oz of gold (No Time For Bull model; quarter-end stock). Full-history comparison; histories may include proxies. See this row's source and method notes. Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.

Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Fed total assets

As of 2026-11-11, Fed total assets: 1.6946 billion troy oz of gold, 29.2% below its 2002-12-25 to 2026-11-11 time-weighted median of 2.39401 billion troy oz of gold (No Time For Bull model; month-end: last weekly stock; weekly since 2026-11-04). Full-history comparison; histories may include proxies. See this row's source and method notes. Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.

Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Treasuries held by the Fed

As of 2026-11-11, Treasuries held by the Fed: 1.1499 billion troy oz of gold, 31.3% below its 2002-12-25 to 2026-11-11 time-weighted median of 1.67461 billion troy oz of gold (No Time For Bull model; month-end: last weekly stock; weekly since 2026-11-04). Full-history comparison; histories may include proxies. See this row's source and method notes. Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.

Dollar-equivalent in gold, not gold owned. Stock divided by same-month average metal price. Overlaps other balance rows; do not sum.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US total credit market debt / GDP

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### 30Y mortgage (PMMS); all-term MIRS proxy before 1971

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Fed funds (effective); discount rate before 1954

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US 10Y Treasury yield

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US 10Y real yield (TIPS)

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Yield curve: 10Y minus 2Y Treasury (pp)

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Gold / silver ratio (oz Ag per oz Au)

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### Gold / oil ratio (WTI bbl per oz Au)

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)

### US CPI (all items, 1982-84=100)

Native rate, ratio or index, not a price in gold ounces.

[Existing model, sources and notes](https://www.notimeforbull.com/prices/)
