# Data quality interactions

Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Scope: Automobile / Nacional, premiums and claims separately; ratio is `claims_to_premiums_ratio`, not a validated actuarial loss ratio. Simulated availability uses the existing helper: first day of the third following calendar month. No historical event labels were used for tuning. Counts are method/window observation rows, not distinct economic incidents.

| Measure | Count |
|---|---|
| Eligible/pending source rows | 2266 / 22 |
| Eligible-source exclusion statuses | {'eligible': 2264, 'excluded_blocked': 2} |
| Negative source increments (retained by default) | 20 |
| Review-flagged source rows | 26 |
| Signals overlapping current/market negative flags | 108 |
| Signals with any current/history/state quality flag | 586 |

Blocked rows are preserved in the source audit and per-method institution outputs with explicit exclusion statuses and blank signals. Review flags and negative increments are retained; affected rolling histories and state are marked separately. Raw and Phase 1.5 outputs are never rewritten. Institution codes are independent; names are labels, not continuity evidence.

## Negative adjustment sensitivity

The following paired run changes only the negative-value policy to exclude. This is a disclosure, not calibration or a recommended deletion policy. It changes market coverage and can trigger insufficient history.

| Level | Policy | NORMAL | WATCH | ALERT | Not scored |
|---|---|---|---|---|---|
| market | retain (default) | 2113 | 175 | 133 | 360 |
| market | exclude (sensitivity only) | 2107 | 158 | 156 | 360 |
| institution | retain (default) | 15229 | 1195 | 1084 | 2886 |
| institution | exclude (sensitivity only) | 13837 | 1120 | 988 | 4449 |

## Market composition and exclusions

Market totals use eligible valid observed contributors, not a hindsight complete-cohort filter. Excluded counts include current blocked/invalid reporters and prior-period reporters absent now. Unknown nonreporters cannot be counted. No missing institution is assigned zero.

| Resource | Report date | Availability | Contributors | Excluded | Blocked | Entered codes | Exited codes | Review contributors |
|---|---|---|---|---|---|---|---|---|
| primas | 2019-10-31 | 2020-01-01 | 10 | 2 | 1 | 0618 | 0616 | 0 |
| siniestros | 2019-10-31 | 2020-01-01 | 10 | 2 | 1 | 0618 | 0616 | 1 |

The ratio requires both totals and a strictly positive premium denominator. Premium and claims contributor metadata are recorded separately; differing cohorts receive `ratio_cohort_mismatch`. All-blocked totals and invalid ratios remain missing. Flags are not causes or ground-truth anomaly labels.

