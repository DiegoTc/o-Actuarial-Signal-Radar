# Evolus event-workspace validation — 2026-10-16

**CONFIGURED for pre-AMD handoff. Full investigation with AMD: NOT VERIFIED.**

The free Developer Event workspace **Actuarial Signal Radar** is active until **15 November 2026**. Activation supplied 50,000 platform credits with no card/payment details. The portal displayed 50K before document indexing; an exact post-indexing balance has not been independently captured. Included credits pay for library embeddings. No paid subscription, external model, AMD resource or payment method was configured.

## Real resources

| Resource | Identifier |
|---|---|
| Workspace / X-Application-Id | `4eaccc3d-45ac-4f36-883f-8dbd307c471c` |
| ActuarialSignalRadarMemory1 | `d2aca892-20c9-f111-bf5b-000d3aae6dc8` |
| Actuarial Signal Investigation | `573811ae-38c3-4b26-a61c-174a7ab3b07d` |

The exposed default application key was revoked. Its replacement is present only in ignored local `.env`, mode 0600. A temporary personal key used for library discovery was revoked immediately afterwards. No personal key is retained. Authentication succeeds with `X-ApiKey` and `X-Application-Id` on the workflow and known-library routes. The initial 401 from `GET /memories` is explained by the official OpenAPI contract: that enumeration endpoint accepts only user authentication.

## Knowledge verification

The existing library was reused. All seven curated excerpts in the unchanged knowledge manifest are present, indexed and verified by downloading their original contents and comparing SHA-256:

- `cnbs_semantics.md`
- `replay.md`
- `statistical.md`
- `expected_behavior.md`
- `case_selection.md`
- `market_claims_2025_09.md`
- `market_ratio_2025_03.md`

The first was uploaded through the UI; the resumable API sync recognized it rather than duplicating it. Other uploads used Simple indexing with no model-generated augmentation/questions. The library uses the platform embedding engine `openai/text-embedding-3-small`; this is not an AMD investigation model. Native document IDs, excerpt hashes, indexing states and chunk counts are in [knowledge_uploads.json](knowledge_uploads.json).

Each test downloads six relevant documents: five common methodology excerpts plus its own case. This verifies actual library/API content access. It does **not** verify semantic search or an agent invoking the library. Those require the future native agent/model configuration.

## Real API executions

Endpoint: `POST https://api.evolus.ai/api/v1/workflows/{workflowId}/execute`, multipart `input` plus flat `parameters={"language":"es"}`. Poll: `GET /workflows/{workflowId}/executions/{executionId}` under the same base URL. The confirmed native response path is `/output`, containing a JSON string.

| Case | Native execution ID | Result |
|---|---|---|
| `market_claims_2025_09` | `e3693f89-75c9-f111-bf5b-6045bd9ce552` | PASS_PRE_AMD_HANDOFF_ONLY |
| `market_ratio_2025_03` | `ff87fda4-75c9-f111-bf5b-6045bd9ce552` | PASS_PRE_AMD_HANDOFF_ONLY |

Both native runs completed seven steps. Both preserved the full original canonical signal JSON string and semantically equal parsed values, required `human_review_required=true`, returned `HUMAN_REVIEW_REQUIRED` and `PENDING_AMD_MODEL`, retained empty hypotheses, and reported `model_execution={"provider":"NOT_CONFIGURED","model":null,"amd_verified":false}`. They generated no model investigation, cause attribution, new signal or detector result.

Two earlier development attempts exposed transport comparison issues: JavaScript spells numeric `0.0` as `0`, and property order differs between canonical and ordinary JSON. One completed remotely but failed the local byte comparison; another failed remote schema-step comparison. They made no model calls and remain in native execution history. The corrected design preserves the original signal JSON string byte-for-byte and independently checks parsed values. Both corrected cases pass; source packages were never rewritten. The native workflow export and versioned definition snapshots are retained here.

The workflow is enabled, but every model operation is replaced by an explicit deterministic pending gate. The production investigation parser intentionally rejects this pending contract. The application does not invent AMD environment settings to run a fake investigation.

## Local checks

- `docker compose build`: PASS.
- `docker compose run --rm app pytest`: **260 passed**, including all previous 243 and 17 new setup tests.
- `python3 scripts/check_evolus_workflow_scripts.py`: **28 offline JavaScript assertions passed**, including both FLAGSHIP chains, missing/invalid fields, changed source values and forbidden live mode.
- SHA-256 preservation: **131 existing data/configuration/statistical/expected-behavior/preprocessing/case-study files unchanged**.
- Secret scan: replacement application key absent from checked source, tests, documentation, reports, schemas and example configuration. `.env` is ignored and mode 0600.

Offline fixtures are labeled and do not count as service execution evidence. The real native execution JSON files, including UTC request/completion times, are separate from those fixtures. No detection tests or analytical expectations were changed.

## Remaining work

Register and verify the real AMD/vLLM model later; create/configure its native Evolus agent and attach the library; replace the pending gate, adapt the production handoff and enforce the existing investigation response schema/citation/causal-language checks. Do not omit a model on an AI block, because the platform then selects its default. Preserve human review and never let the LLM set NORMAL/WATCH/ALERT.

Verify actual native retrieval and model traces, run both real investigations through the existing production CLI, and capture correlated AMD GPU evidence before declaring **VERIFIED**. Connecting a URL alone does not complete those steps. No AMD provisioning or inference was performed during this task.
