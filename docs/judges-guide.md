# Actuarial Signal Radar — guide for judges

[Español](judges-guide.es.md) · [Technical README](../README.md)

## The problem and intended user

Insurance analysts need to distinguish ordinary growth, recurring seasonal behavior and unusual changes in premiums or claims. Aggregate reports can make changes easier to notice only once they are large. Actuarial Signal Radar explores whether interpretable historical signals can help an actuary decide what deserves investigation.

This is research into retrospective early-warning signals. It has not demonstrated prospective forecasting performance or proved that it would have warned earlier than a real historical reporting process.

## The project in one minute

**We detect first. AI investigates second. Humans decide.**

1. Use official CNBS Honduras premiums and claims data for Automobile / National currency.
2. Read the existing guarded monthly accounting increments; preserve negative adjustments and quality flags.
3. Estimate expected trend and month-of-year seasonality using only prior available observations.
4. Compare observed with expected. The primary detector is a 12-month residual robust z-score; complementary statistics and sensitivity evidence remain visible.
5. Assess economic magnitude separately from statistical unusualness, then select documented case studies.
6. Hand an immutable signal package and curated methodology/context to Evolus and an AMD-hosted model for investigation, not detection.
7. Require human review of every generated investigation.

## Why statistics for detection?

The main time series have approximately 100 monthly aggregate observations, not millions of individual claims. The current snapshot spans 104 reporting dates; the saved evaluation admits 103 under its availability cutoff. A complex detector could overfit this small temporal sample.

An interpretable statistical baseline is deliberate: signals are reproducible for the same data/configuration, numerical reasons are inspectable, and accounting-quality limitations stay visible. No ML detector is implemented. Richer claim/policy-level data could justify benchmarking ML against this baseline; greater complexity would not automatically be better.

The residual is **observed − expected**. A robust z-score measures unusualness, not probability. Exploratory materiality bands assess magnitude; they are not regulatory, capital or budget thresholds. `claims_to_premiums_ratio` is not a validated actuarial loss ratio.

## Where AI, AMD and Evolus enter

| Component | Responsibility |
|---|---|
| Statistical engine | Expected values, residuals, scores and NORMAL / WATCH / ALERT; independent of the LLM |
| Evolus Workflow | Orchestrates the investigation and structured-response checks |
| Evolus Knowledge Library | Supplies curated CNBS semantics, methodology and case evidence; six indexed documents are retrieved and checksum-verified per case |
| AMD Token Factory | Hosts the real `DeepSeek-V4-Flash` inference workload used for investigation |
| Human actuary | Reviews context, evaluates hypotheses and makes decisions |

Native semantic-search execution is not independently verified. Do not equate verified indexed document retrieval with a separately validated semantic-search pipeline.

AMD is used through **Token Factory**, not a self-provisioned GPU Droplet. AMD Developer Cloud credits are not required for this integration. This is not verification of a self-hosted ROCm/vLLM server.

The model summarizes evidence, proposes explicitly unestablished hypotheses, identifies missing information and recommends checks. It cannot change the detector's signal values or classifications. Its output must satisfy schema, immutable-snapshot, evidence-reference, causal-language and human-review checks. Rejected output is not silently rewritten to force acceptance.

## Public demo and architecture

