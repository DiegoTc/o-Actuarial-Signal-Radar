# Documentation index / Índice documental

[Project README](../README.md) · [README en español](../README.es.md) · [Public demo](https://actuarial-signal-radar.diegoturciostc.workers.dev)

Start with the judge's guide for the problem, statistical/AI responsibilities, two cases and real deployment limits. Technical documents below provide formulas, contracts and evidence without repeating them here.

Para una primera lectura, la guía para jueces explica el problema, las responsabilidades de estadística/IA, los casos y los límites reales. Los documentos técnicos contienen el detalle y la evidencia.

## Reading paths

| Audience / lector | Documents |
|---|---|
| Judges / jueces | [English guide](judges-guide.md) · [Guía en español](judges-guide.es.md) |
| Spanish-speaking analysts | [Concept guide](guia-conceptos-actuarial-signal-radar.es.md) · [Cómo leer resultados](como-leer-resultados.es.md) |
| Reproducibility | [Data foundation and source reference](data-foundation-reference.md) · [Complete pipeline](../README.md#run-the-complete-pipeline) |

## Statistical and actuarial methodology

| Document | What it answers |
|---|---|
| [CNBS semantics](../reports/data-profile/cnbs_semantics.md) · [Automobile semantics](../reports/data-profile/cnbs_automobile_semantics.md) | Why derive monthly increments from reported cumulative balances, and what accounting questions remain? |
| [Historical replay](historical-replay-methodology.md) · [Español](historical-replay-methodology.es.md) | Which data can enter an evaluation date? Why the conservative lag? Why is strict point-in-time unvalidated? |
| [Statistical baseline](statistical-baseline-methodology.md) · [Español](statistical-baseline-methodology.es.md) | Rolling statistics, standard/robust z, EWMA, CUSUM, thresholds, warm-up and quality rules |
| [Expected behavior](expected-behavior-methodology.md) · [Español](expected-behavior-methodology.es.md) | Prior-only trend/seasonality, expected values, residual detection, materiality and sensitivities |
| [Case-study selection](case-study-selection-methodology.md) | Explainable demo suitability, persistence, cohort and negative-adjustment review; not another anomaly model |
| [Investigation methodology](investigation-methodology.md) | Immutable handoff, evidence, output validation and human-review boundaries |

## Results and case evidence

| Document | Contents |
|---|---|
| [Statistical baseline summary](../reports/statistical-baseline/baseline_summary.md) | Saved Phase 2 results and evaluation coverage |
| [Expected-behavior summary](../reports/expected-behavior/expected_behavior_summary.md) · [Español](../reports/expected-behavior/expected_behavior_summary.es.md) | Saved Phase 3 results and limitations |
| [Raw vs adjusted](../reports/expected-behavior/raw_vs_adjusted_signals.md) · [Español](../reports/expected-behavior/raw_vs_adjusted_signals.es.md) | Which saved classifications change after adjustment? |
| [Materiality](../reports/expected-behavior/materiality_analysis.md) · [Cohort sensitivity](../reports/expected-behavior/cohort_sensitivity.md) · [Negative-adjustment sensitivity](../reports/expected-behavior/negative_adjustment_sensitivity.md) | Magnitude and robustness context |
| [Case index](../reports/case-studies/case_study_index.md) · [Español](../reports/case-studies/case_study_index.es.md) | FLAGSHIP and SUPPORTING selections, reports and charts |
| [Claims September 2025](../reports/case-studies/market_claims_2025_09.md) · [Español](../reports/case-studies/market_claims_2025_09.es.md) | Observed vs expected, economic magnitude, sensitivity and investigation questions |
| [Ratio March 2025](../reports/case-studies/market_ratio_2025_03.md) · [Español](../reports/case-studies/market_ratio_2025_03.es.md) | RAW NORMAL → ADJUSTED ALERT; no causal inference |

## Dashboard, services and deployment

| Document | Contents |
|---|---|
| [Dashboard runbook](dashboard-demo.md) | Local UI/API, artifact requirements, investigation states and tests |
| [Cloudflare compatibility](cloudflare-compatibility.md) | Historical Phase 6A experiment: OpenNext works; unchanged Python Workers migration was not recommended |
| [Cloudflare deployment](cloudflare-deployment.md) | Actual public URL, server-side gateway, secret bindings, latest production outcomes and limits |
| [Railway deployment](railway-deployment.md) | Python backend packaging, authentication, job polling, idle/restart behavior and earlier production validation |
| [Evolus setup](../evolus/README.md) | Workspace/library/workflow, API contracts, knowledge manifest and orchestration |
| [AMD integration](../amd/README.md) | Token Factory, actual model/API and evidence; earlier self-hosted ROCm/vLLM preparation is separately labeled |
| [Knowledge manifest](../evolus/knowledge/manifest.json) | Curated methodology/case inputs; no raw full datasets or secrets |

## Validation reports — read scope and date

| Evidence | Scope |
|---|---|
| [Phase 1](../reports/data-profile/phase1-validation.md) · [Replay readiness](../reports/data-profile/replay_readiness.md) | Foundation and historical-availability evidence |
| [Phase 2](../reports/statistical-baseline/phase2-validation.md) | Statistical baseline tests and preservation |
| [Phase 3 summary](../reports/expected-behavior/expected_behavior_summary.md) | Expected-behavior results, scenarios and limitations |
| [Phase 3.5](../reports/case-studies/phase35-validation.md) | Case-selection validation and preservation |
| [Phase 4 mock/application layer](../reports/investigations/phase4-validation.md) | Earlier implementation tests; not proof of AMD inference |
| [Evolus setup validation](../reports/investigations/evolus-setup/validation.md) | Workspace, context and real pre-model handoff |
| [Token Factory investigation verification](../reports/investigations/token-factory/validation.md) | Earlier successful real-model investigations and saved reports |
| [Dashboard Phase 5](../reports/dashboard/phase5-validation.md) · [UX Phase 5.1](../reports/dashboard/phase51-validation.md) · [Time views Phase 5.2](../reports/dashboard/phase52-validation.md) | UI contracts, explainability, exact 2020 unscored example and yearly views |
| [Latest public deployment acceptance](cloudflare-deployment.md#production-results-and-remaining-blocker) | Claims completed; latest ratio attempts did not pass. Full fresh public two-case acceptance remains PARTIAL. |
| [Final release validation](release-validation.md) | Final regression results, protected-file and secret/history checks for this release |

Earlier successful tests do not supersede a later failed public attempt. Mock, pre-AMD handoff, saved real reports and fresh public executions are distinct evidence categories. Runtime audits, secrets and local deployment receipts stay ignored; selected public validation reports remain in Git.

## Attribution and licensing

CNBS Honduras provides the source data. Evolus supplies orchestration/knowledge features, AMD Token Factory hosts the model workload, Cloudflare serves the frontend/gateway, and Railway serves Python. See their runbooks for official references and third-party terms. No repository LICENSE has been selected; no license is invented by this index.
