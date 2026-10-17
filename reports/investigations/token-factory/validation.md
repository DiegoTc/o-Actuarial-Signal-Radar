# AMD Token Factory / Evolus live validation — 2026-10-16

**AMD: VERIFIED · Evolus: VERIFIED · End-to-end: VERIFIED · Phase 4: COMPLETE.**

These statuses concern real hosted AMD Token Factory inference through the existing production Evolus workflow. No Developer Cloud GPU, self-hosted ROCm/vLLM runtime, payment method or paid subscription was provisioned. No cash cost was incurred.

## Model and API

- Selected: `DeepSeek-V4-Flash`, OpenAI-compatible Chat Completions.
- Base URL: `https://developer.amd.com.cn/radeon/api/v1`; Bearer authentication, secrets omitted.
- Actual shared gateway response model: `self-dploy/DeepSeek-V4-Flash`; the client accepts only the exact requested model or this observed catalog prefix.
- Minimal real JSON smoke: initial direct test HTTP 200 in 1.853 seconds; final client smoke PASS in 1.849 seconds, with expected status/provider JSON returned.
- Qwen3.8-27B was available and passed tiny JSON and native connection tests, but long investigation attempts were incomplete/too slow. They are excluded from verification.
- The console/manual and live API show Chat Completions support; `/v1/responses` is not served. JSON-object mode is followed by the unchanged full application response schema.
- The observed sponsored allowance is $1/day, shared team key, 20 requests/minute at the gateway. This is quota accounting, not a cash bill. No Token Factory expiration was displayed.

## Production path

Immutable saved package → six relevant indexed Evolus library documents → SHA-256 checks → native Evolus LlmCall → explicit `own/deepseek-v4-flash` → structured JSON → immutable snapshot/citation/causal-language/schema checks → HUMAN_REVIEW_REQUIRED → dashboard COMPLETED.

Existing workspace, library and workflow IDs are unchanged. Library: `ActuarialSignalRadarMemory1`. Workflow: `Actuarial Signal Investigation` (`573811ae-38c3-4b26-a61c-174a7ab3b07d`). No default model or automatic paid-model fallback is configured. Temperature 0, max_tokens 8192, reasoning_effort none.

The indexed document downloads were verified byte-for-byte against the registered curated excerpts, and registered references occur in the final model output. The library is also attached to the prepared agent. The production inline model does not independently demonstrate native semantic-search tool execution: `native_semantic_retrieval_verified=false`. No raw CNBS dataset was uploaded.

## Verified cases

| Case | Execution ID | Result | Original classifications | Human review |
|---|---|---|---|---|
| [market_claims_2025_09](market_claims_2025_09.es.md) | `40a0b4ae-b9c9-f111-bf5b-6045bd9ce552` | PASS / COMPLETED | ALERT → ALERT | REQUIRED |
| [market_ratio_2025_03](market_ratio_2025_03.es.md) | `e3414a08-bac9-f111-bf5b-6045bd9ce552` | PASS / COMPLETED | NORMAL → ALERT | REQUIRED |

Both responses preserve every required signal-snapshot value exactly, including both report and simulated availability dates. The September claims residual remains 42942866.19499999, robust z 11.015446264198951. The March ratio residual remains 0.10860263924809477, robust z 8.611067998372137; RAW NORMAL remains ADJUSTED ALERT. Statistical calculations, thresholds and classifications were not rerun or changed.

## Validation and failed attempts

Original model/provider outputs and execution IDs are retained in timestamped ignored audits and `.local/token-factory/`. Earlier Qwen long-reasoning runs, native agent tool-loop/response-envelope failures, direct diagnostic responses and polling 429 errors are not counted as successful end-to-end results. The successful reference uses native LlmCall. Resume with `--execution-id <id>` after a polling failure; do not resubmit automatically.

The first successful claims workflow response was initially flagged because the conservative lexical guard did not recognize “No se establece causa, fraude o insolvencia” as a negation. The guard now recognizes this Spanish reflexive form; regression tests still reject positive accusations and contrasting accusations after “pero”. The model output was retained unchanged and revalidated, not rewritten. Full JSON Schema, immutable values, LOW/MEDIUM hypothesis confidence, registered evidence references and human review remain required.

One direct comparison returned hypothesis evidence as prose instead of registered IDs and was correctly rejected. The native prompt now explicitly requires IDs for supporting_evidence too. No validator was relaxed to accept unknown references.

## Checks

- Backend: `docker compose run --rm app pytest` — **302 passed** (including all 281 previous tests).
- Frontend: Node 22 `npm test` — **19 passed**.
- TypeScript: `npm run typecheck` — PASS.
- Existing browser suite: `npx playwright test dashboard.spec.ts` — **9 passed**.
- Real saved-result browser checks: `RUN_LIVE_VALIDATION=1 npx playwright test live-investigation.spec.ts` — **2 passed**; these read existing real results and do not issue new model calls.
- `docker compose build` — app and frontend PASS; local services run with `docker compose up -d`.
- Protected before/after SHA-256 inventory: **140 files unchanged**; includes raw/processed datasets, Phase 2/3/3.5 outputs and analytical code/configuration/schemas/packages.
- Actual configured API-key scan: no key values found in shareable project files. `.env` remains ignored and mode 0600; tokens never enter browser JSON.

## Evidence and demo

- [Machine-readable verification](verification.json).
- [September claims Spanish report](market_claims_2025_09.es.md) and [JSON](market_claims_2025_09.es.json).
- [March ratio Spanish report](market_ratio_2025_03.es.md) and [JSON](market_ratio_2025_03.es.json).
- Private smoke/model/usage receipts, native execution traces, failed attempts and screenshots: `.local/token-factory/` (ignored).
- Open `http://localhost:3000/cases/market_claims_2025_09` or `http://localhost:3000/cases/market_ratio_2025_03`. Both show COMPLETED with the real Spanish investigation and HUMAN_REVIEW_REQUIRED. Saved results are explicitly identified; page reads make no new inference call.

## Limits

Verification covers these two real Spanish case investigations and the tested hosted service integration, not all possible inputs, English generation quality, native semantic retrieval, self-hosted GPU hardware, production monitoring or factual/causal validation of every sentence. Schema and lexical checks cannot establish narrative truth; a human must assess hypotheses and missing evidence. Current replay remains LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.

No analytical phase, cloud provisioning or billing work was performed. No secrets were committed and no Git push was made.

Final sponsored usage receipt: $0.02732124738395214 consumed from the $1 daily allowance, $0.9726787526160479 remaining. This is free allocation usage, not cash spent. The successful inline runs are Completed; the two earlier Qwen/AgentCall attempt IDs were also checked and are no longer Running. They remain excluded from the verified reference cases regardless of their terminal status.