**[Open the dashboard](https://actuarial-signal-radar.diegoturciostc.workers.dev)** — Spanish default, English switch available.

```text
Browser → Cloudflare Next.js/OpenNext + server-side gateway
        → Railway Python API reading saved analytical artifacts
        → Evolus Workflow + Knowledge Library
        → AMD Token Factory / DeepSeek-V4-Flash
        → structured-response validation → human review
```

The browser never receives the backend token or provider keys. Live inference requires configured service credentials; a GitHub clone alone does not include them. The public API transports saved values rather than recalculating statistics.

## Two cases to inspect

Rounded display values below come from the local immutable signal packages (`data/processed/investigations/`, ignored by Git). The linked case reports document the case evidence.

| Case | Report period | Simulated availability | Observed | Expected | Difference | Residual robust z | Raw → adjusted |
|---|---|---|---:|---:|---:|---:|---|
| [Market claims](../reports/case-studies/market_claims_2025_09.md) | 2025-09-30 | 2025-12-01 | L185.38m | L142.43m | +L42.94m | 11.02 | ALERT → ALERT |
| [Claims-to-premiums ratio](../reports/case-studies/market_ratio_2025_03.md) | 2025-03-31 | 2025-06-01 | 63.91% | 53.05% | +10.86 pp | 8.61 | NORMAL → ALERT |

Claims materiality is HIGH; ratio materiality is MEDIUM, both exploratory. The second case illustrates why adjustment matters: the raw detector classified NORMAL while the expected-behavior detector classified ALERT. This does not establish why the deviation occurred.

## What has actually been verified?

The latest recorded Cloudflare validation is separate from earlier successful local/Railway integrations.

| Scope | Evidence/status |
|---|---|
| Saved statistical pipeline and case selection | Implemented and documented; source artifacts preserved |
| Public frontend, gateway, year/compare views, languages and mobile | DEPLOYED / VERIFIED |
| Earlier local/Railway Evolus + AMD runs | Both FLAGSHIP cases completed; [historical validation](../reports/investigations/token-factory/validation.md) |
| Fresh public claims investigation | COMPLETED in 154.224 s; DeepSeek-V4-Flash, six knowledge documents, zero validation issues and human review required |
| Fresh public ratio investigation | NOT VERIFIED: first response produced VALIDATION_WARNING; one reviewed retry failed structured-response validation |
| Full fresh public two-case acceptance | PARTIALLY VERIFIED; not claimed complete |

The ratio warning flagged an exploratory question containing “se debe a”. The reviewed retry failed the Evolus step `Validate structured AMD response` with `Missing model execution envelope`. No workflow/model/validator was changed to make the test pass. [Deployment details and limitations](cloudflare-deployment.md) record the outcomes; full runtime traces remain local and ignored because they are operational audit material.

## Suggested judge walkthrough

1. Open the overview and read the five-step explanation.
2. Compare observed and expected market claims; inspect the September 2025 case and its economic magnitude.
3. Open March 2025 to compare RAW NORMAL with ADJUSTED ALERT.
4. Review the Statistics → AI → Human boundary and investigation status. A live run may take 1–3 minutes or fail validation; do not treat a warning as completed findings.
5. Use the methodology links below to audit the assumptions and saved values.

Opening a page does not start a model call. An explicit Investigate action can consume event model allowance. When a saved result is shown, it is labeled as a saved real execution, not a new inference. Production runtime state is transient: Railway sleeping/restarting can reset jobs and remove displayed completion state. Do not assume the page will retain a past live result indefinitely.

## Limits that matter

- **LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.** The conservative calendar lag makes a January month-end eligible on April 1. It is a modeling assumption, not a confirmed CNBS publication schedule. Current historical figures may contain revisions; release dates/vintages were not reconstructed.
- CNBS data are monthly accounting aggregates. The exact treatment of paid/incurred claims, reserves and reinsurance is not fully resolved. A monthly increment need not be an individual claim payment or an occurrence-month loss.
- Trend/seasonality models need warm-up. An unscored spike is not NORMAL. Missing months are not silently zero-filled, and institution-code continuity is not inferred from names.
- Alerts are investigation signals, not confirmed incidents, causal findings, fraud determinations, insolvency diagnoses or disaster predictions. Materiality is exploratory.
- Live model responses can fail strict validation, as the ratio test demonstrates. Human review is mandatory even for accepted responses.
- This supervised hackathon demo lacks durable investigation storage and a presenter-authentication gate. Same-origin POST checks are not general bot protection.
- No paid-plan upgrade was performed. Cloudflare subscription reading returned OAuth 403, so independent Workers Free billing-tier confirmation is not established; hosted CPU headroom should not be inferred from build success.

## Reproduce and audit

With the required local artifacts already generated:

```sh
docker compose up --build
# Dashboard: http://localhost:3000
docker compose run --rm app pytest
```

`data/raw/` and `data/processed/` are Git-ignored: a fresh clone does not automatically receive the deployed artifacts. The [technical pipeline instructions](../README.md#run-the-complete-pipeline) describe generating them from CNBS; a later download may differ from the deployed snapshot. The public dashboard is the recommended judge walkthrough without local setup.

The analytical views read local artifacts. Real investigations additionally require the documented server-side configuration; credentials are never supplied by the repository. See [.env.example](../.env.example), [AMD](../amd/README.md) and [Evolus](../evolus/README.md). Do not rerun ingestion/backtests merely to view the demo.

Most recent recorded checks: **313 backend tests, 25 frontend tests, 16 local browser tests, eight gateway tests**, plus TypeScript and production OpenNext build. These tests do not override the unresolved fresh public ratio failure.

- [CNBS semantics](../reports/data-profile/cnbs_semantics.md)
- [Historical replay methodology](historical-replay-methodology.md)
- [Expected behavior methodology](expected-behavior-methodology.md)
- [Case selection methodology](case-study-selection-methodology.md)
- [Case study index](../reports/case-studies/case_study_index.md)
- [Railway deployment](railway-deployment.md) and [Cloudflare deployment](cloudflare-deployment.md)
