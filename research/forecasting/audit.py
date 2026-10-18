"""Read-only source audit. No downloads, monthly derivation, or model fitting."""
import calendar
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'actuarial-engine'))
from preprocessing.availability import availability_date
from statistical.data import normalize, market_events

CUTOFF = '2026-07-31'
MONTHLY = 'data/processed/cnbs/monthly/automobile_siniestros.csv'


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def month_end(year, month):
    return date(year, month, calendar.monthrange(year, month)[1]).isoformat()


def add_months(value, delta):
    d = date.fromisoformat(value)
    year, month = divmod(d.year * 12 + d.month - 1 + delta, 12)
    return month_end(year, month + 1)


def monthly_claims(rows, cutoff=CUTOFF):
    """Filter BEFORE normalization/aggregation. Ignore all later amount values."""
    availability_date(cutoff)  # validates ISO month-end, reuses existing helper
    selected = [r for r in rows if r['report_date'] <= cutoff]
    events = normalize(selected, negative_policy='retain')
    markets = [r for r in market_events(events) if r['metric'] == 'monthly_claims']
    if not markets or markets[-1]['report_date'] != cutoff:
        raise ValueError('Missing observation cutoff; no download or imputation allowed')
    for i, row in enumerate(markets):
        if row['value'] is None:
            raise ValueError('Market month without eligible values; research must stop')
        if i and row['report_date'] != add_months(markets[i-1]['report_date'], 1):
            raise ValueError('Missing market month; no silent interpolation or zero-fill')
    return markets, events


def source_audit(root=ROOT):
    root = Path(root)
    manifest_path = root / 'data/processed/cnbs/monthly/monthly_derivation_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    sources = {}
    for name in ['primas', 'siniestros']:
        raw = root / f'data/raw/cnbs/{name}.csv'
        sidecar = root / f'data/raw/cnbs/{name}.metadata.json'
        metadata = json.loads(sidecar.read_text())
        digest = sha256(raw)
        if digest != metadata['sha256'] or digest != manifest['resources'][name]['raw_sha256']:
            raise ValueError(f'Raw {name} hash differs from retained provenance')
        archive = root / f'data/raw/cnbs/snapshots/{digest}/{name}.csv'
        # Archive file naming is discovered rather than assumed.
        retained = [p for p in archive.parent.rglob('*') if p.is_file() and p.suffix == '.csv']
        if not any(sha256(p) == digest for p in retained):
            raise ValueError(f'Retained content-addressed {name} snapshot missing/mismatched')
        sources[name] = {k: metadata[k] for k in ['source_url', 'resource_id', 'download_timestamp', 'sha256', 'rows']}
    if sha256(root / 'config/cnbs_semantics.json') != manifest['policy_sha256']:
        raise ValueError('Monthly semantics policy hash mismatch')
    with (root / MONTHLY).open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    markets, events = monthly_claims(rows)
    provenance_files = [MONTHLY, 'data/processed/cnbs/monthly/monthly_derivation_manifest.json',
        'config/cnbs_semantics.json', 'config/expected_behavior.json',
        'actuarial-engine/preprocessing/availability.py',
        'actuarial-engine/preprocessing/semantics.py', 'actuarial-engine/statistical/data.py',
        'actuarial-engine/expected_behavior/model.py']
    audit = {'status': 'CONDITIONALLY_READY_CURRENT_VINTAGE',
        'audit_execution_utc': datetime.now(timezone.utc).isoformat(),
        'observation_cutoff': CUTOFF, 'source_snapshot': sources,
        'file_sha256': {name: sha256(root/name) for name in provenance_files},
        'training_start': markets[0]['report_date'], 'training_end': markets[-1]['report_date'],
        'market_months': len(markets), 'institution_rows': len(events),
        'blocked_rows': sum(bool(r['exclusion_status']) for r in events),
        'negative_increments': sum(r['value'] is not None and r['value'] < 0 for r in events),
        'review_rows': sum(bool(r['quality_flags']) for r in events),
        'derivation_status_counts': dict(Counter(r['source_derivation_status'] for r in events)),
        'post_cutoff_rows_excluded': sum(r['report_date'] > CUTOFF for r in rows),
        'partial_market_periods': [{k:r[k] for k in ['report_date', 'value', 'contributing_institutions', 'excluded_codes', 'quality_flags']} for r in markets if r['excluded_institutions']],
        'negative_market_periods': sum(r['value'] < 0 for r in markets),
        'months_with_negative_contributors': sum(r['negative_contributors'] > 0 for r in markets),
        'composition_changes': [{k:r[k] for k in ['report_date', 'entered_codes', 'exited_codes']} for r in markets if r['entered_codes'] or r['exited_codes']],
        'largest_market_months': [{k:r[k] for k in ['report_date', 'value', 'quality_flags']} for r in sorted(markets, key=lambda r:r['value'], reverse=True)[:5]],
        'simulated_information_set_date_for_full_July_cutoff': availability_date(CUTOFF),
        'strict_point_in_time': 'NOT_VALIDATED', 'new_downloads': False}
    return audit, markets


