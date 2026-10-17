# Actuarial Signal Investigation — Evolus integration

Current live integration: **VERIFIED end-to-end for both FLAGSHIP cases**. The existing Developer Event workspace, library and workflow IDs are unchanged. A native **Your models → OpenAI-compatible** connection now points to AMD Token Factory and has passed Evolus's answer/tool/stream checks. The current workflow calls the explicit own model through a native inline LlmCall block; it no longer stops at the pre-AMD gate.

## Token Factory workflow

```text
Dashboard/app → immutable FLAGSHIP package
  → indexed Evolus library downloads, SHA-256 verification
  → Evolus Workflow: signal schema + registered-context checks
  → LlmCall: own/deepseek-v4-flash → AMD Token Factory
  → structured JSON + immutable snapshot checks
  → application full schema/citation/causality validation
  → HUMAN_REVIEW_REQUIRED → dashboard COMPLETED (only after PASS)
```

The connection is `AMD Token Factory — Actuarial Signal Radar`, base URL `https://developer.amd.com.cn/radeon/api/v1`, model ID `DeepSeek-V4-Flash`. The native agent is `Actuarial Signal Investigator — AMD Token Factory`, ID `42601a7a-93ac-4631-a7bf-c97c3ebdb478`; it is linked to `ActuarialSignalRadarMemory1`. The normalized Evolus model key is `own/deepseek-v4-flash`. Authentication is stored in the native secure connection, never in workflow scripts or execution inputs. The workspace fallback policy is **Stop**; no automatic switch to Evolus's paid model routing is enabled. No billing changes were made.

Selected DeepSeek agent parameters: `temperature=0`, `max_tokens=8192`, `reasoning_effort=none`; no model fallback or external web search. AMD documents that omitting reasoning effort makes Qwen default to `xhigh`. The first long-reasoning attempt exhausted 8192 reasoning tokens without a final answer; that attempt is retained as incomplete, never converted to a valid investigation.

The existing seven steps are now:

1. Validate the original signal schema, language, canonical signal text and live mode.
2. Check the existing library ID, six case-relevant indexed document IDs and curated excerpt hashes.
3. Call the explicit AMD Token Factory own-model connection with the native LlmCall block; no default model or agent tool loop.
4. Parse and check the original model JSON, required schema fields and exact signal snapshot.
5. Compare the original immutable signal and canonical text with the returned envelope.
6. Require human actuarial review.
7. Return through the native Output block.

The application applies the unchanged full JSON Schema, registered evidence references, copied values and conservative causal-language validation. It preserves the original execution, does not rewrite failed model text, and returns VALIDATION_WARNING/ERROR rather than invented findings. Hypotheses remain **HYPOTHESIS — NOT ESTABLISHED**, confidence LOW/MEDIUM only. The LLM cannot decide or override NORMAL/WATCH/ALERT.

The application downloads the six relevant indexed library documents, verifies their content hashes and sends them as model context. The same library is also attached to the prepared agent, but the current production model step uses LlmCall with the verified documents supplied in context. Native AgentCall attempts entered a long tool loop and were not treated as verified results. This verifies **retrieval of registered library evidence**, but attachment or output citations alone do not independently prove native semantic-search tool execution. Keep `native_agent_retrieval_verified=false` unless a retrieval trace proves otherwise. Do not upload raw CNBS datasets.

Invocation remains `POST /api/v1/workflows/{workflowId}/execute`, multipart `input` plus `parameters={"language":"es"}`; poll `GET /api/v1/workflows/{workflowId}/executions/{executionId}`. Headers are `X-ApiKey` and `X-Application-Id`. Input mode is `AMD_TOKEN_FACTORY_INVESTIGATION`; the signal schema and analytical values are unchanged. Completed envelopes contain `investigation`, unchanged `signal_package`, `knowledge_citations`, `model_execution={"provider":"amd_token_factory","model":"DeepSeek-V4-Flash"}` and `human_review_required=true`.

Required local variables: existing `EVOLUS_BASE_URL`, `EVOLUS_APPLICATION_ID`, `EVOLUS_API_KEY`, `EVOLUS_WORKFLOW_ID`, `EVOLUS_LIBRARY_ID`, `EVOLUS_RESULT_POINTER=/output`; `INVESTIGATION_PROVIDER=amd_token_factory`, `AMD_TOKEN_FACTORY_BASE_URL`, `AMD_TOKEN_FACTORY_MODEL`, and the private `AMD_TOKEN_FACTORY_API_KEY`. The latter is needed for direct smoke tests; Evolus keeps its own secure copy for workflow inference. Compose sends secrets only to Python, never the browser.

Use the existing dashboard **Investigate signal** action or:

