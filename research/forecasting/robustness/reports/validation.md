# V2 execution and preservation validation

Branch: `research/claims-forecast-2026-2027`. Parent commit: `39a67e645bc111b3f2bafefd62d1274a37513f77`. V2 remains local and uncommitted; no push, merge or deployment was performed.

## Protocol and execution record

- Primary protocol/configuration declaration: **2026-10-18T00:50:55.086638+00:00**.
- Primary execution began: **2026-10-18T00:53:48.975755+00:00** (October 17 in Honduras).
- Primary frozen bundle: [2026-10-18-v2](../results/2026-10-18-v2/manifest.json).
- Additional calibration-pool influence work has its own [post-primary exploratory protocol](interval-influence-protocol.md) and [separate manifest](../results/2026-10-18-v2-interval-audit/manifest.json). Its protocol hash was captured before its calculations. It was not represented as part of an untouched confirmation exercise.
- No v2 final forecast was selected or substituted for the v1 July-cutoff forecast.

## Tests and actual calculations

- **92 research tests passed** in 2.63 seconds: 38 unchanged v1 tests and 54 v2 tests. These cover every candidate's future-perturbation invariance, exact seven-month horizons, reporting/availability cutoffs, prior-year history, missing/negative amounts, harmonic support, known-line OLS extrapolation, deterministic predictions, whole-window interval-calibration purging, actual calibration/evaluation separation, formula/score checks and frozen-output tamper detection in disposable copies.
- **313 existing backend regression tests passed** in Docker in 23.51 seconds. Production requirements and tests were not changed.
- All 14 experimental point specifications plus seasonal naive completed the common 16-origin panel, with 112 errors per candidate. Primary fit-failure count: **0**. The separate legacy panel retains its own counts.
- **Two counterfactual influence fits** (median_24 at July 2021 with October 2019 or November 2020 masked) lacked sufficient prior-year seasonal innovations. They are recorded in `influence_failures.json`; no replacement was invented. Each altered diagnostic is compared with the matching baseline rows.
- Horizon-empirical intervals explicitly record unavailable early origins and lag-aware calibration fits. Matched comparisons use identical eligible target/origin rows, not selectively dropped failures.
- A second complete primary execution reproduced **all 20 CSV outputs byte-for-byte**, including predictions, calibration errors, metrics, interval summaries, influence diagnostics and stability tables. Configurations and failure/availability records also matched. Execution timestamps/provenance timestamps are intentionally different.
- A second supplementary execution reproduced **all three diagnostic CSV outputs byte-for-byte**.
- All six primary figures were visually inspected: trend windows, seasonal methods, origin stability, error/bias distributions, interval coverage/width/score and event influence. They use actual outputs and label dependence/diagnostic scope.

## Preservation and security

- All **390 pre-existing protected files** retained their captured SHA-256 hashes. This includes tracked v1 research/code/manifests, production source/configuration, existing analytical outputs and local original/processed data.
- V1 and primary v2 frozen integrity verification passed; supplementary artifact hashes and its link to the original manifests passed. Recorded source hashes still match their files. Existing v1 manifests were not edited.
- Only `research/forecasting/robustness/` was added. No production service dependency, dashboard, deployment, anomaly method, availability helper, Evolus workflow or AMD configuration changed.
- New public-file candidates were checked against locally configured credential values without printing those values, and checked for private-key blocks. No match was found. Relative Markdown links, file sizes and whitespace checks passed.
- No new raw download, model-service call, cloud resource, commit or push occurred. Runtime environments and independent reruns remain in the existing Git-ignored local research storage.

## Scientific limits retained

Current-vintage/report-cutoff timing is not strict historical point-in-time validation. Six disjoint target windows do not establish six independent experiments; all share training history. V2's historical comparisons are exploratory because v1 outcomes were already known. Empirical interval undercoverage and sensitivity to November 2020 are reported without weakening safeguards or recommending removal of that observation. See [scientific conclusions](conclusions.md) for exact metrics and defensible presentation claims.
