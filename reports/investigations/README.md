# Phase 4 investigation outputs

These are **MOCK integration fixtures**, not results from AMD inference or an Evolus workflow. No causal hypothesis was generated. Every output is HUMAN_REVIEW_REQUIRED; PASS means structural/consistency checks passed, not human approval.

| Case | English | Español | Structured JSON |
|---|---|---|---|
| Market claims, report 2025-09-30; availability 2025-12-01 | [Report](market_claims_2025_09.md) | [Informe](market_claims_2025_09.es.md) | [en](market_claims_2025_09.json), [es](market_claims_2025_09.es.json) |
| Market ratio, report 2025-03-31; availability 2025-06-01 | [Report](market_ratio_2025_03.md) | [Informe](market_ratio_2025_03.es.md) | [en](market_ratio_2025_03.json), [es](market_ratio_2025_03.es.json) |

Versionable signal-package examples: [claims](../../evolus/examples/market_claims_2025_09.json), [ratio](../../evolus/examples/market_ratio_2025_03.json). Generated handoffs are stored separately in data/processed/investigations/.

Each latest JSON points to its timestamped audit. Original model/fixture output and request context are retained for every attempt; current audit records also include the complete provenance block. Earlier development fixture audits remain retained. A successful schema check does not establish truth, semantic support or AMD hardware identity.

Validation: [phase4-validation.md](phase4-validation.md). Setup and remaining live-demo actions: [AMD](../../amd/README.md), [Evolus](../../evolus/README.md). Scientific and safety boundaries: [investigation methodology](../../docs/investigation-methodology.md).

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**. Detect first; investigate second; humans decide.