```sh
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
docker compose run --rm app python scripts/run_investigation.py --case market_ratio_2025_03 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
```

Deployment code: [token_factory_workflow.py](../actuarial-engine/investigation/token_factory_workflow.py). The explicit `configure_token_factory_workflow.py` command upgrades only the known project workflow and retains an ignored local backup. Creating/linking a native model or assigning a library may require the signed-in user UI; the application key cannot perform every developer operation. Do not create duplicate workspaces/libraries or export secrets to work around permissions.

Workflow + Knowledge Library + native own-model connection are meaningful building blocks. Token Factory is the shared AMD service, not a self-hosted vLLM claim. AMD Developer Cloud credits and GPU droplets are not needed for this path. Current replay remains **LAGGED RETROSPECTIVE BACKTEST**, strict point-in-time **NOT VALIDATED**.

## Historical pre-AMD setup record

The sections below retain the earlier setup procedure and pre-AMD evidence. Statements about PENDING_AMD_MODEL/NOT CONFIGURED describe that earlier workflow version, not the current live configuration. Original setup reports and immutable analytical packages are preserved.

## Live workspace and evidence

| Setting | Verified value |
|---|---|
| Workspace | Actuarial Signal Radar |
| Workspace/application ID | `4eaccc3d-45ac-4f36-883f-8dbd307c471c` |
| REST base | `https://api.evolus.ai/api/v1` |
| Plan | Developer Event, free; no payment details added |
| Expiration | 15 November 2026; activation UI 16:59, conditions 23:59 Italian time |
| Credits | 50,000 at activation; portal showed 50K before indexing. Indexing uses included credits; no exact post-indexing balance is asserted. |
| Library | ActuarialSignalRadarMemory1 |
| Library ID | `d2aca892-20c9-f111-bf5b-000d3aae6dc8` |
| Workflow | Actuarial Signal Investigation |
| Workflow ID | `573811ae-38c3-4b26-a61c-174a7ab3b07d` |

The exposed default key was revoked. The replacement is in the ignored local `.env`, mode 0600, and is never a workflow parameter or model input. A temporary personal discovery key was revoked after identifying the existing library. No secret is stored in this document or [deployment metadata](deployment.json).

Seven curated manifest excerpts are indexed: CNBS semantics, replay, statistical baseline, expected behavior, case selection, September claims and March ratio. Every remote original download matched its excerpt SHA-256. The existing library was reused; no duplicate library or raw dataset was uploaded. The embedding engine is `openai/text-embedding-3-small`, a platform indexing service, not AMD model inference.

Native exports, upload/document IDs and execution evidence are in [evolus-setup](../reports/investigations/evolus-setup/). Read [setup validation](../reports/investigations/evolus-setup/validation.md) for exact scope and limitations.

We detect first. AI investigates second. Humans decide.

## Architecture and building blocks

```text
Saved validated signal → checksummed investigation package
  → Evolus Workflow: Actuarial Signal Investigation
  → Knowledge Library: curated methods + relevant case evidence
  → Evolus agent using team open model on AMD/vLLM
  → structured response + citations + execution metadata
  → application schema / immutable-signal / language checks
  → HUMAN_REVIEW_REQUIRED → actuary
```

The Workflow and Knowledge Library are deployed. In the current pre-AMD path, the application reads the relevant indexed documents through the library API, verifies their bytes, and supplies six case-relevant excerpts to the workflow. This is real document access, **not verified native agent semantic retrieval**. The future agent performs the AMD model call within the workflow. This layer cannot change NORMAL/WATCH/ALERT or the analytical inputs. Local mock/direct-AMD execution alone does not imply Evolus execution.

The [workflow plan](workflow/actuarial_signal_investigation.json) remains the future investigation contract, **not a vendor-native import file**. The actual [native pre-AMD export](../reports/investigations/evolus-setup/native_workflow.json) is separately retained. [Canonical schemas](schemas/README.md) are shared rather than duplicated. The [knowledge manifest](knowledge/manifest.json) is the original content contract; its historical deployment label is superseded by [deployment metadata](deployment.json), without changing manifest/source checksums.

## Current seven-step workflow

1. Validate every signal field against the existing `investigation_signal.schema.json` rules and require the declared language and pre-AMD mode.
2. Validate the case-relevant library context IDs, registered excerpt hashes and library ID. The application already downloaded and checked the actual content.
3. Stop at an explicit model gate: **NOT AMD VERIFIED**. No AgentCall, LlmCall, default model or external HTTP block exists in this workflow version.
4. Build a structured pending response with the unchanged signal, empty hypotheses and `model_execution.provider=NOT_CONFIGURED`.
5. Compare the result with the original signal and original JSON text.
6. Require `human_review_required=true` and `HUMAN_REVIEW_REQUIRED`.
7. Return the result using a native Output block.

