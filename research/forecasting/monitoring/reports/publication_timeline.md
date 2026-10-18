# Official publication timing and vintage evidence

## What the official documents establish

| Evidence | Exact location | Supported conclusion | What it does not establish |
|---|---|---|---|
| CNBS Manual Contable, Sección VI | File p.2, §I; [official copy](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%2BFinanciera%2FManuales%2BContables%2BNIIF%2FInstituciones%2Bde%2BSeguros/7.%20Secci%C3%B3n%20VI-MC%20Seguros-ModEF.pdf) | Institutions submit monthly financial statements to CNBS, referring to period end, with a stated 15-business-day filing deadline. | A filing deadline is **not** the actual public release date of a monthly CKAN row. |
| CNBS Primas y Siniestros publication catalogue | `2. Mensuales`, report from January 2018; [official catalogue](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Cifras%20Estad%C3%ADsticas%20y%20Financieras%2FPrimas%20y%20Siniestros) | Monthly classification is officially documented. | No exact day-of-month release schedule or row-level release log was recovered. |
| Circular CNBS 007/2022, April 5, 2022 | File p.1 considerando (2), p.2 considerando (5); [official PDF](https://circulares.cnbs.gob.hn/Archivo/Viewer/28/1) | Recites a monthly CNBS statistical-publication mandate and the 2020 rules for insurer annual/quarterly statements. | A general mandate is not proof of compliance, exact release dates or CKAN insurance-data timing. |
| La Gaceta 34,728, August 25, 2018; insurance publication norms | File p.2 considerando (4); pp.3–4, arts.7/10; [official CNBS archive](https://circulares.cnbs.gob.hn/Archivo/Viewer/267/Gaceta%2034728%20Resolucion%20GES%20745%2021-08-2018.pdf) | Gives framework implementation history and annual/quarterly statement-publication rules. | Dated institution-level rules do not establish the monthly datastore release schedule or unchanged later rules. |
| CNBS publication portal | Footer [revision warning](https://publicaciones.cnbs.gob.hn/) | Published figures can be revised. | Does not identify which historical record changed, when or why. |

The two additional PDFs were acquired only after a [documentary acquisition plan](documentary_acquisition_plan.json) was written; [receipts and hashes](additional_official_sources.json) are separate from observational snapshots. No new claims dataset was downloaded. The 2018 document supports framework implementation from January 2018, but does not prove a stable CKAN account extraction across years or upgrade the frozen v1 methodology.

## Current metadata/activity inspection

The [evidence registry](evidence_registry.json) preserves a compact record of two actual official API responses, with full response bytes in ignored local documentary storage:

- `package_show`: package `metadata_modified` **2024-02-01T00:54:38.549840**, claims-resource metadata timestamp **2024-02-01T00:54:26.400823**, resource `last_modified` **null**. The response bytes match the retained October 3 package-metadata bytes despite observational data through August 2026.
- `package_activity_list` with limit 100: **11** returned activities, dated September 30, 2022 and February 1, 2024. They concern package activity, not row-level monthly publication or amount revisions.

These responses do not recover historical monthly release dates or distinct observational vintages. They also do not prove that no other archive exists. Search-result crawl dates and metadata creation/update dates are not substituted for publication dates. Some direct PDF/API URLs were inaccessible through the browsing tool; official alternate URLs or already-retained matching archives were used, and the two metadata APIs were queried directly. This access limitation is not evidence that historical information does not exist.

## What could an analyst actually have known?

**July 31, 2026:** the exact historical public information set is **UNRESOLVED**. A snapshot retrieved in October cannot prove which revision or reporting month was accessible in July. No July receipt or historical row-level release archive is available here. The project helper's April cutoff at a simulated July decision date is an assumption, not recovered publication history.

**October 3, 2026:** the retained successful Siniestros download at **16:41:14.238865 UTC**, matching its sidecar and content-addressed archive, contains reporting periods through **August 31, 2026**. It establishes availability of those retained bytes **by retrieval**, not first publication. For August, that is a 33-day reporting-end-to-download upper bound; it is not a universal reporting lag. The snapshot contains no September outcome.

**Forecast execution:** V1 began **October 18, 2026 at 00:32:13.398091 UTC** (October 17 in Honduras). All August/September targets preceded execution; those comparisons cannot be called prospective even though their actuals were excluded from fitting. Later target periods were not completed at execution, but their prospective evaluation remains subject to vintage and data-access limitations.

## Distinct dates retained by monitoring

| Concept | August 2026 example |
|---|---|
| Source accounting/reporting period | 2026-08-31 |
| Exact first CNBS publication | **UNRESOLVED / null** |
| Retained download | 2026-10-03T16:41:14.238865+00:00 |
| V1 execution | 2026-10-18T00:32:13.398091+00:00 |
| Receipt-based comparison eligibility | After actual forecast execution and receipt; execution is later in this example |
| Existing simulated-lag eligibility | **2026-11-01** |
| Actual evaluation time | Stored in each monitoring run's manifest and rows |

The complete July training information set has simulated availability **October 1**, not July 31. Receipt-based monitoring and simulated-lag scoring are intentionally different, separately reported policies; the production helper is unchanged.

| Target month | Simulated eligibility under existing helper |
|---|---|
| August 2026 | November 1, 2026 |
| September 2026 | December 1, 2026 |
| October 2026 | January 1, 2027 |
| November 2026 | February 1, 2027 |
| December 2026 | March 1, 2027 |
| January 2027 | April 1, 2027 |
| February 2027 | May 1, 2027 |

For the February 2027 presentation, do not promise complete observed seven-month results. Actual retrievals might precede simulated dates, but must have their own retained receipts and must not be invented. Strict historical point-in-time validity remains **NOT VALIDATED**.

## Evidence still needed

Seek CNBS confirmation of the base resource's exact account formula, revision policy, row-release schedule and available historical extracts, with dates and versions. The official portal lists `InformesyCifras@cnbs.gob.hn` for information enquiries; a draft question list is in the presentation outline. No message was sent. Institution statements can provide additional reconciliation evidence but cannot automatically stand in for identical-scope datastore vintages.
