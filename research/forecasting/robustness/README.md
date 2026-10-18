# Forecasting robustness and sensitivity — v2

Independent actuarial research on the existing `research/claims-forecast-2026-2027` branch. V1 forecasts, manifests, source code, original data, anomaly detection and production integrations remain unchanged. No alternative automatically replaces v1. All comparisons are exploratory: v1's historical outcomes are already known.

- [Protocol](METHODOLOGY.md): fixed comparisons, formulas, overlapping-origin interpretation, purged interval calibration and influence diagnostics.
- [Configuration](config.json): 6/12/18/24-month median/mean trends; experimental linear trend; shorter-lookback median, mean and harmonic seasonality.
- [Results](results/): frozen run-specific numerical tables, parameters, provenance, interval evidence, scientific report and six figures.
- [Reports](reports/): final validation and presentation guidance.

Completed outputs: [scientific conclusions](reports/conclusions.md), [primary frozen findings](results/2026-10-18-v2/research_findings.md), [trend comparison](results/2026-10-18-v2/trend_comparison.csv), [seasonal comparison](results/2026-10-18-v2/seasonal_comparison.csv), [matched interval comparison](results/2026-10-18-v2/interval_matched.csv), and [supplementary interval-influence results](results/2026-10-18-v2-interval-audit/interval_influence_summary.csv).

[Validation record](reports/validation.md): 92 research tests, 313 unchanged backend tests, independent numerical reproduction and 390 protected-file hashes checked.

## Reproduce from repository root

Use the existing isolated Python 3.12 environment and v1 pinned dependencies. No production dependency is added:

```sh
python3.12 -m venv .local/forecasting/venv
.local/forecasting/venv/bin/pip install -r research/forecasting/requirements.txt

.local/forecasting/venv/bin/python -m research.forecasting.experiment \
  --verify research/forecasting/results/2026-10-18-v1

.local/forecasting/venv/bin/python -m pytest \
  -c research/forecasting/pytest.ini \
  research/forecasting/tests research/forecasting/robustness/tests

# Choose a NEW directory; overwriting frozen results is refused.
.local/forecasting/venv/bin/python -m research.forecasting.robustness.run \
  --output research/forecasting/robustness/results/2026-10-18-v2

.local/forecasting/venv/bin/python -m research.forecasting.robustness.run \
  --verify research/forecasting/robustness/results/2026-10-18-v2

docker compose run --rm app pytest
```

The supplementary calibration-pool diagnostic is declared in a [separate post-primary protocol](reports/interval-influence-protocol.md). It does not modify the primary bundle. Reproduce into a NEW output directory:

```sh
.local/forecasting/venv/bin/python -m research.forecasting.robustness.interval_influence \
  --primary research/forecasting/robustness/results/2026-10-18-v2 \
  --output research/forecasting/robustness/results/2026-10-18-v2-interval-audit
```

Original raw snapshots are Git-ignored; a fresh clone must obtain the separately retained matching snapshot. Missing inputs stop execution. There is no implicit download or substitution with a newer vintage. The run checks the original source hashes, cutoff and v1 integrity before fitting.

## Reading the outputs

`trend_comparison.csv` and `seasonal_comparison.csv` use the same 16 quarterly origins and 112 errors per candidate. `legacy_july.csv` is separate. `by_origin.csv`, `by_horizon.csv`, `by_period.csv` and `stability.csv` expose variation. Origin count is **not independent evidence count**: windows overlap and all share training history.

`interval_matched.csv` compares both methods on identical eligible rows, while `interval_all.csv` shows availability differences. `calibration_predictions.csv` and calibration cutoffs allow auditing that only fully matured past seven-month windows enter the empirical intervals. No coverage guarantee is implied. The interval study also reports a separate lag-aware baseline sensitivity.

`influence_predictions.csv` contains hypothetical fitting exclusions only; original stored data and primary forecasts retain all extreme/negative amounts. `target_error_concentration.csv` separately describes error concentration without replacing primary scores. Dates are reporting periods, not asserted historical publication dates; all projections use the retained October 2026 vintage.

No final v2 seven-month forecast is selected or published. Keep the original v1 July-cutoff projections unchanged. Full February 2027 outcomes may not be available for the February presentation.
