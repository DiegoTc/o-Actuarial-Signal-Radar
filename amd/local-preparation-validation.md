# Local preparation verification — 2026-10-15

AMD status: **NOT CONFIGURED**. These are local preparation checks, not GPU execution evidence.

- `docker compose build`: PASS; normal CPU application image, no GPU dependencies added.
- `docker compose run --rm app pytest`: **243 passed** (2.80 seconds). All 214 previous tests and 29 new offline deployment tests pass.
- Bash syntax checks: PASS for all six `amd/*.sh` wrappers.
- Local Markdown links in the preparation documents: PASS.
- Runtime evidence ignore rule: checked; generated evidence is ignored, `artifacts/amd/README.md` remains trackable. Evidence is excluded from the Docker build context.
- SHA-256 preservation check: **219 existing files unchanged**, including 60 data files, 83 reports, 36 engine files, 3 configuration files, and the existing docs/schemas/scripts/tests/Evolus files. The pre-change manifest was kept outside the repository in `/tmp`.

Changes for this task are confined to the AMD preparation tools/documents, evidence-directory README, a new deployment test file, the Dockerfile's `COPY amd/ amd/` instruction, and evidence exclusions in `.gitignore` / `.dockerignore`. Existing `.env.example` already contains the required application variables and was not changed by this task. Other existing Git changes predate this preparation.

Tests exercise missing settings, startup command construction, private-token redaction, explicit loopback defaults, container argument handling, HTTP/model failures, strict JSON parsing, unavailable host tools, dry-run isolation, signal/provenance/human-review contracts, ordered validation and preservation of failed application audits. Injected fixtures are synthetic and never evidence of AMD execution.

No GPU resource, paid service, model download, actual credential file, remote inference, live application investigation or Evolus configuration was created. Live ROCm/vLLM compatibility, latency, model response quality, correlated GPU activity, application success and actual cost remain unverified.

Next manual preparation: confirm credits and the current quote; register a public SSH key; enable/test Docker host networking; prepare a private matching server/client token; review the [live checklist](LIVE_VALIDATION_CHECKLIST.md). Creation and eventual destruction remain separately approved manual actions.
