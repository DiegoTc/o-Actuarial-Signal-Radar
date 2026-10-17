# Phase 4 validation record

Validated locally on 2026-10-15 (America/Tegucigalpa); generation timestamps are UTC. The code/mock pipeline is implemented. **AMD: NOT CONFIGURED. Evolus: PARTIAL**, with no live deployment or API execution verified.

## Verified commands

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/build_investigation_package.py --case market_claims_2025_09
docker compose run --rm app python scripts/build_investigation_package.py --case market_ratio_2025_03
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider mock --language en
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider mock --language es
docker compose run --rm app python scripts/run_investigation.py --case market_ratio_2025_03 --provider mock --language en
docker compose run --rm app python scripts/run_investigation.py --case market_ratio_2025_03 --provider mock --language es
docker compose run --rm app python scripts/sync_evolus_knowledge.py
```

Docker build: passed. Full suite: **214 passed** (all 165 pre-existing tests plus 49 Phase 4 tests). Packages and all four mock investigations: exit 0, validation PASS, HUMAN_REVIEW_REQUIRED. Knowledge command: local plan only, seven verified documents, zero external requests. Dependencies remain pinned; Python 3.12.15 and pytest 8.4.2. No local GPU runtime is required.

## Test coverage

Offline fixtures cover schema/known FLAGSHIP extraction, exact saved values, package determinism/source preservation, checksum rejection, missing/unknown fields, availability/future-context guards, provider selection/missing configuration, explicit mock behavior, Spanish text with English fields, malformed/duplicate/fenced/non-finite JSON, immutable analytical fields, human review, LOW/MEDIUM hypothesis confidence, evidence references, causal-language checks, AMD request formatting/auth/timeouts/errors, provenance/audit, protected output paths, Evolus upload/start/poll/result contracts, failed runs and retained execution IDs. HTTP calls in tests are simulated; they do not establish live service behavior.

## Preservation

Before work, all existing files under data, analytical source, config, tests, scripts, reports and docs were checksummed, and Git status was captured. **168 existing files retained identical SHA-256 values**. Raw/processed/monthly CNBS data, analytical configuration, availability helper, models, existing tests and Phase 2/3/3.5 outputs are unchanged. New investigation packages are additive. Pre-existing Git changes were left intact.

Intentional infrastructure/documentation changes: README/README.es, .env.example, Dockerfile copies, Compose environment pass-through, and pinned JSON Schema dependencies. New analytical algorithms, source derivations and detection thresholds were not added.

Source and excerpt hashes are checked before package/context use. Local documentation links, example-package identity, latest report/audit provenance and English/Spanish immutable signal fields are checked. See [phase4-preservation.json](phase4-preservation.json) for the captured original file hashes and final checks.

## Real-service limitations

No actual AMD model was selected/configured or invoked; no GPU/ROCm/vLLM execution evidence exists. No Evolus workspace, indexed library, native enabled workflow or runtime retrieval was verified. The two target building blocks are Workflow and Knowledge Library; application REST adapters and a manual setup plan do not satisfy deployed-block verification by themselves.

Mock model: deterministic-placeholder-v1. Mock hypotheses are empty. No fixture is attributed to AMD/Evolus. Real model name is supplied only via AMD_VLLM_MODEL. Schema/lexical/citation checks are consistency filters and cannot establish narrative truth or cause. Every output requires human actuarial review. Replay remains LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.

Before a live demo: provision/verify AMD host and model, connect its endpoint, create event workspace/library and verify indexing, configure/enable workflow and exact result mapping, run both cases end to end, and retain model/retrieval/workflow/AMD-host evidence. No dashboard/frontend work was started.
