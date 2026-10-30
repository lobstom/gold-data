# Observation freshness report

Generated 2026-10-30T13:37:15-07:00.
Model update label 2026-10-26. This is not the observation date of every row.
This generator performs no live upstream retrieval. Dated manual publisher checks, where available, are listed separately below. Other release expectations remain unverified; age flags are review prompts, not missed-release claims.

| Row | Observation period | Cadence | Age review | Last evidenced source check |
| --- | --- | --- | --- | --- |
| Gold | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Silver | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| Copper (LME grade A) | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| Uranium U3O8 (spot) | 2026-10-12 | month-end history, latest UxC weekly | review_old_vintage | Unverified |
| Crude oil (WTI) | 2026-10-16 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Crude oil (Brent) | 2026-10-16 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Natural gas (US) | 2026-10-16 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Natural gas (Europe, TTF) | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| Coal (Australian, Newcastle) | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| Lumber (LBR rolling futures; since Sep 2022) | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| US electricity (all sectors) | 2026-08 | monthly avg | review_old_vintage | Unverified |
| US median new-home price | 2026-Q2 | quarterly | review_old_vintage | Unverified |
| US M2 money supply | 2026-08 | monthly, seasonally adjusted | review_old_vintage | Unverified |
| Who owns the federal debt (and the Fed's balance sheet) | 2026-10-23 | quarter-end stock (annual before 1966); weekly since 2026-08-28 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Avg hourly earnings (production workers) | 2026-09 | monthly | within_age_review_threshold | Unverified |
| S&P 500 (price index) | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Dow Jones Industrial Average | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| 30Y mortgage (PMMS); all-term MIRS proxy before 1971 | 2026-10-22 | weekly PMMS; annual all-term proxy 1963-1970 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Fed funds (effective); discount rate before 1954 | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| US 10Y Treasury yield | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| US 10Y real yield (TIPS) | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Yield curve: 10Y minus 2Y Treasury (pp) | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| US total credit market debt / GDP | 2026-Q2 | quarterly | review_old_vintage | Unverified |
| US CPI (all items, 1982-84=100) | 2026-09 | monthly | within_age_review_threshold | Unverified |
| Gold / silver ratio (oz Ag per oz Au) | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| Gold / oil ratio (WTI bbl per oz Au) | 2026-10-16 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | Unverified |
| US home price index vs gold, Jan 2000 = 100 | 2026-07 | monthly (3-month average, published about two months late) | review_old_vintage | Unverified |
| US Dollar Index | 2026-09 | monthly avg | within_age_review_threshold | Unverified |
| US dollar | 2026-10-23 | monthly avg; weekly since 2026-10-02 | within_age_review_threshold | Unverified |
| Fed total assets | 2026-10-21 | month-end: last weekly stock; weekly since 2026-10-07 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Treasuries held by the Fed | 2026-10-21 | month-end: last weekly stock; weekly since 2026-10-07 | within_age_review_threshold | 2026-10-26T08:01:51.937648-07:00 |
| Federal debt held by the public | 2026-Q2 | quarter-end stock | within_age_review_threshold | Unverified |
| Federal debt held by government accounts | 2026-Q2 | quarter-end stock | within_age_review_threshold | Unverified |

## Dated publisher release checks

These are dated manual release-period checks, not a new fetch on each report build. They do not verify stored values or gold conversions. No model data was changed.

### US electricity (all sectors)
Checked 2026-10-30T13:35:02-07:00. Source [US Energy Information Administration](https://www.eia.gov/electricity/monthly/).
Publisher release 2026-10-23; latest published period 2026-08; stored model period 2026-08.
August 2026 is the latest published Electric Power Monthly period. The age flag is a review heuristic, not a missed-ingestion claim. This verifies release period, not the stored price value or gold denominator.
Next announced release date 2026-11-24; no release time is inferred.

### US M2 money supply
Checked 2026-10-30T13:35:02-07:00. Source [Federal Reserve H.6](https://www.federalreserve.gov/releases/h6/current/default.htm).
Publisher release 2026-10-27; latest published period 2026-09; stored model period 2026-08.
Table 1 contains September 2026 seasonally adjusted M2, 23413.9 billion USD. Release is after the intentional October 26 model cut. This is next-refresh evidence, not failed ingestion; no stored data or gold conversion is changed.
