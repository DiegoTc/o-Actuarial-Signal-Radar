# Phase 2 validation record

Validated 2026-10-14. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

## Docker commands and exact results

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_statistical_backtest.py
```

All completed successfully (exit 0) on the finalized code. The initial sandboxed build could not access Docker builder files; the approved retry succeeded. Tests: **104 passed**, Python 3.12.15, pytest 8.4.2. This includes the original 62 tests and 42 Phase 2 cases covering baseline arithmetic, status/quality behavior, calendar eligibility integration, state evolution, future-value/future-institution leakage, persistence, aggregation, denominator safety, deterministic artifacts and source preservation.

## Reference evaluation

- Cutoff: 2026-10-03 (snapshot date; not the date of running the software).
- Input: 2,288 existing monthly-derived records, 1,144 per resource.
- Eligible source rows: 2,266; blocked numerical exclusions: 2; usable source rows: 2,264.
- Pending source rows: 22, for August 2026, simulated available 2026-11-01.
- Report periods evaluated: 103, 2018-01-31 through 2026-07-31.
- Availability timeline: 2018-04-01 through 2026-10-01.
- First scored availability: 2018-10-01 for 6-month windows; 2019-04-01 for 12-month windows and EWMA/CUSUM; 2020-04-01 for 24-month windows.
- Institution output: 20,394 method/window rows; 17,508 scored.
- Market output: 2,781 method/window rows across premiums, claims and their ratio; 2,421 scored.
- Signals across all variants: institution NORMAL 15,229 / WATCH 1,195 / ALERT 1,084; market NORMAL 2,113 / WATCH 175 / ALERT 133.

Counts repeat observations across methods/windows. They are not independent incidents, validated anomalies or estimates of predictive accuracy. Full measured results are in [baseline_summary.md](baseline_summary.md), [signal_summary.md](signal_summary.md), [method_comparison.md](method_comparison.md), [data_quality_interactions.md](data_quality_interactions.md) and [summary.json](summary.json).

## Preservation and reproducibility

All 65 pre-existing files under data/, actuarial-engine/, scripts/, tests/ and config/ matched the hashes captured before Phase 2 work. This includes raw data, prepared data, monthly-derived files, original manifests, samples, semantic evidence, the availability helper and derivation logic. Only separate backtest outputs were added to data/processed/cnbs/backtest/. No ingestion, preparation, evidence-fetch or monthly-derivation command was run.

Input/output/configuration/helper/implementation hashes are stored in data/processed/cnbs/backtest/backtest_manifest.json. Output CSV hashes and inclusive cutoff compliance were independently inspected. A synthetic end-to-end test produces byte-identical CSVs, manifests and generated reports across two runs with unchanged inputs. No timestamps or random seeds enter detector decisions.

## Phase boundary

Rolling baselines, standard/robust z, EWMA residual scoring, adaptive two-sided CUSUM and statistical retrospective evaluation are implemented. No ML detector, AMD/ROCm/vLLM, Evolus, API, dashboard or LLM explanation was added. No causal or strict point-in-time claims are established. Phase 3 is recommended for reviewed robustness work only; it has not been started.
