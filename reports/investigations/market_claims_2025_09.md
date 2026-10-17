# Investigation

MOCK: deterministic integration fixture; no AI investigation has been performed.

## Signal

signal_id: `market_claims_2025_09`

report_date: **2025-09-30**; availability_date: **2025-12-01**.

observed_value=185377003.67; expected_value=142434137.475; residual=42942866.19499999; robust_z_score=11.015446264198951.

raw_signal_level=ALERT; adjusted_signal_level=ALERT; materiality_level=HIGH.

provider=mock; model=deterministic-placeholder-v1; orchestrator=local

**MOCK — no AMD/Evolus inference.**

## What changed

- **OBSERVATION**: The saved residual is 42,942,866.19 Lempiras: observed_value − expected_value. (signal:/observed_value, signal:/expected_value, signal:/residual, signal:/raw_signal_level, signal:/adjusted_signal_level)

## Statistical evidence

- **OBSERVATION**: robust_z_score=11.01544626; standard_z_score=4.1732153424686524; adjusted_signal_level=ALERT (signal:/robust_z_score, signal:/standard_z_score, signal:/adjusted_signal_level)

- **FACT**: cusum_state={'level': 'WATCH', 'score': 3.6732153424686524, 'positive': 3.6732153424686524, 'negative': 0.0}; sensitivity_results=[{'scenario': 'fixed_cohort_sensitivity', 'status': 'scored', 'adjusted_signal_level': 'ALERT', 'robust_z_score': 7.599987084506023, 'residual': 41978971.52250001}, {'scenario': 'negative_fit_sensitivity', 'status': 'scored', 'adjusted_signal_level': 'ALERT', 'robust_z_score': 5.071461251755308, 'residual': 44426956.43000001}, {'scenario': 'trend_window_sensitivity', 'status': 'scored', 'adjusted_signal_level': 'ALERT', 'robust_z_score': 9.266997351764443, 'residual': 46435691.349999994}] (signal:/cusum_state, signal:/sensitivity_results)

## Economic materiality

{"evidence_refs": ["signal:/materiality_level", "signal:/residual"], "explanation": "Exploratory bands, not capital or budget limits.", "level": "HIGH", "unit": "Lempiras"}

## Persistence

No future persistence is inferred. Review only the sequence known through availability_date.

## Data quality

- **FACT**: data_quality_risk=MEDIUM; quality_flags=model_fit_review_sensitive (signal:/data_quality_risk, signal:/quality_flags)

## Possible hypotheses

No hypotheses generated; mock output performs no investigation.

## Missing evidence

- Did claim frequency or average claim severity increase?

- Did repair costs or portfolio composition change?

- Was there an accounting or reporting adjustment?

- Which institutions contributed most to the movement?

- Is there official evidence of an external event, and when was it public?

## Investigation questions

- Did claim frequency or average claim severity increase?

- Did repair costs or portfolio composition change?

- Was there an accounting or reporting adjustment?

- Which institutions contributed most to the movement?

- Is there official evidence of an external event, and when was it public?

## Recommended next checks

- Break down by institution without merging codes.

- Request official frequency, severity and accounting notes.

- Inspect numerical sensitivity scores, not only ALERT retention.

## Human review

**HUMAN_REVIEW_REQUIRED**

validation_status=PASS

Schema validation does not establish that narrative claims are true.

Review is pending: a person must assess evidence, uncertainty and next checks.

## Methodological limitations

- MOCK: neither AMD nor Evolus was called.

- LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.

- No cause is established. claims_to_premiums_ratio is not a validated actuarial loss ratio.

**LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

ALERT requires investigation; it does not establish cause, fraud, insolvency or continued growth.

## Provenance

