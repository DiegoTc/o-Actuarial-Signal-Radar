# February 2027 — evidence-led actuarial presentation package

This is a research outline and technical briefing, **not a polished deck**. Sources are the frozen V1/V2 studies, [accounting review](actuarial_interpretation.md), [timeline review](publication_timeline.md), and the [snapshot-pinned monitoring report](../results/2026-10-18-retained-oct03-r2/evaluation_report.md). Refresh outcomes only through a separately registered snapshot and a new evaluation, never by editing these artifacts.

| Section | Professional explanation | Technical material / evidence |
|---|---|---|
| 1. Research problem | Can a transparent historical reference help distinguish unexpected monetary insurance behavior? | Define the target as eligible reported monetary accounting increments, not accident counts. Separate detection, forecasting and causal explanation. |
| 2. Official data and limitations | Public market information is broad, but monthly and aggregated. | CNBS Primas y Siniestros; Automobile/Nacional; 103 training months; October 3 vintage. Unknown gross/net/paid/incurred mapping, actual release dates and revisions. |
| 3. Monthly reconstruction | We measure changes in the reported accounting balance. | January balance; exact same-key prior-month difference otherwise; preserve adjustments; missing/ambiguous prior blocks derivation. October 2019 partial coverage example. |
| 4. Original anomaly framework | An unusual deviation deserves investigation; it does not identify a cause. | Existing raw/expected/residual framework; robust-z reference and complementary evidence. Unchanged original methodology; no new detector introduced. |
| 5. Forecasting model development | Start with simple, auditable baselines for a short time series. | Seasonal naive, additive trend/seasonality, damped additive Holt–Winters, fixed SARIMA. Original model selection remains frozen. |
| 6. Selected model mathematics | A recent typical level plus the historical same-month pattern. | Prior-only trend innovations, additive seasonal median, fixed multi-step trend; see formula below. |
| 7. V1 historical evidence | Better historical performance is encouraging, not proof of future accuracy. | Confirmation n=14 from two July origins: original MAE 9.403M, RMSE 15.367M, WAPE 6.65%, 37.316% MAE reduction versus naive. Dependent errors and known-vintage caveats. |
| 8. V2 robustness | Parameter choices and the evaluation period matter. | Quarterly panel: original MAE 9.962M, median_6 9.348M, naive 16.603M; period reversal; no independent new confirmation or replacement of V1. |
| 9. Seven frozen forecasts | Publish a fixed reference before monitoring outcomes. | Use the [original exact CSV](../../results/2026-10-18-v1/seven_month_forecast.csv) and its intervals, copied byte-for-byte into monitoring. Do not rerun fitting for presentation. |
| 10. Available outcomes | Report what is genuinely in the chosen vintage, including missing months. | August 155.25833981000004M; September–February missing in the retained October 3 snapshot. A later evaluation must name its different vintage. |
| 11. Errors and uncertainty | One retrospective outcome cannot validate a seven-month forecast. | August overforecast 2.14448523999996M, 1.381236745558602%; inside both original intervals; n=1. At this October execution, simulated-lag sample n=0. Show actual-versus-frozen plot with six missing outcomes. |
| 12. Supported conclusions | The study is reproducible and exposes sensitivity and uncertainty. | Preserved bytes, hashes, prior-only fitting, fixed forecasts and explicit sample sizes. Robust median references remain competitive on this snapshot. |
| 13. Uncertainty and unresolved issues | Some interpretation cannot be recovered from a numeric series alone. | No real-time July claim; no causal/accident-frequency inference. Wide original intervals and undercoverage of the alternative; account mapping, revisions and coverage gaps. |
| 14. Future research | Better evidence is more valuable than another retrospective accuracy search. | Archive subsequent releases; obtain account/exposure definitions; dependence-aware evaluation; compare richer models only with suitable new data and a declared protocol. |

## Mathematical appendix

For monthly monetary amount `y_t`, the frozen reference has:

```text
tau_j = median(prior 12 calendar months; at least 9 usable observations)
d_j = y_j - tau_j
s_(m,T) = median(d_j for month m in eligible prior years, lookback <= 6 years,
                 at least 2 seasonal innovations)
yhat_(T+h|T) = median(y_(T-11), ..., y_T) + s_(month(T+h),T), h=1,...,7
```

The terminal level stays fixed across all seven simultaneous predictions; no subsequent actual updates the frozen path. Original uncertainty uses centered historical prequential residual blocks. Sampling the same marginal pool at each h does not propagate full parameter uncertainty. V2's horizon-specific empirical errors are an exploratory alternative, not a recalibration of the published intervals.

Score conventions: `error = forecast − actual`; MAE, RMSE and WAPE use only explicitly available outcomes. Coverage has a numerator and denominator, not a guarantee. Missing observations have no errors, not zero errors. Do not present the interval inclusion of a single August outcome as evidence of calibration.

## Presentation checklist

- Name the observation cutoff, original download date, actual execution date and chosen outcome vintage separately.
- Show all seven forecast months; label each missing actual explicitly.
- Keep receipt-based and simulated-lag sample sizes separate.
- State V2 is exploratory; no successor has independently replaced V1.
- Explain October 2019 partial coverage, negative adjustments and November 2020's uncertainty influence.
- Retain definitions as unresolved when evidence does not map `Saldo` precisely.
- Date every table/figure and preserve its result manifest.
- February 2027 outcome eligibility is May 1 under the existing assumption; a full evaluation may need a later addendum.

## Questions for official clarification — not sent

1. Which accounts, signs, reserve movements and reinsurance components define the base Siniestros `Saldo` extraction, by period?
2. Is the dataset year-to-date under a stable convention from 2018 onward? How are reversals/reclassifications represented?
3. What are the actual monthly datastore release dates, historical refresh logs and correction rules?
4. Are immutable historical extracts available, particularly what was available July 31 and October 3, 2026?
5. What is the approved continuity treatment of institution codes 0616/0618 around October 2019?
6. Can the December 2022 cross-publication claims discrepancy be reconciled by scope, correction or revision documentation?

Claims about portfolio growth, inflation, catastrophe, reinsurance or reporting changes require additional matched evidence. Monetary changes alone do not reveal accident frequency or severity.
