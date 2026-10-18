# Independent actuarial forecasting research

Scope: CNBS Honduras / Seguros Generales / Vehículos Automotores / Nacional; monthly **monetary claims accounting increments**, not claim counts. This research extension is separate from the validated anomaly detector and production dashboard. No service is deployed or modified.

1. [Data readiness](reports/data_readiness.md) — original retained October 3 snapshot, hashes, July cutoff, quality and timing caveats.
2. [Protocol and mathematical specifications](METHODOLOGY.md) — four fixed models, rolling-origin evaluation, selection gates and interval assumptions.
3. [Frozen results](results/) — run-specific report, forecasts, comparisons, coefficients, figures and integrity manifest.
4. [Validation and interpretation](reports/validation.md) — genuine comparison results, repeat execution, regression checks and remaining work.

Completed run: [report](results/2026-10-18-v1/research_report.md), [seven-month forecast CSV](results/2026-10-18-v1/seven_month_forecast.csv), [model comparison](results/2026-10-18-v1/model_comparison.csv), [forecast uncertainty](results/2026-10-18-v1/forecast_uncertainty.png). The selected trend-plus-seasonality approach reduced confirmation MAE by 37.316% versus seasonal naive across 14 target months; this limited retrospective comparison is not proof of prospective superiority.

## Commands — from repository root

Use Python 3.12 and an isolated, Git-ignored environment:

```sh
python3.12 -m venv .local/forecasting/venv
.local/forecasting/venv/bin/pip install -r research/forecasting/requirements.txt

# Audit first: no download, monthly derivation, or forecast fitting.
.local/forecasting/venv/bin/python -m research.forecasting.audit

# Review the audit, then run the research-only tests.
.local/forecasting/venv/bin/python -m pytest -c research/forecasting/pytest.ini research/forecasting/tests

# Use a NEW directory for each run; overwriting is refused.
.local/forecasting/venv/bin/python -m research.forecasting.experiment \
  --output research/forecasting/results/2026-10-18-v1

# Read-only verification after generation.
.local/forecasting/venv/bin/python -m research.forecasting.experiment \
  --verify research/forecasting/results/2026-10-18-v1

# Existing production regression suite, unchanged.
docker compose run --rm app pytest
```

A fresh clone lacks the Git-ignored source snapshots. The audit must stop rather than silently downloading replacement data. Obtain the retained private/local snapshot by a separate explicit process. Frozen research results include a small aggregate training extract for review, not full raw datasets. It is not automatically substituted for a missing original snapshot.

## Timing and scientific status

Training reporting periods end **2026-07-31**. Targets are August 2026–February 2027. The primary mode conditions on the complete July reporting information set, which the existing availability helper admits on **2026-10-01**, not July 31. It is a **current-vintage conditional forecasting experiment** executed in October 2026. August/September targets are retrospective. Strict historical point-in-time validity remains **NOT VALIDATED**.

The separate `lag_aware` sensitivity trains only through April for a simulated July-31 decision date, and bridges May–July without observing them. Neither mode changes the existing production lag or anomaly methodology.

Two confirmation origins provide limited evidence. Failure to beat seasonal naive is a legitimate result. Intervals are conditional/approximate, not actuarial capital thresholds. February outcomes may not be available by the February 2027 presentation; do not promise a full seven-month prospective evaluation then.

No credentials, live inference, cloud services, new raw downloads, production dependency changes, commit, push or deployment are required by these commands.