```json
{
  "signal_source": [
    {
      "path": "data/processed/cnbs/expected-behavior/expected_behavior_manifest.json",
      "sha256": "a2ea5149bf2547ed839e720d1b19f8969ac2efea689bcccf401a5b7e98df3a4b"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/fixed_cohort_sensitivity.csv",
      "sha256": "737e5cb7c27b119a749472887e2a927dc807921ab67aea99cd36423c18988865"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/negative_fit_sensitivity.csv",
      "sha256": "b0f3beacec213dbf4336351d63d6a9f2b9b67d54789e5c7afbd71ecda5c3c1bf"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/primary_dynamic.csv",
      "sha256": "9091051504b5b05f36b22480057e5dd24045e1009ef84dd1abd3080a36add4ed"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/trend_window_sensitivity.csv",
      "sha256": "b98ecf2486736c68bbdaa6898b172820fb3ef890a6391e8118d662184f1961c2"
    },
    {
      "path": "reports/case-studies/candidate_evaluations.csv",
      "sha256": "2814f89a0c0d2b59cb1d0f6223a458dbbf5816d532e7f3693da8675ef329cf33"
    },
    {
      "path": "reports/case-studies/case_selection_manifest.json",
      "sha256": "48e3e23a1f3fa07281c83cf36adbae6a3b0c9a1c38be55aca82df37be32eaff9"
    },
    {
      "path": "reports/case-studies/case_selection_summary.md",
      "sha256": "3623b5269ca8a3b15adc446176c9737a94811da91b4993a09d0f6bc06b87522f"
    },
    {
      "path": "reports/case-studies/market_claims_2025_09.md",
      "sha256": "21c01bce183cfb75637ed1eea8992b51d53dfba3d5d6618d46a95871356dcbd1"
    },
    {
      "path": "reports/case-studies/surrounding_periods.csv",
      "sha256": "2f477e8008540c8d393368e77773c8e1332249e18ccb1ee790a4cf400965c026"
    }
  ],
  "case_study_source": [
    "reports/case-studies/market_claims_2025_09.md",
    "reports/case-studies/case_selection_summary.md"
  ],
  "signal_package_sha256": "b38b7575861c83427a6466fbb253723e08d1ff7cb43d92827f8003a0b4d02f8b",
  "configuration_version": "investigation-v1",
  "provider": "mock",
  "model_name": "deterministic-placeholder-v1",
  "prompt_version": "evidence-investigation-v1",
  "prompt_sha256": "ba8f154cb950d2243009f80279c004bff4ab0be4088a414889e2105489b14234",
  "model_endpoint_sha256": null,
  "response_schema_sha256": "a28ca877b317580b34c8f4cbbd31a257b401c4f27c5e290fd8fbc8a4a3f55066",
  "generated_at": "2026-10-16T03:46:20.770513+00:00",
  "language": "en",
  "orchestrator": "local",
  "knowledge": {
    "manifest_path": "evolus/knowledge/manifest.json",
    "manifest_sha256": "5058a3c578583cd1a3c81d577359f876e5d3f844262652efd027c0f135aba9d9",
    "retrieval": "LOCAL_MANIFEST_EXCERPTS_NOT_EVOLUS",
    "documents": [
      {
        "id": "knowledge:cnbs_semantics",
        "sha256": "374cfc2d089fa33b66a66c335afad73b3d23139d2e07fe4d6a7a67148762be00"
      },
      {
        "id": "knowledge:replay",
        "sha256": "d777b94850fb29ccdb660984f6ddfafd13ab49e9f0c4c2cf5257a880d328ee92"
      },
      {
        "id": "knowledge:statistical",
        "sha256": "ba45a3a8b3d11065c4f2affdffc4766532ecab88080f9df3ed566892c9b1f0dd"
      },
      {
        "id": "knowledge:expected_behavior",
        "sha256": "ab8012ded85188d2f134e970fa35af7e1f0598afec433baa931eb4a10452f70f"
      },
      {
        "id": "knowledge:case_selection",
        "sha256": "614e90b6ec953436ca2098cb536fe2dadac4f0c0ddf29ec8124411bf525a1bf8"
      },
      {
        "id": "knowledge:market_claims_2025_09",
        "sha256": "7cf5e57a65a77239d9e6fe7f3d6883ab85cebf01db8ecf56b21c16d91af9ddd5"
      }
    ]
  },
  "replay_mode": "LAGGED_RETROSPECTIVE_BACKTEST",
  "strict_point_in_time_status": "NOT_VALIDATED",
  "amd_hardware_execution_verified": false,
  "evolus_execution_verified": false,
  "request_settings": {
    "timeout_seconds": 60.0,
    "temperature": 0,
    "max_tokens": 2500
  }
}
```
