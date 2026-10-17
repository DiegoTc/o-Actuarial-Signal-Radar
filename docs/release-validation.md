# Hackathon release validation

Documentation/public-repository release after Phase 6C. Analytical code, datasets, saved results, schemas, detector configuration and provider/workflow settings are preserved. No new model inference, ingestion, statistical replay or cloud deployment was triggered for these release checks.

## Scope

- Consolidated English/Spanish READMEs, source-derived rounded FLAGSHIP values, 2020 UNSCORED explanation, Mermaid architecture and honest live-demo status.
- Added the documentation index and retained detailed CNBS/data-foundation instructions in a dedicated reference.
- Hardened ignore rules for environment variants, Worker development secrets and build/test caches. Local data, credentials, screenshots and raw runtime audits remain excluded.
- No LICENSE exists and none was added. Provider/model attribution remains explicit.

## Regression results

| Check | Result |
|---|---|
| `docker compose run --rm app pytest` | PASS — 313 tests |
| Frontend `npm test` | PASS — 25 tests |
| Frontend `npm run typecheck` | PASS |
| `npm --prefix cloudflare test` | PASS — eight gateway tests |
| `docker compose build` | PASS — Python and Next.js images |
| `npm --prefix cloudflare run build:production` | PASS — local OpenNext bundle, no redeployment |
| Local browser tests with `RUN_LIVE_VALIDATION=1 npx playwright test` | PASS — 16 tests, including saved real-report checks |

The browser flag enables read-only checks of existing validated saved AMD/Evolus reports; it does not submit new inference. Data-dependent checks require local artifacts not included automatically in a fresh clone.

## Repository checks

Before staging, known secret values and conservative credential/coupon patterns were checked against candidate files and all reachable Git-history objects. No matches were found. The staged set is checked again before commit. Secret values and full scan receipts stay local and ignored.

The preservation baseline covers **346 files**, including analytical source, data, reports, schemas, frontend, deployment/provider configuration and local environment files. All 346 hashes matched after documentation edits. The documentation check verified 124 relative links with no missing or Git-ignored targets. FLAGSHIP display values were formatted directly from existing packages, and `git diff --check` passed before staging.

These are repository/regression checks, not a fresh acceptance test of every public model run. See [Cloudflare deployment](cloudflare-deployment.md) for the actual outcomes: claims completed; the latest ratio attempt produced a warning and its reviewed retry failed with `Missing model execution envelope`. Full fresh public end-to-end acceptance remains **PARTIAL / VERIFIED FOR CLAIMS CASE**. No safeguard was weakened to bypass that result.

## Remaining submission items

- Review the public analytical walkthrough and disclose the ratio investigation limitation.
- Confirm Workers Free billing tier from the account dashboard; OAuth subscription reading returned 403.
- Select a repository license explicitly if one is desired or required by submission rules; this release does not choose one.
- Complete the hackathon submission materials and required form separately; committing/pushing this repository does not submit the entry.
