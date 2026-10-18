# Actuarial accounting evidence — Phase 3 review

Labels: **CONFIRMED** means explicit at the cited scope; **STRONGLY_SUPPORTED** means a reasoned dataset interpretation with a stated mapping gap; **UNRESOLVED** means the inspected evidence does not establish the requested field definition. Framework accounts are not automatically the CKAN extraction formula. File-page references are one-based.

## Official source register

The [machine-readable evidence registry](evidence_registry.json) records exact archived filenames, official URLs, download times and SHA-256 checks for 13 sources. The originals remain in ignored `data/raw/cnbs_semantics/`; none were replaced. Main sources:

| ID | Official document / relevant location | URL |
|---|---|---|
| S1 | CNBS CKAN Primas y Siniestros; resource list and resource dictionaries (`Saldo` column) | [Dataset](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros), [Siniestros resource](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros/resource/b36f83a9-d763-41da-809b-7e379fac990f) |
| S2 | Manual Contable de las Instituciones de Seguros, Sección III, criterios generales: file p.2, accumulation/accrual and accounting year | [Official manual](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/4.%20Secci%C3%B3n%20III-MC%20Seguros-CGC.pdf) |
| S3 | Manual Contable, Sección V, modified January 2023: file pp.170 (401), 172 (403), 189 (501), 190 (503) | [Official account relations](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/6.%20Secci%C3%B3n%20V%20MC%20Seguros%20%20%28Modificado%20Ene%2023%29.pdf) |
| S4 | Manual Contable, Sección VI, file p.2 §I filing periods, p.3 disclosure/authorization, p.4 currency | [Original official URL](https://www.cnbs.gob.hn/files/segurosNIIF/ManualContableNIIF/7-SeccionVI_MC-Seguros-ModEF.pdf), [accessible official publication copy](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%2BFinanciera%2FManuales%2BContables%2BNIIF%2FInstituciones%2Bde%2BSeguros/7.%20Secci%C3%B3n%20VI-MC%20Seguros-ModEF.pdf) |
| S5 | Manual Contable, Sección VII, file pp.2–3, statement-of-results model | [Official annexes](https://publicaciones.cnbs.gob.hn/Home/Viewer/Informaci%C3%B3n%20Financiera%2FManuales%20Contables%20NIIF%2FInstituciones%20de%20Seguros/8.%20Secci%C3%B3n%20VII-MC%20Seguros-Anexos.pdf) |
| S6 | CNBS publication portal, footer revision notice; Primas y Siniestros monthly catalogue | [Portal](https://publicaciones.cnbs.gob.hn/), [Catalogue API](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Cifras%20Estad%C3%ADsticas%20y%20Financieras%2FPrimas%20y%20Siniestros) |
| S7 | Panorama del Sistema Supervisado, December 2022, file p.17; December 2023, file p.15, §2.4 | [2022](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/08.%20Boletin%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic.2022.pdf), [2023](https://publicaciones.cnbs.gob.hn/Home/Viewer/Publicaciones%2BEstad%C3%ADsticas%2By%2BFinancieras%2FEstudios%2Be%2BInformes%2FPanorama%2Bdel%2BSistema%2BSupervisado/10.%20Boleti%CC%81n%20Panorama%20Sistema%20Supervisado_cifras%20a%20dic_2023.pdf) |

## Findings and unresolved questions

| Question | Supported finding | Status and remaining uncertainty |
|---|---|---|
| What is `Saldo`? | S1's dictionary supplies a numeric type without an account/extraction definition. The audited series is monetary; S2/S3 support accumulation over a calendar accounting year, while S5 uses monetary result balances. | Calendar-year cumulative reported accounting amount: **STRONGLY_SUPPORTED**, not a field-specific confirmed SQL/account mapping. The January/difference transformation remains the existing guarded policy. |
| Gross or net of reinsurance? | S1 lists separate resources for retained net claims and assumed-reinsurance incurred claims. Those titles do not define the base resource. S3 distinguishes recovery and expense accounts. | **UNRESOLVED** for base Siniestros `Saldo`; never label it gross or net merely because another resource is named net. |
| Paid, incurred or obligations? | S2 specifies accrual accounting at framework level. S3's 501 group includes direct/assumed/co-insurance expenses, settlement costs and 501105 unreported claims. | Framework distinctions **CONFIRMED**; which accounts feed this exact base dataset is **UNRESOLVED**. Do not label all amounts paid, incurred, obligations or cash flows. |
| Reserves and adjustments? | S3 separates technical-reserve movements in 503 from 501 claim expenses and its estimation/adjustment mechanics. | Accounting framework **CONFIRMED**. CKAN reserve inclusion, aggregation and netting remain **UNRESOLVED**. |
| Can a negative monthly increment be legitimate? | S3 p.189 allows credit adjustments/reclassifications in 501. A cumulative reported amount can decrease without meaning negative accident counts. | Legitimate adjustment mechanism **CONFIRMED at framework scope**. The reason for any particular negative row is **UNRESOLVED**; retain and review, never automatically “correct.” |
| Can annual balances be revised? | S6 explicitly warns that figures can be revised later. S7's 2023 report gives a different 2022 claims comparator from the 2022 report. | Revision possibility **CONFIRMED**. The cross-publication discrepancy does not identify a specific changed CKAN record, correction date, scope change or cause. Distinct raw vintages are required. |
| Institution/code changes? | The retained data show 0616 ending and 0618 starting around October 2019. Existing policy does not bridge codes. | The observed code transition is **CONFIRMED IN THIS SNAPSHOT**; legal continuity and comparability are **UNRESOLVED**. No accounting manual licenses automatic bridging for this extraction. |
| October 2019 coverage? | The guarded market sum is HNL 59,978,056.45, with 10 contributors and excluded codes 0616/0618; one 0618 row lacks the required same-code prior month. | **CONFIRMED IN THE DERIVATION**, not evidence of a complete-market contraction. The absent increment cannot be imputed as zero or reconstructed from another code without evidence. |

The January-2023 manual does not establish unchanged extraction conventions throughout 2018–2022. Current publication copies and historical snapshots must retain their own dates. This review strengthens the account-level explanation without upgrading the unresolved field mapping.

## Interpretation of the currently observed August outcome

Established data evidence: the retained source supports an August 2026 eligible increment of **HNL 155,258,339.81000004**. Its comparison with V1 is retrospective because these bytes predate forecast execution. The original precision is preserved; displayed cents/millions may be rounded explicitly.

| Potential explanation | Evidence classification | What is still required |
|---|---|---|
| Claims accounting adjustment | **PLAUSIBLE HYPOTHESIS**, framework permits adjustments | Account-level bridge, adjustment entries and insurer confirmation; no such causal evidence supplied |
| Portfolio/premium growth | **UNRESOLVED explanation** | Matched exposure/policy counts, coverage and business-mix data; monetary premiums alone do not prove claim incidence |
| Institution composition | Contributor and exclusion flags are **ESTABLISHED DATA EVIDENCE** | Legal-code continuity and contribution reconciliation before attributing a market change |
| Repair-cost inflation | **UNSUPPORTED as an attribution here** | Applicable official cost index and claim-severity/repair mix; none linked to this observation |
| Catastrophe-related monetary impact | **UNSUPPORTED as an attribution here** | Official event-to-portfolio/claim linkage, dates and covered-loss amounts; no cause inferred from a spike |
| Reporting-practice change | **PLAUSIBLE HYPOTHESIS**, not established | Dated circular, effective scope and reconciliation for the affected series |
| Reinsurance effects | **UNRESOLVED explanation** | Proven `Saldo` account mapping, ceded/retained reconciliation and consistent vintage |
| Increased accident frequency | **UNSUPPORTED** | Current source is monetary accounting data; individual event/claim counts are unavailable |

The forecast difference is established arithmetic. It is not causal evidence, a source-error diagnosis or a measurement of claim frequency. No external investigation or institutional contact was performed.
