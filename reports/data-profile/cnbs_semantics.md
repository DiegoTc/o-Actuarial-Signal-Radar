# CNBS data semantics validation — Phase 1.5

> Phase 2 implementation update: statistical baselines and the lagged retrospective backtest are now implemented. See [Phase 2 results](../statistical-baseline/baseline_summary.md) and [statistical methodology](../../docs/statistical-baseline-methodology.md). Earlier phase decisions and measurements below are retained as historical records. Strict point-in-time validity remains NOT VALIDATED.

Assessment date: 2026-10-03. Scope: official CNBS Primas and Siniestros dumps already ingested in Phase 1. **No historical replay or anomaly detection is implemented.**

## Current methodology update — 2026-10-14

Phase 1.5 is complete for Automobile/Nacional under the restricted accounting-increment interpretation below. **RETROSPECTIVE_BACKTEST_READY**; current mode **LAGGED_RETROSPECTIVE_BACKTEST**, assumption **CONSERVATIVE_TWO_MONTHS**; **STRICT_POINT_IN_TIME_NOT_VALIDATED**. Phase 2 may proceed with the current snapshot, while Phase 1.6 remains partial and non-blocking. The October 3 retrieval proves August 2026 availability by that date (33-day upper bound), not an exact release date or general historical lag. See the [methodology and research decision](../../docs/historical-replay-methodology.md) and [replay readiness](replay_readiness.md). The October 3 evidence and measurements below are preserved.

## Decision

**Saldo is STRONGLY SUPPORTED as a calendar-year cumulative reported accounting amount for both resources.** A separate, guarded Automobile/Nacional transformation is justified by official accounting and publication evidence. It produces monthly changes in those reported amounts, including adjustments. Calling these pure monthly cash payments, earned premiums or accident-month losses is not justified.

The confidence is deliberately below CONFIRMED: CNBS has not supplied a field-specific CKAN dictionary or the extraction formula connecting Saldo to accounting accounts. The revised account manual inspected is dated January 2023; an unchanged extraction/accounting convention throughout 2018–2022 is not directly established. **Automobile is not ready for point-in-time historical replay**, because actual availability dates, historical revision vintages, exact account scope and the causes of negative increments remain unresolved.

## Confidence and official evidence

CONFIRMED means an explicit official statement at the relevant scope. STRONGLY SUPPORTED means an inference supported by official framework/publication evidence, with its remaining gap stated. UNRESOLVED means that the sources inspected do not answer the question. Statistical growth/reset behavior alone never establishes accounting meaning.

