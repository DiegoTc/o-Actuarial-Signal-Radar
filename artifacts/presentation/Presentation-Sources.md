# Final hackathon presentation — sources and screenshot provenance

Eight slides, English, 16:9. The PowerPoint contains editable text and diagrams, real application screenshots, and speaker notes for approximately three minutes. The PDF was exported from the actual PowerPoint using Keynote. Every rendered slide was visually reviewed.

## Screenshots used

| Screenshot | Slide(s) | Provenance |
|---|---|---|
| 2025 monthly claims — yearly dashboard view | 1, 2 | Captured from the live public dashboard on 2026-10-17. Includes the real observed/expected chart, monthly axis, and saved classifications. |
| September 2025 claims — observed/expected/difference summary | 1 | Captured from the live case page on 2026-10-17; cropped to its actual metrics. |
| 2025 claims — observed versus expected chart | 4 | Captured directly from the live yearly chart on 2026-10-17. |
| 2025 claims — difference from expected chart | 4 | Captured directly from the live yearly residual chart on 2026-10-17. |
| Completed claims investigation, AMD receipt, human-review requirement | 5 | Cropped from an existing screenshot of the real public production validation run. Explicitly labeled **recorded real public run**. Spanish UI output is preserved as photographed. |

No chart or dashboard screenshot was recreated. Presentation diagrams are explanatory native slide objects, not fabricated product UI. Screenshots were cropped and scaled proportionally.

During the new read-only capture, both public investigation panels showed `NOT_STARTED`. A Railway restart can clear transient investigation state. The deck therefore uses previously recorded real evidence for completion; it does not pretend a new inference was run. No new investigation was submitted for this presentation.

## Public sources

- [Live dashboard](https://actuarial-signal-radar.diegoturciostc.workers.dev)
- [2025 claims view](https://actuarial-signal-radar.diegoturciostc.workers.dev/?metric=claims&view=year&year=2025)
- [September claims case](https://actuarial-signal-radar.diegoturciostc.workers.dev/cases/market_claims_2025_09)
- [March ratio case](https://actuarial-signal-radar.diegoturciostc.workers.dev/cases/market_ratio_2025_03)
- [Repository and English README](https://github.com/DiegoTc/o-Actuarial-Signal-Radar)
- [Spanish README](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/README.es.md)
- [Documentation index](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/docs/README.md)
- [Expected-behavior methodology](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/docs/expected-behavior-methodology.md)
- [Replay methodology](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/docs/historical-replay-methodology.md)
- [Evolus integration](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/evolus/README.md)
- [AMD integration](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/amd/README.md)
- [Public production validation and limitations](https://github.com/DiegoTc/o-Actuarial-Signal-Radar/blob/main/docs/cloudflare-deployment.md)

## Factual checks

The public GitHub README matched the local release README byte for byte. Public case API values were checked against the existing immutable local investigation packages. Rounding is presentation-only; statistical values and classifications were not recomputed.

- Claims: observed L185,377,003.67; expected L142,434,137.475; residual approximately +L42,942,866.195; relative residual 0.30149279488940856; residual robust z 11.015446264198951.
- Ratio: observed 0.6391391483302911; expected 0.5305365090821963; residual 0.10860263924809477; residual robust z 8.611067998372137; RAW NORMAL → ADJUSTED ALERT.
- Claims represent monetary accounting amounts, never accident counts or counts of individual claims.
- Latest fresh public end-to-end status remains PARTIAL / VERIFIED FOR CLAIMS CASE. The ratio retry failed with `Missing model execution envelope`; safeguards were not weakened.
- Model inference is AMD Token Factory / DeepSeek-V4-Flash through Evolus. Self-hosted ROCm/vLLM is not validated.
- Evolus workspace: Actuarial Signal Radar. Knowledge Library: ActuarialSignalRadarMemory1. Workflow: Actuarial Signal Investigation. Six indexed documents were checksum-verified in the recorded validated claims workflow; native semantic search is not independently validated.

## Presentation validation

- Eight slides, 16:9, all with speaker notes (448 narration words).
- Both case values checked against saved source packages.
- No out-of-bounds slide objects.
- PDF and PowerPoint checked against actual locally stored secret values without logging those values: PASS.
- Live demo and GitHub links returned HTTP 200. PDF link annotations are present.
- No new model inference, cloud provisioning, analytics changes, or application changes.

These presentation deliverables are accompanied by the demo draft video and narration audio. See the [presentation assets index](README.md) for downloads.
