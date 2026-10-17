# Phase 5.2 — Time exploration / year-by-year analysis

## Scope and implementation

Presentation only. Saved Phase 3 primary market observations (`robust_z`, 12-month detector window) remain the source. No Python API, statistical code, datasets, outputs, configuration, Evolus workflow or AMD settings changed.

- Historical remains the default, with full saved reporting range January 2018–July 2026, observed/expected series and signal markers. Unscored observations now have neutral hollow markers, explicit tooltip status and a neutral explanatory notice.
- By year defaults to the latest available year (2026) and uses localized month labels. Only actual saved reporting dates appear; 2026 contains seven observations. Observed and expected values, residual chart, signal markers, saved-classification counts and accessible monthly details share the selected year.
- Compare years defaults to the latest three years, supports up to four with keyboard-accessible checkboxes, and aligns January–December. It displays observed values only. Missing months remain null, lines do not bridge missing values, and no aggregation, normalization or new expected values are introduced. Tooltip reports each year's observed value, dates and saved signal status. An expected-lines toggle was omitted to preserve readability.
- Metric switching preserves view/year selections. Query parameters support `metric=claims|premiums|ratio`, `view=historical|year|compare`, `year=2025`, and `years=2023,2024,2025,2026`. Invalid values are sanitized; selections are restored on reload. URL updates replace the current entry rather than adding history entries for each control click.
- Year summaries count existing NORMAL/WATCH/ALERT/NOT_SCORED rows for the selected metric. They are not new signals or confirmed incidents. In 2025, market claims has 9 NORMAL, 0 WATCH, 3 ALERT and 0 unscored; the ratio has 8 NORMAL, 2 WATCH, 2 ALERT and 0 unscored. Matching FLAGSHIP links point to existing reports/pages. Narrative year-insight generation was omitted; saved counts provide a neutral summary.
- First scored primary observation: report **2021-10-31**, simulated availability **2022-01-01**. Expected-value warm-up and detector-score warm-up are distinct: an expected value and residual can exist while robust z remains unavailable.

## Exact 2020 spike from saved outputs

Source: `data/processed/cnbs/expected-behavior/primary_dynamic.csv`, market level, baseline method `robust_z`, baseline window `12`. The following are stored values, including floating-point representation. Ratio values in this table are dimensionless source values; the UI formats levels as percentages and absolute differences as percentage points.

| Field | Monthly claims | Claims-to-premiums ratio |
|---|---|---|
| report_date | 2020-11-30 | 2020-11-30 |
| availability_date | 2021-02-01 | 2021-02-01 |
| observed_value | 226427838.52 | 1.6935946350277675 |
| expected_value | 75397334.19750005 | 0.609831335219926 |
| residual | 151030504.32249996 | 1.0837632998078415 |
| robust z-score | blank / unavailable | blank / unavailable |
| saved signal classification | blank / unscored | blank / unscored |
| residual_evaluation_status | insufficient_history | insufficient_history |
| residual_signal_reason | insufficient_history | insufficient_history |
| model_status | modeled | modeled |
| trend_history_count | 12 | 12 |
| seasonal_history_count | 2 | 2 |
| residual_history_count | 1 | 1 |

Both are the largest observed values within their respective 2020 saved market series. Neither is a saved adjusted NORMAL, WATCH or ALERT. The display says **Sin puntuar — Historia previa insuficiente**. The entire selected 2020 year has 12 unscored observations for each of these metrics. No manual classification or cause has been inferred.

## Validation

- Backend: `docker compose run --rm app pytest` — **281 passed**, unchanged regression suite.
- Frontend: `npm test` — **17 passed**, including year selection, query defaults, exact November 2020 saved values/status, missing-month handling, unchanged comparison values and bilingual month labels.
- Browser: the full original and expanded suite passed **9 tests**, including the dedicated yearly-table desktop/mobile check. All tests are offline with respect to model/workflow execution; no new integration calls were made.
- `npm run typecheck` — passed.
- `docker compose build` — passed, including production TypeScript checks.
- Protected-file SHA-256 baseline: `.local/phase52-preservation.json` — **166/166 unchanged**, including all data, analytical code, prior analytical reports, configuration, selections, signal packages, schemas and Evolus resources.
- `git diff --check` — passed.

Visual inspection covered historical claims, 2020 claims/ratio, 2025 claims/ratio and comparison of 2023–2026, plus mobile comparison and year controls. Month labels angle on narrow screens to prevent overlap. Local ignored screenshots: `.local/phase52-2020-claims.png`, `phase52-2020-ratio.png`, `phase52-2025-claims.png`, `phase52-2025-ratio.png`, `phase52-compare.png`, `phase52-compare-mobile.png`, `phase52-year-mobile.png`.

## Demo links

- Historical claims: http://localhost:3000/?metric=claims&view=historical
- 2020 claims: http://localhost:3000/?metric=claims&view=year&year=2020
- 2020 ratio: http://localhost:3000/?metric=ratio&view=year&year=2020
- 2025 claims: http://localhost:3000/?metric=claims&view=year&year=2025
- 2025 ratio: http://localhost:3000/?metric=ratio&view=year&year=2025
- Four-year comparison: http://localhost:3000/?metric=claims&view=compare&years=2023,2024,2025,2026

The current historical snapshot and conservative availability policy remain a **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time is **NOT VALIDATED**. No forecasting, reclassification or seasonality estimation is performed by these views. AMD remains unconfigured and Evolus behavior is unchanged.
