# Phase 4 — Post-detection investigation methodology

The statistical engine detects first. AI investigates second. Humans decide. Phase 4 does not fit models, change thresholds, recalculate monthly values, modify case selection or decide whether an anomaly exists. Statistical modules never import the investigation layer and remain runnable without any provider credentials.

## Signal handoff

`scripts/build_investigation_package.py --case <selected-id>` reads the retained Phase 3.5 candidate/evidence manifests and Phase 3 scenario CSVs. It verifies their declared SHA-256 values, checks candidate numbers/levels against the saved primary output, and selects the saved standard-z/CUSUM companion rows. It does not call the analytical engines. The canonical [signal schema](../schemas/investigation_signal.schema.json) defines English field names, both dates, numerical values, signal levels, quality/cohort/negative sensitivity, suitability, source hashes and methodology/replay versions.

Packages are deterministic and timestamp-free; provenance timestamps belong to the investigation attempt. Only selected FLAGSHIP/SUPPORTING cases can be handed off. Original output directories are protected write destinations. Newly generated packages live in `data/processed/investigations/`; existing processed CNBS data remain unchanged. Concise example packages are versionable under `evolus/examples/`; no raw datasets are model context.

## Timing and scope

Report_date is the accounting period end; availability_date is simulated eligibility under the existing calendar helper. The package validates that relationship rather than implementing a second policy. Persistence context includes T−3 through T only and rejects later availability. Case-study T+1…T+3 follow-up is excluded from the structured package and the curated case excerpts.

This is **RETROSPECTIVE_CASE_REVIEW** of already selected cases, not an as-of historical agent. Knowledge includes currently retained methodology and hindsight-selected fixed-cohort sensitivity. It does not reconstruct a historical analyst's knowledge. Replay remains **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time is **NOT VALIDATED**. Revisions, exact historical releases and accounting interpretation remain unresolved.

## Provider and orchestration boundaries

- `mock`: deterministic integration fixture, empty hypotheses, explicit no-AI/no-AMD/no-Evolus notice. It copies handoff facts and asks questions; it does not synthesize explanations or invent analytical conclusions.
- `amd_token_factory`, Evolus orchestration: the current ACT III path. The native Evolus LlmCall block uses `own/deepseek-v4-flash`, with six indexed, downloaded, content-verified Knowledge Library excerpts supplied in context. Both real FLAGSHIP investigations passed validation. This is hosted Token Factory evidence; no Developer Cloud credits, GPU droplet or self-hosted ROCm/vLLM is required or claimed. Native semantic-search execution is not independently verified.
- `amd_token_factory`, local orchestration: direct OpenAI-compatible Chat Completions for diagnosis/smoke tests, JSON-object mode followed by unchanged full-schema validation. Direct execution alone does not verify Evolus. The gateway returns `self-dploy/<model>` in its response; only that observed catalog prefix and the exact requested model are accepted.
- `amd_vllm`, local orchestration: one remote OpenAI-compatible vLLM request using a team-configured open model; no model name is assumed. Endpoint/model configuration is not AMD hardware proof.
- `amd_vllm`, Evolus orchestration: application preflight → native Workflow → Knowledge Library/agent → team AMD model → application postflight. Local mock/direct mode is not described as Evolus execution. See the [Evolus setup/status](../evolus/README.md).

Remote failures never silently fall back to mock. HTTP response sizes, timeouts and polling are bounded. A polling timeout can leave a remote workflow running; its execution ID is retained when available. There is no automatic resubmission or incident closure.

## Knowledge and prompts

The [knowledge manifest](../evolus/knowledge/manifest.json) records existing Markdown sources, exact headings, source/excerpt hashes and upload representations. Only curated sections are sent/uploaded, with a bounded per-case local context. No raw CNBS rows, API credentials or runtime environment dump enter prompts. Local excerpts are labeled LOCAL_MANIFEST_EXCERPTS_NOT_EVOLUS. Uploaded content must finish indexing and be attached to the agent before live use.

The prompt treats documents as evidence, never executable instructions. FACT requires direct support; OBSERVATION describes supplied statistics; HYPOTHESIS requires missing evidence and LOW/MEDIUM confidence; UNRESOLVED means insufficient evidence. Causal HIGH confidence is disallowed by schema. Questions about frequency/severity, repair costs, portfolio mix, accounting adjustments or external events remain questions unless separately evidenced. Known historical events are not labels or causes.

Raw-vs-adjusted labels refer to the robust-z 12-month reference. Another raw method may already alert. UNAFFECTED negative-fit status does not mean unchanged score calibration; saved alternate numerical scores remain supplied. Materiality is exploratory, and ratio deviations are not Lempiras or a validated actuarial loss ratio.

## Response validation and audit

The [response schema](../schemas/investigation_response.schema.json) requires English keys, output language, human review and an exact `signal_snapshot`. Validation flags:

- malformed, duplicate-key, fenced or non-finite JSON;
- missing/extra fields, invalid hypothesis confidence/status or false human_review_required;
- altered signal identity, date, amount, decision level, materiality or units;
- unregistered evidence references, provider/status/model inconsistencies or truncated completions;
- unsupported causal/definitive wording in English/Spanish;
- missing/mismatched Evolus citation/model metadata.

The original model text and transport envelope are preserved in a timestamped audit sidecar, alongside prompts. Invalid text is not repaired or silently rewritten. The public JSON keeps the parsed response and validation issues alongside the authoritative signal. The Markdown draft suppresses unvalidated narrative sections, explicitly identifies issues and points to the untouched audit. CLI exit codes: 0 = validation passed, 1 = setup/source error before generation, 2 = flagged/provider error with a review artifact.

The lexical causal guard is conservative, may flag legitimate mentions, and can miss paraphrases. Citation membership and matching hashes do not establish semantic entailment or prove native retrieval. Schema validation cannot prove that free-text claims or numbers are correct. A malicious or mistaken model can still produce misleading text; no output is automatically approved. Deterministic copied signal fields remain the authoritative evidence shown to reviewers.

Every attempt records source/case paths and hashes, package/config/prompt/schema versions/hashes, provider/model, timestamp/language, replay restrictions, knowledge provenance and provider metadata where available. Model-provider labels and a remote execution ID do not prove AMD GPU use. `amd_hardware_execution_verified` remains false until separately retained host evidence is reviewed; the repository does not auto-certify it.

## Human review

Every branch is **HUMAN_REVIEW_REQUIRED**, including schema PASS. PASS means structural/consistency checks passed; it is not approval, causal validation or an actuarial decision. Reviewers must reconcile narrative statements with immutable signal values, assess flags/sensitivities, identify genuinely missing evidence, and approve any subsequent investigation manually. There is no automatic reviewer approval, incident closure, solvency judgment or downstream action.

See [AMD Token Factory setup](../amd/README.md), [Evolus workflow](../evolus/README.md) and [live verification evidence](../reports/investigations/token-factory/validation.md). Self-hosted ROCm/vLLM remains an optional unverified deployment path; current service verification does not change that hardware flag.

Spanish reflexive negation such as “No se establece causa, fraude o insolvencia” is treated as a denial, not a causal assertion. Positive assertions and a subsequent contrasting accusation are still flagged. Original model text is preserved. Execution resumption verifies the stored signal/language before revalidating the original result; it never submits another model call. The local message hash is a reference-prompt audit, while the actual native model step is configured in Evolus.