All six processing blocks are deterministic JavaScript; the vendor catalog documents zero AI calls and zero credits for Script blocks. The library indexing step uses the event's included credits. The test runner reuses `EvolusClient.execute_raw()` for queueing/polling, with no retries or AMD settings. It does not call the production `--provider amd_vllm` CLI with invented credentials.

The multipart `input` is a JSON envelope containing `signal_package`, `signal_package_json`, `language`, `validation_mode=PRE_AMD_HANDOFF_ONLY`, `library_id` and `knowledge_context`. All requested analytical fields are inside the unchanged `signal_package`. The flat execution parameter is `language` (`es` or `en`). JSON runtimes can serialize `0.0` as `0`; the original canonical JSON string is preserved exactly alongside semantically equal parsed values. Original packages are not rewritten.

The pending response contains `status`, `investigation_status`, `validation_mode`, `signal_id`, `signal_package`, `signal_package_json`, `language`, `knowledge_access`, `model_execution`, empty `possible_hypotheses`, `limitations`, and `human_review_required=true`. It is intentionally **not** a completed `investigation_response.schema.json` result; the production parser rejects it as an investigation.

## Implemented in code

- Build/validate immutable selected-case packages from saved Phase 3/3.5 outputs.
- Prepare local, bounded, checksummed knowledge excerpts. Exclude Persistence/future-follow-up sections from case excerpts.
- Upload those excerpts to a configured library; list documents for indexing status.
- Start a workflow, retain its execution ID, poll Pending/Running until Completed/Failed, and extract the result using an explicit JSON Pointer.
- Validate JSON schema, copied analytical fields, evidence IDs, reported model/citations, causal wording and human review. Preserve original output and provider response in an audit.
- Render English/Spanish investigation drafts and return nonzero for flagged/provider-error responses. No automatic closure or actuarial decision is implemented.

