# Case studies — Phase 3.5

[Español](case_study_index.es.md) · [Complete ranking and limitations](case_selection_summary.md) · [Scoring methodology](../../docs/case-study-selection-methodology.md)

**LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time **NOT VALIDATED**. Consumes saved Phase 2/3 signals without changing historical calculations. 122 candidate/control observations evaluated; 4 shortlisted cases. Suitability is a presentation-selection rubric, not a new anomaly detector.

| Selected case | Class | Suitability / 18 | Report period | Simulated availability |
| --- | --- | --- | --- | --- |
| [Market: monthly_claims — 2025-09-30](market_claims_2025_09.md) | FLAGSHIP | 13 | 2025-09-30 | 2025-12-01 |
| [Market: claims_to_premiums_ratio — 2025-03-31](market_ratio_2025_03.md) | FLAGSHIP | 12 | 2025-03-31 | 2025-06-01 |
| [Institution 0608: monthly_premiums — 2024-08-31](institution_0608_premiums_2024_08.md) | SUPPORTING | 14 | 2024-08-31 | 2024-11-01 |
| [Institution 0603: monthly_claims — 2024-05-31](institution_0603_claims_2024_05.md) | SUPPORTING | 14 | 2024-05-31 | 2024-08-01 |

## Reading order and demo recommendation

Present market September 2025 claims for monetary magnitude and sensitivity robustness; market March 2025 ratio for RAW NORMAL → ADJUSTED ALERT; optionally institution 0608 August 2024 premiums for an independent institution-level adjusted-only example. Keep its SUPPORTING status visible. Institution 0603 May 2024 claims provides a lower-than-expected contrast.

## Investigated but not shortlisted

- [Institution 0617: monthly_premiums — 2026-03-31](institution_0617_premiums_2026_03.md): SUPPORTING — Useful statistical contrast; institution counterfactual coverage is incomplete.
- [Market: monthly_claims — 2025-02-28](market_claims_2025_02.md): SUPPORTING — Limited corroboration, persistence, materiality or sensitivity robustness.
- [Institution 0613: monthly_claims — 2025-09-30](institution_0613_claims_2025_09.md): RESEARCH_ONLY — High source-quality risk or nearby negative-adjustment interpretation.
- [Market: monthly_claims — 2025-06-30](market_claims_2025_06.md): RESEARCH_ONLY — Adjusted ALERT downgraded by a scored sensitivity.

## Reproduce

```sh
docker compose run --rm app python scripts/generate_case_studies.py
```

The command verifies saved input hashes, writes only this case-study directory, and never reruns core models. Charts use a focused report-period window; top axes show the corresponding simulated availability dates. Follow-up after T is shaded and is not part of decision-time suitability. No external event evidence or cause is asserted.