| Question | Conclusion | Confidence | Source and concise evidence |
|---|---|---|---|
| Reporting frequency | Monthly for these two resources; separate reinsurance resources must not inherit it automatically. | CONFIRMED | [publication_catalogue](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Cifras%20Estad%C3%ADsticas%20y%20Financieras%2FPrimas%20y%20Siniestros) places Primas y Siniestros from January 2018 under Mensuales. [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) p.2 requires monthly results submissions. |
| Observed date grain | 104 calendar month ends, 2018-01-31–2026-08-31, in each dump. | CONFIRMED for this snapshot | [dataset_metadata](https://datos.cnbs.gob.hn/api/3/action/package_show?id=primas-y-siniestros) identifies the resources; raw checksums and measured dates are in the [Phase 1 profile](cnbs_profile.md). |
| Fecha Reporte meaning | Accounting period end, rather than cash/event date or release timestamp. | STRONGLY SUPPORTED | [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) p.2 says financial information refers to the last day of its period; the official current publication is headed with an August 31 cutoff. The CKAN field dictionary itself is silent. |
| Fiscal-year boundary | January 1–December 31 under the framework, unless CNBS specifies otherwise. | CONFIRMED at framework scope | [manual_III](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/4.%20Secci%C3%B3n%20III-MC%20Seguros-CGC.pdf) p.2 states the fiscal-year dates; no alternative period was found for these resources. |
| Saldo temporal convention | Calendar-year cumulative reported accounting amount, in both Primas and Siniestros. | STRONGLY SUPPORTED | [manual_V](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/6.%20Secci%C3%B3n%20V%20MC%20Seguros%20%20%28Modificado%20Ene%2023%29.pdf) pp.170,189 describes accumulating revenue/expense accounts, premium/claims accounts and year-end closure; [manual_III](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/4.%20Secci%C3%B3n%20III-MC%20Seguros-CGC.pdf) p.2 defines the year; [panorama_2022](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/08.%20Boletin%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic.2022.pdf) p.17 annual totals reconcile with December dumps. Exact CKAN extraction mapping is missing. |
| Exact premium/claims accounting scope | Gross/net premiums, cancellations, paid/incurred claims, reserves, reinsurance components and included accounts cannot be established field-by-field. | UNRESOLVED | [manual_VII](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/8.%20Secci%C3%B3n%20VII-MC%20Seguros-Anexos.pdf) pp.2–3 separates premiums, cancellations, net premiums and claims/settlement lines; [manual_V](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/6.%20Secci%C3%B3n%20V%20MC%20Seguros%20%20%28Modificado%20Ene%2023%29.pdf) describes account mechanics but neither resource dictionary maps Saldo to them. |
| Monetary unit, Nacional | Unscaled Lempiras in the dump; presentation may divide by 1,000 or 1,000,000. | STRONGLY SUPPORTED | [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) p.4 gives functional/presentation currency Lempiras; [manual_VII](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/8.%20Secci%C3%B3n%20VII-MC%20Seguros-Anexos.pdf) p.2 labels the model in Lempiras. Annual totals and one current institution/line cell reconcile after display scaling, below. CKAN has no explicit unit description. |
| Extranjera treatment | A foreign-denominated category apparently presented in Lempiras-equivalent amounts; not permission to treat the column as raw USD. | STRONGLY SUPPORTED for presentation only | [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) p.4 requires presentation in Lempiras; the 2022 claims total reconciles only when both category amounts are included at the same display scale. |
| Exact foreign conversion | Original foreign currency, conversion timing/rate for these flows, and whether translation creates accounting adjustments. | UNRESOLVED | [manual_II](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/3-SeccionII-MC-Seguros-DG.pdf) pp.3–4 and [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) p.4 distinguish transaction conversion from closing-rate translation of monetary assets/liabilities. Neither specifies the datastore extraction. Closing asset/liability rates must not be assumed for premium/claims amounts. |
| Can historical figures be revised? | Yes, revision is an explicit possibility; do not freeze current history as if originally published. | CONFIRMED | [publication_portal](https://publicaciones.cnbs.gob.hn/) says figures “están sujetas a revisión posterior”. [manual_III](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/4.%20Secci%C3%B3n%20III-MC%20Seguros-CGC.pdf) p.3 also permits restatement of comparative classification. |
| Did particular raw rows change retroactively? | Not established from the retained single distinct amount vintage. | UNRESOLVED | Raw content-addressed snapshots and [Automobile report](cnbs_automobile_semantics.md) show no earlier distinct baseline. Differences between official publications are documented below but do not identify a specific revised record. |
| Public release dates/lags | Not supplied by the report dates or current dumps. | UNRESOLVED | [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) p.2 sets a regulatory submission deadline of 15 working days after close. That is not a public dissemination date or guaranteed lag. |

The observed Primas currency is code `1` / `Nacional`; Siniestros also has code `2` / `Extranjera`. Codes, institution identifiers, parent/line labels and dates are retained as separate grouping dimensions. No currency conversion, mixed-currency production total or cross-resource financial join was added.

## Why cumulative interpretation is supported

In [manual_V](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/6.%20Secci%C3%B3n%20V%20MC%20Seguros%20%20%28Modificado%20Ene%2023%29.pdf), p.170, revenue accounts “Agrupa a las cuentas que acumulan ingresos devengados en el período”; premium account 401 permits adjustments/reversals and “Por la cancelación de saldos al cierre del ejercicio”. Page 189 describes accumulating expense accounts, including claims and settlement account 501, adjustments/reclassifications and year-end closure. Together with the fiscal year in [manual_III](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/4.%20Secci%C3%B3n%20III-MC%20Seguros-CGC.pdf), this supports year-to-date accounting balances rather than independent monthly flows. The CNBS-authored current report identifies its insurance NIIF/prudential framework; the annual publication reconciliations connect that framework to the amounts actually downloaded.

This is an inference from multiple official sources, not a direct Saldo definition. Account 401 or 501 is **not asserted to equal the precise CKAN extraction**. Accrual accounting by itself says when income/expense is recognized; it does not prove YTD accumulation. Monotonic growth and January resets are corroboration only. A monthly difference may contain cancellations, reserve movements, corrections or reclassifications, and can legitimately be negative. The exact components and historical framework changes still need CNBS clarification.

## Publication reconciliation and contradictory evidence

Amounts below are in **millions of Lempiras**, rounded only in the displayed comparison. Calculations use the current raw dumps, one December report date, all institution/line rows, and exact decimal summation. Adding the two claims currency categories here is an evidence check of published scope/units, not a production analytical aggregation or an authorized foreign monthly transformation.

| Publication / cutoff | Measure | Current dump sum, millions | Official displayed amount | Outcome |
|---|---|---:|---:|---|
| [panorama_2022](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/08.%20Boletin%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic.2022.pdf) p.17 / December 2022 | Primas, Nacional | 14312.037295 | 14312.0 | Reconciles at publication precision |
| Same | Siniestros, Nacional + Extranjera | 4892.821869 + 1886.867143 = 6779.689012 | 6779.7 | Reconciles at publication precision |
| [panorama_2023](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/10.%20Boleti%CC%81n%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic_2023.pdf) p.15 / December 2023 | Primas, Nacional | 16540.554407 | 16540.6 | Reconciles at publication precision |
| Same | Siniestros, Nacional + Extranjera | 5345.423281 + 1185.209431 = 6530.632713 | 6879.7 | **Does not reconcile**; difference 349.067287 million |

The 2023 publication's prior-year claims comparator is 7116.0 million, versus 6779.7 in the 2022 publication. **UNRESOLVED cause**: revision, definition/scope change or publication error cannot be distinguished. Matching premiums does not resolve the claims discrepancy. These checks support temporal interpretation without proving complete accounting comparability or a particular vintage revision.

A manual observation of the [CNBS-authored current report](https://app.powerbi.com/view?r=eyJrIjoiMWIzOGQwOWYtODA5Ny00MGM3LWJkNDEtYjhiOTJiOTRjNmY2IiwidCI6ImZlNDA4MTE2LWZkMTMtNDhjMy04MzJiLTc5NDU3ZGNjNmUyMyJ9&language=es&formatLocale=es-HN), discovered through [publication_catalogue](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Cifras%20Estad%C3%ADsticas%20y%20Financieras%2FPrimas%20y%20Siniestros), used August 2026, Moneda Todas, display Miles de Lempiras. Its Primas cell for SEGUROS DAVIVIENDA / Vehículos Automotores was 278838.8, matching raw Nacional `278838791.62 / 1000` rounded to one decimal. It described preliminary figures and later revision. No explicit YTD label was observed. This observation is logged in [source provenance](cnbs_semantics_sources.json); no durable screenshot/export was retained, so the archived manuals and annual publications carry the principal reproducible evidence.

## Separate derivation and safeguards

The policy is versioned in [config/cnbs_semantics.json](../../config/cnbs_semantics.json). Derivation requires CONFIRMED or STRONGLY SUPPORTED official temporal evidence and is restricted to exact `Seguros Generales` / `Vehículos Automotores` / currency `1` / `Nacional`, separately for each resource.

- January: `saldo_monthly_derived = saldo_reported`; previous December is never subtracted.
- February–December: subtract the exact prior calendar month end under the same `(resource, institution_code, parent_line, line, currency_code)`.
- Original raw files and original processed cumulative `saldo` remain unchanged. New files preserve those fields and add `saldo_reported`, `saldo_monthly_derived`, `saldo_derivation_status`, review flags and prior-value provenance.
- Invalid dates/amounts, non-month-end dates, duplicate/ambiguous keys, changed currency labels and missing prior months produce blank derived values with explicit blocked status. Selected rows are retained; outside-scope exclusion counts are explicit.
- Negative increments are retained and flagged, never clipped. Same-code institution-name changes are flagged; different codes, parent/line labels and currencies are never bridged. A code/name transition is not proof of legal continuity.
- An optional earlier raw baseline compares same-key amount/label changes and flags affected current/next-month differences. Added/deleted or ambiguous keys are separately reported. A December revision never contaminates January derivation. Snapshot differences do not establish an economic cause or original availability date.

`derived_*` means arithmetic was possible under this evidence policy, not that every amount is fully validated. `_review` requires documented treatment in retrospective evaluation and further investigation before economic interpretation. `blocked_*` has no monthly amount and must not be silently filtered or filled.

## Automobile / Nacional results

See [complete Automobile report](cnbs_automobile_semantics.md) and [machine-readable detail](cnbs_automobile_semantics.json) for every institution, coverage window, exact missing month, cumulative/derived example, negative increment and label change.

| Measure | Primas | Siniestros |
|---|---:|---:|
| Selected records, none dropped | 1144 | 1144 |
| Date range | 2018-01-31–2026-08-31 | 2018-01-31–2026-08-31 |
| Historical institution codes | 12 | 12 |
| Common full-history cohort | 10 | 10 |
| Internal gaps within each code's observed window | 0 | 0 |
| Monthly values derived | 1143 | 1143 |
| Blocked missing prior month | 1 | 1 |
| Negative derived differences | 1 | 19 |
| Same-code label transitions | 3 | 3 |
| Derived records requiring review, including overlaps | 4 | 22 |

The blocked row is `0618`, October 2019, in each resource. `0616` ASSA ends September 2019; `0618` ASSA CIA. DE SEGUROS starts October 2019. Both windows have no internal gaps, but legal/reporting continuity is unresolved and the previous code is not used as a baseline. The ten full-history codes are `0601, 0603, 0604, 0606, 0608, 0609, 0612, 0613, 0615, 0617`.

The negative premiums increment is November 2019 / `0618`, `-337710.9400000009`. Claims include decreases as large as October 2019 / `0615`, `-16228444.97`; all 19 are listed individually. Label changes include `0617` ASRURAL HN → SEGUROS BANRURAL in January 2025 and back in June 2025, and `0612` EQUIDAD → SEGUROS EQUIDAD in February 2026. No unusual **retroactive** revision has been established without a distinct baseline. Source floating representations are preserved through Decimal arithmetic; they are not rounded into false precision claims.

## Reproduction and validation

After the existing download/profile/prepare workflow:

```sh
docker compose build
docker compose run --rm app python scripts/fetch_cnbs_semantics_evidence.py
docker compose run --rm app python scripts/derive_cnbs_monthly.py
docker compose run --rm app pytest
```

All four commands succeeded on 2026-10-03. Evidence archiving retrieved all 13 configured official sources with HTTP 200 and validated PDF signatures / JSON responses. **54 tests passed** inside Docker, including 21 semantics tests covering gating, missing/duplicate priors, exact decimals, institution/line/currency changes, year boundaries, revisions and unchanged originals. Checksums of both raw and both original processed CSVs were verified unchanged after derivation. No additional PDF dependency was added to the runtime; read-only research rendering was performed separately.

Research and source selection are reviewed human evidence; the fetch command archives sources but does not regenerate their interpretation automatically. The checked-in report describes the recorded source/raw hashes, not any future CNBS update. A future semantic/accounting change requires reassessing the policy, not merely rerunning arithmetic.

## Remaining research and current Phase 2 decision

1. Obtain a CNBS field-specific definition/extraction account mapping for premiums and claims, including cancellations, paid/incurred claims, reserve movements and reinsurance treatment; confirm consistency across 2018–2026.
2. Resolve the 2023 annual claims discrepancy and the causes of the 20 negative Automobile differences. Do not label them revisions or economic signals by assumption.
3. Obtain actual publication timestamps/lags and distinct historical vintages, or explicitly design any later exercise as retrospective analysis of the latest revised snapshot rather than point-in-time replay.
4. Establish institution continuity and a reviewed cohort policy; keep ASSA codes separate until confirmed and review changing labels.
5. Before expanding beyond Nacional, obtain the original foreign currency, conversion rule and scaling from CNBS.

**Current decision (2026-10-14): Phase 2 may proceed with a lagged retrospective backtest of the current snapshot using the conservative two-month reporting lag.** Monthly reported accounting increments retain the documented restrictions. Strict point-in-time replay remains unvalidated; release-date/vintage reconstruction is a partial, non-blocking Phase 1.6 track. The research items above remain relevant to interpretation, cohort treatment and future expansion. No statistical baseline or backtest has been implemented. See the [methodology](../../docs/historical-replay-methodology.md).

## Source archive

Only official CNBS metadata, publications and accounting manuals were used. Publication folders/file URLs were discovered from CNBS catalogue responses; no resource URLs were invented. The CNBS-authored PowerBI report is linked by CNBS and hosted on its publishing platform, not a third-party mirror. Dataset ingestion still uses the official datastore dumps, never HTML scraping.

Archived originals are under git-ignored `data/raw/cnbs_semantics/`, with content-addressed snapshots. [cnbs_semantics_sources.json](cnbs_semantics_sources.json) records URL, final URL, retrieval time, HTTP status, byte size, SHA256, relevant PDF pages and the manual current-publication observation. The source registry is also in the policy. PDF page references above are one-based file page numbers.

| Source | Archived filename | Inspected pages / evidence |
|---|---|---|
| [dataset_metadata](https://datos.cnbs.gob.hn/api/3/action/package_show?id=primas-y-siniestros) | `dataset_metadata.json` | Metadata / catalogue / notice: Package metadata and resource descriptions do not define Saldo. |
| [primas_dictionary](https://datos.cnbs.gob.hn/api/3/action/datastore_search?resource_id=d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370&limit=0) | `primas_dictionary.json` | Metadata / catalogue / notice: Field types only; Saldo float8 and report date text. |
| [siniestros_dictionary](https://datos.cnbs.gob.hn/api/3/action/datastore_search?resource_id=b36f83a9-d763-41da-809b-7e379fac990f&limit=0) | `siniestros_dictionary.json` | Metadata / catalogue / notice: Same field types; no temporal/currency formula supplied. |
| [publication_catalogue](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Cifras%20Estad%C3%ADsticas%20y%20Financieras%2FPrimas%20y%20Siniestros) | `publication_catalogue.json` | Metadata / catalogue / notice: CNBS lists the current report under Mensuales, from January 2018; the linked CNBS-owned report footnote identifies the insurance NIIF/prudential framework. |
| [publication_portal](https://publicaciones.cnbs.gob.hn/) | `publication_portal.html` | Metadata / catalogue / notice: CNBS explicitly warns that supervised-system figures are subject to later revision. |
| [manual_catalogue](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros) | `manual_catalogue.json` | Metadata / catalogue / notice: Official discovery of the insurance manuals, including the January 2023 account relations version. |
| [manual_II](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/3-SeccionII-MC-Seguros-DG.pdf) | `manual_II.pdf` | 3, 4: Monthly financial submission and balance preparation; exchange-rate rules distinguish monetary assets/liabilities from other amounts. Not a CKAN conversion specification. |
| [manual_III](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/4.%20Secci%C3%B3n%20III-MC%20Seguros-CGC.pdf) | `manual_III.pdf` | 2, 3: Fiscal year January 1–December 31; accrual accounting and restatement of comparative amounts when classification changes. |
| [manual_V](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/6.%20Secci%C3%B3n%20V%20MC%20Seguros%20%20%28Modificado%20Ene%2023%29.pdf) | `manual_V_2023.pdf` | 170, 189: Revenue/expense accounts accumulate; premium account 401 and claims/settlement account 501 close at year-end and permit adjustments/reclassifications. These are framework accounts, not a proven exact CKAN formula. |
| [manual_VI](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf) | `manual_VI.pdf` | 2, 4: Financial information refers to last day of period; results submitted monthly within 15 working days. Functional/presentation currency Lempiras, foreign transactions translated at transaction-date rates. |
| [manual_VII](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/8.%20Secci%C3%B3n%20VII-MC%20Seguros-Anexos.pdf) | `manual_VII.pdf` | 2, 3: Results model reports current/prior-year balances in Lempiras; separates premiums, returns/cancellations, net premiums and claims/settlement amounts. |
| [panorama_2022](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/08.%20Boletin%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic.2022.pdf) | `panorama_2022.pdf` | 17: December 2022 totals: premiums L14,312.0 million and claims L6,779.7 million; both reconcile to current dumps at displayed precision. |
| [panorama_2023](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/10.%20Boleti%CC%81n%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic_2023.pdf) | `panorama_2023.pdf` | 15: December 2023 premiums reconcile; claims and the 2022 claims comparator differ from current/earlier figures. Cause unresolved; not proof of a particular revised record. |