def write_readiness(destination):
    audit, markets = source_audit()
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'data_readiness.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False)+'\n')
    top = audit['largest_market_months'][0]
    text = f'''# Forecasting data readiness — audit before model implementation

Status: **{audit['status']}**. Audit executed UTC: {audit['audit_execution_utc']}.

## Repository and source

The existing Python engine, scripts, configuration, tests, Next.js dashboard and deployment integrations remain unchanged. Research lives in `research/forecasting/` on a dedicated research branch. Production requirements are separate.

Original local raw CSVs and matching content-addressed copies ARE available. Their SHA-256 values match their 2026-10-03 download sidecars and the Phase 1.5 monthly derivation manifest. No data were downloaded. See `data_readiness.json` for exact URLs, IDs, timestamps and hashes.

Input: `{MONTHLY}`. It was produced by `scripts/derive_cnbs_monthly.py` / `preprocessing.semantics` under the existing CNBS semantics policy. January uses its reported balance; later months require the exact prior month in the same institution/line/currency. This study reads that guarded result and reuses existing normalization/eligible-market aggregation; it does not independently derive monthly values.

## Cutoff and quality

- Reporting-period cutoff: **{CUTOFF}**; {audit['market_months']} contiguous market months from {audit['training_start']}; {audit['institution_rows']} institution rows.
- {audit['post_cutoff_rows_excluded']} later institution rows excluded before normalization/aggregation. August 2026 amounts are not used for fitting, selection or final forecasts.
- {audit['blocked_rows']} blocked row; {audit['negative_increments']} negative institution increments; {audit['review_rows']} review/quality-flagged rows. Negatives are retained, not clipped or treated as accident counts.
- {len(audit['partial_market_periods'])} partial eligible-market period(s): {', '.join(r['report_date'] for r in audit['partial_market_periods'])}. The target is the **sum of eligible reported accounting increments**, not a reconstructed complete-market total. The missing institution is not treated as zero; contributor metadata is retained. This can affect forecasts.
- No missing market months and no market-month interpolation or zero filling. Missing institution months remain missing. Codes 0616/0618 are not merged; name changes remain flagged.
- Largest retained month: {top['report_date']}, HNL {top['value']:,.2f}. Unusual months (including November 2020) stay in training and evaluation; no event-based outlier removal.

## Timing: critical distinction

July observations are NOT asserted publicly available on July 31. Existing availability logic makes the full July information set eligible on **{availability_date(CUTOFF)}**. Exact CNBS release dates and earlier vintages remain unvalidated. The archived snapshot was downloaded October 3, after the requested observation cutoff.

The primary study will be a **current-vintage, reporting-cutoff conditional forecasting experiment**: simultaneous August–February projections conditioned on all report dates through July. It is not a deployable July-31 real-time forecast or the production anomaly replay. At actual execution in October 2026, the early target months are already past. A separate lag-aware July-31 sensitivity will train only on records admitted by the unchanged availability helper (through April) and bridge the missing May–July months without using their actual values.

## Decision before modeling

Proceed conditionally. Do not claim prospective accuracy, original-vintage availability or a complete legal-market total. Preserve all quality flags and source hashes. Block experiments if required files, matching provenance or contiguous usable market observations are absent. Missing raw snapshots must never be silently redownloaded.

Predeclare four models and July expanding-window origins before fitting. Use development origins 2021–2023 for selection, 2024–2025 for confirmation; seven simultaneous targets per origin, no monthly updating within a forecast. Small origin counts limit inference. Post-July-2026 values are not an evaluation set in this run.
'''
    (destination / 'data_readiness.md').write_text(text)
    return audit


if __name__ == '__main__':
    result = write_readiness(ROOT/'research/forecasting/reports')
    print(json.dumps({k:result[k] for k in ['status','market_months','blocked_rows','negative_increments','post_cutoff_rows_excluded','partial_market_periods','largest_market_months']}, indent=2))
