# Phase 3.5 validation record

Validated 2026-10-14. This phase consumes saved outputs only; no analytical pipeline or detector model was rerun to generate cases.

## Docker commands

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/generate_case_studies.py
```

Build: passed. Tests: **165 passed**, including all 135 pre-existing tests and 30 case-selection tests. Case generator: passed, exit 0. Docker: Python 3.12.15, pytest 8.4.2. The host Python lacks pytest; authoritative results above come from Docker.

The new tests cover score range/determinism; classification thresholds/evidence gates; candidate extraction; calendar neighborhoods and missing/censored observations; preserved availability dates; no future follow-up or future-institution influence on suitability; same-direction backward persistence; sensitivity tolerance; missing institution counterfactuals; source negatives and review propagation; residual-vs-accounting-negative distinction; raw/adjusted controls; code diversity; protected output paths; input checksum/cutoff rejection; deterministic generation and source-byte preservation.

## Outputs

- 122 candidates: 61 scored residual robust-z ALERTs plus 61 jointly scored raw-ALERT downgrade controls.
- 2 FLAGSHIP, 43 SUPPORTING, 13 RESEARCH_ONLY, 64 REJECTED_FOR_DEMO.
- Four selected cases: two market FLAGSHIPs and two different institution SUPPORTING cases.
- Eight detailed English reports (all six initial examples plus two newly selected institution examples); two Spanish FLAGSHIP companions; bilingual index; full selection summary.
- Candidate CSV, 854 neighborhood positions, provenance manifest, and eight PNG charts (four per FLAGSHIP).
- Reports/charts are generated only in the separate case-study directory. Existing Phase 2/3 outputs are not rewritten.

## Preservation and interpretation checks

All **127** previously captured files under data, analytical source/scripts/tests/config, prior reports and methodology documents retained identical SHA-256 values. This includes original raw/processed/monthly datasets, saved backtests, configurations, availability helper, model/detector source and existing tests. README navigation/status edits are intentional. Pre-existing uncommitted project changes remain intact.

Local Markdown links and chart references are checked. Narrative numerical fields are formatted directly from saved rows; evidence CSV fields preserve saved strings. The source manifest hashes are verified before generation and input/output hashes appear in case_selection_manifest.json. Repeated generation is deterministic for numerical evidence, reports and charts in the validated Docker environment. Charts were visually inspected; both date axes show actual corresponding report/availability dates.

Replay remains **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time remains **NOT VALIDATED**. Follow-up after each signal is retrospective context, not decision-time score input. Missing institution fits remain unassessed. Neither market FLAGSHIP earns persistence points at detection. No external cause was researched or inferred; investigation questions remain unanswered. No new detector or downstream integration was implemented.