REST request shapes follow the [official Evolus developer guide](https://evolus.ai/en/developers), checked 2026-10-15. Its workspace reference remains authoritative for full response shapes and permissions. These are REST integrations, not the separate OpenAI-compatible Evolus chat endpoint. No unofficial SDK or guessed endpoint is used.

## Remaining AMD-dependent workspace configuration

1. Workspace and API key rotation are complete. Keep the replacement key private; do not reuse the exposed default.
2. The existing Knowledge Library and seven indexed excerpts are ready. Keep the receipt mapping from native document IDs to manifest IDs/excerpt hashes. Actual agent retrieval still requires the model-dependent steps below.
3. Register the team's real AMD/vLLM endpoint, exact model and key. Test it and select it for the investigation agent. The model must support the needed structured output/tool calling.
4. Attach the Knowledge Library to that agent. Use the system instructions in `investigation/prompts.py`, and require retrieval of relevant methodology/case chunks with their manifest IDs and excerpt hashes. Preserve retrieval traces; a model merely echoing citation IDs is not proof that retrieval occurred.
5. Upgrade the existing **Actuarial Signal Investigation** from its deliberate pending gate to the actual agent/model path; do not create a duplicate or simply label the pending response as AMD. Update its input mapping for the existing production handoff and enforce the production response schema/immutable snapshot. Keep human review on every branch. The platform documents that omitting an agent/LLM model chooses its default, so no implicit-model agent was created as a placeholder.
6. The native execution result is confirmed at `/output`, as a JSON string. Configure the final result envelope below, then validate the production parser against an actual completed AMD-backed run. Retain the updated export and version.
7. Run the application through Evolus. Retain execution, retrieval, model and AMD-host traces. Verify that no default hosted model silently replaced the team's AMD model. Compare report numbers with the source package before presenting a live demo.

The remaining model/agent binding is a real limitation: changing the endpoint URL alone does not convert the current deterministic workflow into an AI investigation. No causal explanation, default-model fallback or AMD verification is claimed.

## Environment and API flow

```dotenv
EVOLUS_BASE_URL=https://api.evolus.ai/api/v1
EVOLUS_APPLICATION_ID=your-space-id
EVOLUS_API_KEY=your-local-secret
EVOLUS_WORKFLOW_ID=your-enabled-workflow-id
EVOLUS_LIBRARY_ID=your-library-id
EVOLUS_RESULT_POINTER=
EVOLUS_POLL_INTERVAL_SECONDS=2
EVOLUS_MAXIMUM_POLLS=30
```

`EVOLUS_API_URL` aliases `EVOLUS_BASE_URL`; `EVOLUS_WORKSPACE_ID` aliases `EVOLUS_APPLICATION_ID`. Use matching values if both names are set. `.env` already contains the real non-secret IDs and private replacement key; `.env.example` contains placeholders only. Do not inspect/print the resolved Compose configuration with secrets loaded.

Also configure AMD_VLLM_BASE_URL, AMD_VLLM_MODEL and AMD_VLLM_API_KEY as in [AMD deployment](../amd/README.md), with INVESTIGATION_PROVIDER=amd_vllm. A local `.env` is read by Compose; host Python needs exported variables.

The client uses application-key REST authentication. The published workflow start is multipart, queued; the client polls its execution resource. Library uploads are multipart Markdown with language=en, followed by indexing checks. See the official developer guide for endpoints and header definitions. Secrets are HTTP headers, never run parameters or model context.

The workflow must return this **application-defined** result object at the configured pointer:

```json
{
  "investigation": "An object conforming to investigation_response.schema.json",
  "knowledge_citations": [
    {"id": "knowledge:replay", "sha256": "the actual curated excerpt SHA-256"}
  ],
  "model_execution": {"provider": "amd_vllm", "model": "the exact configured model"}
}
```

`investigation` must be a real JSON object (or a string containing that object), not the illustrative sentence above. Require relevant citations, not just a token citation. The application checks membership/hashes and model metadata; these are consistency checks, not proof of semantic support, native retrieval, or AMD hardware. Keep the native traces for those claims.

```sh
# Local inspection only; makes no external requests.
docker compose run --rm app python scripts/sync_evolus_knowledge.py

# Read configured library status (real, read-only API call).
docker compose run --rm app python scripts/prepare_evolus_workspace.py inspect

# Explicit resumable sync; compares existing remote bytes and refuses duplicates.
# Already completed: do not re-upload with the older non-resumable sync command.
docker compose run --rm app python scripts/prepare_evolus_workspace.py sync --apply

# Real Evolus execution, deterministic pre-AMD mode; no model/AMD connection required.
docker compose run --rm app python scripts/prepare_evolus_workspace.py test --apply --case market_claims_2025_09
docker compose run --rm app python scripts/prepare_evolus_workspace.py test --apply --case market_ratio_2025_03

# Offline generated-JavaScript checks on the laptop (Node required, no download/install).
python3 scripts/check_evolus_workflow_scripts.py

# Inspect indexed documents in workspace or use EvolusClient.list_documents().
# FUTURE ONLY: after the real model, agent, retrieval and production mappings are wired.
docker compose run --rm app python scripts/run_investigation.py \
  --case market_claims_2025_09 --provider amd_vllm --orchestrator evolus --language es
```

Current resumable receipts are written incrementally under reports/investigations/evolus-setup/. The older sync CLI uses evolus_knowledge_uploads.json and does not check existing content. Partial failures must be reviewed before resuming. Workflow errors/timeouts retain execution IDs; a polling timeout does not prove the job stopped. Do not resubmit blindly. No webhook receiver or new application API is implemented.

`GET /memories` requires a personal User API key according to the downloaded workspace OpenAPI document; a workspace key receives 401 on that route. This was a permission-contract mismatch, not a defective rotated key. Once the library ID is known, its metadata/documents and the workflow routes accept the application key. No persistent personal discovery key is needed.

## Demo flow and evidence

1. Select a FLAGSHIP and show its statistical evidence and both dates.
2. Show the immutable signal package and start the Evolus workflow.
3. Show relevant methodology retrieved from the Knowledge Library.
4. Show the open-model call linked to retained AMD/vLLM evidence.
5. Show labeled hypotheses, missing evidence and recommended checks.
6. Have the actuary review the unresolved case.

The pre-AMD demo can show real workflow execution, library document access and immutable human-review output. Label the model stage pending; no AI investigation or native agent retrieval has occurred. Live-demo blockers are the actual AMD endpoint/model, native agent/library attachment, replacement of the pending gate and production request/response mapping, followed by end-to-end evidence. Exact CNBS historical release dates remain unresolved, but do not block this disclosed retrospective investigation design.

## Polling, resumption and saved demo results

Use `EVOLUS_POLL_INTERVAL_SECONDS=10` and `EVOLUS_MAXIMUM_POLLS=120` for the live session. Multiple simultaneous fast pollers can hit Evolus REST throttling. A polling HTTP 429 is not proof that the underlying model workflow failed. Preserve its execution ID and resume the same run with `--execution-id <id>` on the investigation CLI; do not resubmit blindly. Resumption checks the stored execution input against the original signal and requested language before validating its output.

The dashboard restores only PASS-validated real Evolus reports from `reports/investigations/token-factory/`, checking provider, workflow evidence, original package hash, unchanged snapshot, references and human review. It rejects mock/pending/flagged reports. A restored result is labeled saved evidence, not a fresh model call. Full runtime audits remain ignored by Git.
