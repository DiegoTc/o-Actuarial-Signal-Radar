# Phase 3.5 — Signal validation and case selection

This phase reads saved Phase 3 outputs, including the raw Phase 2 method comparisons already retained in those outputs. It never refits trend, seasonality, thresholds or detectors. The primary reference is residual robust z with a **12-month detector window**, independent of the trend-window sensitivity. Official CNBS Automobile/Nacional scope is unchanged.

Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**. Availability remains governed by the existing [helper and methodology](historical-replay-methodology.md). No external event evidence is used to rank cases.

## Candidate universe and audit

Take every scored primary-reference residual ALERT, plus jointly scored raw ALERTs downgraded by adjustment as controls. Do not limit the search to the six proposed examples. Candidate identity is analysis level, institution code, metric and report period. All candidates receive seven explicit report-month positions T−3 through T+3, including missing/censored placeholders. December/February month arithmetic is calendar based; placeholder availability reuses the existing helper.

RAW_AND_ADJUSTED / ADJUSTED_ONLY / RAW_ONLY classify the **12-month robust-z reference**, not all methods collectively. A raw standard-z or CUSUM ALERT can coexist with an ADJUSTED_ONLY robust-z classification; the per-method table must remain visible.

The generator verifies the four scenario CSV hashes against `expected_behavior_manifest.json` and rejects rows beyond its saved evaluation cutoff. It writes separate candidate evidence, neighborhoods, reports, charts and a source/output hash manifest under `reports/case-studies/`. Protected source/data/prior-report trees are refused as output destinations. It does not rerun Phase 2/3 or reconstruct monthly amounts.

## Suitability rubric (0–18)

This is an exploratory, declared **case study suitability** rubric for a demo, not another anomaly score, statistical significance test, causal diagnosis or performance validation. These integer cutoffs are presentation-selection choices, not learned detector thresholds. They have not been validated against external outcomes. Larger z alone does not win.

| Dimension | Exact assignment |
|---|---|
| Statistical robustness | 0: no residual ALERT. 3: residual standard-z ALERT and residual CUSUM WATCH/ALERT agree with robust-z direction. 2: either standard-z or CUSUM WATCH/ALERT agrees. 1: robust ALERT alone. Unscored companion never corroborates. |
| Economic materiality | Existing exploratory HIGH=3, MEDIUM=2, LOW=1, missing=0. No new financial thresholds. Ratio bands do not represent Lempiras. |
| Persistence | Take the longer same-direction consecutive WATCH/ALERT run in robust z or CUSUM through T, using T−3…T only. Points = min(3, max(0, run−1)). One isolated alert scores 0; four consecutive non-NORMAL observations score 3. |
| Sensitivity robustness | 0 if fixed cohort is SENSITIVE, negative-fit is HIGHLY_SENSITIVE, or scored trend-window alternative is NORMAL or reverses robust-score direction. Otherwise 1 if any is partly/moderately sensitive or the window alternative is WATCH. Otherwise 3 only with all three saved comparisons scored, cohort ROBUST, negatives UNAFFECTED and alternative window ALERT. Otherwise 2 if negatives are structurally UNAFFECTED but counterfactual coverage is incomplete; 1 for remaining missing-evidence cases. |
| Data quality confidence | HIGH risk=0: current negative-sensitive observation, unsafe relative denominator, unmodeled row, material composition change, excluded contributors, or an institution negative-sensitive observation in T−3…T−1. MEDIUM=2: other current source/model quality flags or recent market negative-sensitive observations. LOW=3: none of these. A negative residual is not itself a source negative increment. |
| Narrative usefulness | ADJUSTED_ONLY=3 (raw NORMAL/WATCH → adjusted ALERT); RAW_AND_ADJUSTED=2; RAW_ONLY=1; OTHER=0. This describes demonstrative contrast, not events or inferred cause. |

