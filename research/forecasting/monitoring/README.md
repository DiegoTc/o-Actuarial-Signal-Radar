# Phase 3 — actuarial validation and frozen-forecast monitoring

Independent research on `research/claims-forecast-2026-2027`. V1, V2, original datasets, anomaly detection and production services are unchanged. No model is fitted or recalibrated here. No commit, push, merge or deployment is part of this phase.

Read first:

1. [Accounting evidence and unresolved definitions](reports/actuarial_interpretation.md).
2. [Official publication timing and revision evidence](reports/publication_timeline.md).
3. [Monitoring methodology and temporal policies](METHODOLOGY.md).
4. [Actual frozen-forecast evaluation](results/2026-10-18-retained-oct03-r2/evaluation_report.md), [CSV](results/2026-10-18-retained-oct03-r2/forecast_monitoring.csv), [JSON](results/2026-10-18-retained-oct03-r2/forecast_monitoring.json), [figure](results/2026-10-18-retained-oct03-r2/actual_vs_frozen.png).
5. [Revision-assessment report](results/2026-10-18-vintage-check/revision_report.md).
6. [February 2027 research outline](reports/february_2027_outline.md).

[Integrated scientific report](reports/research_evidence_report.md) and [validation record](reports/validation.md) summarize findings, tests and unresolved research questions.

## Current result and its interpretation

The original October 3, 2026 snapshot already includes **August 2026**, deliberately excluded from V1/V2 fitting. It supplies an eligible monetary accounting increment of **HNL 155,258,339.81000004**, compared with the unchanged V1 forecast **HNL 157,402,825.05**. Absolute error is **HNL 2,144,485.23999996**, or **1.381236745558602%** of the observed amount. The value falls inside both original intervals.

This is **one retrospective comparison (n=1)**, not prospective model validation, seven-month accuracy or interval calibration. The floating-source decimal tails are preserved for audit, not asserted as economic measurement precision. September 2026–February 2027 remain explicitly missing in this vintage.

Receipt-based and simulated-lag evaluations are separate. These exact bytes were retained by October 3; the helper nevertheless makes August eligible **November 1**. At this October execution the receipt-based sample is **n=1**, the unchanged simulated-lag sample is **n=0**. Official first-publication dates remain unknown. No newer claims data were downloaded.

## Commands — repository root, existing isolated research environment

```sh
# Existing environment/dependencies; no production dependency change.
python3.12 -m venv .local/forecasting/venv
.local/forecasting/venv/bin/pip install -r research/forecasting/requirements.txt

# Read-only checks.
.local/forecasting/venv/bin/python -m research.forecasting.robustness.run \
  --verify research/forecasting/robustness/results/2026-10-18-v2

# FIRST local registration only; the bundled registry already exists in this repository.
# Requires original ignored raw/metadata files; no download occurs.
# On a fresh clone with the original retained sources, use a NEW ID if needed.
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli \
  bootstrap-retained --id retained-local-copy

.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli \
  verify-snapshot \
  --snapshot research/forecasting/monitoring/snapshots/retained-local-copy.json

# Always choose a NEW output directory. Each run binds one explicit snapshot.
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli evaluate \
  --snapshot research/forecasting/monitoring/snapshots/retained-local-copy.json \
  --output research/forecasting/monitoring/results/NEW-EVALUATION-ID

# Public artifact integrity + original frozen-forecast/reference consistency.
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli verify-result \
  --output research/forecasting/monitoring/results/2026-10-18-retained-oct03-r2

.local/forecasting/venv/bin/python -m pytest -c research/forecasting/pytest.ini \
  research/forecasting/tests research/forecasting/robustness/tests \
  research/forecasting/monitoring/tests

docker compose run --rm app pytest
```

**Fresh-clone note:** original observational bytes are Git-ignored, so public frozen-result verification and raw-snapshot re-execution are different operations. Do not replace missing original bytes with a fresh download. To recreate the existing registry on another machine, obtain the exact matching original files, use the separate `retained-local-copy` registration above, and pass its registry explicitly to subsequent evaluation commands. This is the same content vintage, not new revision evidence. The pre-existing public registry must not be silently rebound to different bytes or edited paths.

## Future snapshots — explicit manual workflow only

First inspect the source, purpose and isolation plan; this command sends **no network request**:

```sh
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli plan-download \
  --purpose 'Monitor frozen V1 outcomes using a separately retained official vintage'
```

When the researcher explicitly decides to acquire a new version, this command performs the actual new acquisition. **It was not run for this phase.** Choose a unique ID:

```sh
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli download \
  --id NEW-SNAPSHOT-ID \
  --purpose 'Monitor frozen V1 outcomes; never replace original training data' \
  --acknowledge-new-vintage
```

The acquisition plan is saved before network access. Official source and metadata URLs are fixed in [config](config.json). Bytes, receipts, metadata and guarded monthly derivation stay in `.local/forecasting/monitoring/`; only a compact registry goes under `snapshots/`. An interrupted/invalid acquisition is not a valid registered snapshot; use a distinct ID after diagnosing it. Never move raw CSVs into the public research folder.

Alternatively import locally acquired official bytes with their matching acquisition receipt:

```sh
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli import \
  --id NEW-SNAPSHOT-ID --raw PATH-TO-RAW-CSV \
  --receipt PATH-TO-RECEIPT-JSON --metadata PATH-TO-CKAN-PACKAGE-JSON
```

Receipt fields: `resource_id`, exact official `source_url`, timezone-aware `download_timestamp`, `sha256`, `file_size`, `http_status=200`. A receipt supplied by a researcher is an auditable assertion with byte checks, not independent timestamp notarization. Metadata must identify the same official resource. Missing schema fields, invalid provenance, future reporting periods or reused IDs stop ingestion. No forecast code runs during import.

For verified publication evidence, optional `--publication-evidence FILE.json` accepts a list of entries containing `report_date`, `publication_timestamp`, the exact `raw_sha256`, `verification_status=MANUALLY_VERIFIED`, official CNBS `evidence_url`, retained `evidence_path` and its `evidence_sha256`. The researcher must establish that the publication evidence actually applies to this period and these bytes. Metadata changes or receipt timestamps are insufficient; do not invent dates to fill the field. Without such evidence it remains null.

Compare vintages explicitly and preserve the report:

```sh
.local/forecasting/venv/bin/python -m research.forecasting.monitoring.src.cli revisions \
  --baseline research/forecasting/monitoring/snapshots/retained-2026-10-03.json \
  --current research/forecasting/monitoring/snapshots/NEW-SNAPSHOT-ID.json \
  --output research/forecasting/monitoring/results/NEW-REVISION-REPORT-ID
```

Same-key revisions, new periods, historical additions/removals, label changes and ambiguity remain separate. A changed cumulative balance can affect two monthly increments; no cause is inferred. Two identical copies do not establish historical stability. Use the new registry in a **new** evaluation output directory; do not refresh previously published scores in place.

## Documentary review tooling

Monitoring uses the existing isolated research requirements. Optional PDF inspection uses a **separate** environment and [documentary requirements](requirements-evidence.txt), with its actual [environment lock](reports/documentary_environment.lock.txt). It is not a runtime/production dependency. Original manuals and two newly archived regulatory PDFs were inspected; retained source hashes are in the evidence registries. Current CKAN metadata/activity queries retrieved documentary metadata only, never a new claims dump. No external enquiries were sent.

The evidence package is ready for research review. A full seven-month outcome evaluation is not promised for February 2027; under the unchanged lag, February is eligible May 1.