CUSUM agreement uses its saved signed dominant cumulative state. A CUSUM score is not a standard or robust z-score. Persistence never counts opposite-direction movement as continued same-direction change.

## Sensitivity labels

For saved cohort and negative-fit comparisons, require a scored alternative. Compare robust-score direction, signal level, and residual change:

```text
relative_residual_change = abs(alternative_residual - primary_residual)
                           / max(abs(primary_residual), 1e-12)
```

Same level and direction with change ≤25% yields **ROBUST** / **UNAFFECTED**. Same direction and alternative WATCH/ALERT otherwise yields **PARTIALLY_ROBUST** / **MODERATELY_SENSITIVE**. Remaining scored alternatives yield **SENSITIVE** / **HIGHLY_SENSITIVE**. The 25% tolerance is an explicit exploratory suitability convention, not a detector threshold; it avoids interpreting unchanged ALERT status alone as unchanged magnitude. “UNAFFECTED” means this operational label, not numerically identical fits. Exact alternate residuals and scores remain visible.

A missing/unscored comparison is **NOT_ASSESSED**, never ROBUST. Market roster sensitivity is **NOT_APPLICABLE** to independently modeled institution codes; this does not assess institution portfolio changes. If no negative-sensitive observation exists in the institution/metric history available through T, excluding such inputs would remove nothing: label UNAFFECTED by structural inspection, explicitly not by a new counterfactual run. Otherwise the unsaved institutional negative-fit comparison remains NOT_ASSESSED. Saved Phase 3 alternative fits cover markets only; institution window/fit coverage therefore remains incomplete.

The 24-month **trend** sensitivity is distinct from the unchanged 12-month residual **detector** reference. A scored alternative ALERT must retain corroboration for full sensitivity points; unscored history is not a vanished alert. The complete-history fixed cohort is hindsight-selected and remains a sensitivity only.

## Classification and final selection

Apply these gates in order:

1. Raw-only controls or direct negative-sensitive observations: **REJECTED_FOR_DEMO**. This conservative presentation choice retains them for audit/research; it does not invalidate the original detector signal.
2. HIGH data-quality risk or severe scored sensitivity: **RESEARCH_ONLY**, irrespective of total.
3. At least 12/18, complete scored counterfactual coverage and sensitivity points=3: **FLAGSHIP**.
4. Other non-gated cases scoring at least 11/18: **SUPPORTING**.
5. Remaining cases: **RESEARCH_ONLY**.

Rank by descending total, statistical corroboration, quality confidence, narrative usefulness, absolute robust z, then stable candidate ID. Select at most two FLAGSHIP markets and two FLAGSHIP/SUPPORTING institutions with distinct codes. Do not fabricate evidence to meet a minimum. The four-case shortlist provides diversity rather than simply the four highest scores. SUPPORTING can have a larger total than FLAGSHIP while lacking required counterfactual evidence. All dimension values and nonselected cases are published.

## Timing and interpretation

Scoring uses only source flags/history available through T and backward persistence. The T+1…T+3 observations are post-signal validation context, never input to suitability or original signals. Case selection itself is retrospective exploration of the current snapshot and is not prospective validation. Charts show up to 24 preceding and six following report months where saved data exist; later follow-up is shaded and the corresponding simulated availability dates appear on the top axis.

ALERT means substantial departure from modeled historical expectation deserving investigation. It does not establish fraud, a disaster, insolvency, cause or continued claims growth. Materiality bands remain exploratory; claims_to_premiums_ratio is not a validated actuarial loss ratio. Current-vintage revisions, unverified exact releases, incomplete institution counterfactuals and hindsight fixed-cohort selection limit interpretation. External investigation questions remain unanswered for a later phase.

## Reproduction

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/generate_case_studies.py
```

Inputs default to `data/processed/cnbs/expected-behavior/`. Outputs default to `reports/case-studies/`. No analytical configuration or source output is modified. Provenance hashes identify the saved inputs and separate outputs.
