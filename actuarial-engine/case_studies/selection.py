"""Explainable demo suitability, never an anomaly or causal score."""
import calendar
from datetime import date

from preprocessing.availability import availability_date


def number(value):
    return None if value in {'', None} else float(value)


def sign(value):
    return 0 if value is None or value == 0 else 1 if value > 0 else -1


def series_key(row):
    return row['analysis_level'], row['institution_code'], row['metric']


def key(row):
    return (*series_key(row), row['report_date'])


def primary_reference(rows):
    return [r for r in rows if r['baseline_method'] == 'robust_z' and r['baseline_window'] == '12' and not r.get('ewma_span')]


def extract_candidates(rows):
    """All adjusted ALERTs plus jointly scored raw-ALERT downgrade controls."""
    candidates = [r for r in primary_reference(rows) if r['residual_evaluation_status'] == 'scored' and
                  (r['residual_signal_level'] == 'ALERT' or
                   (r['raw_evaluation_status'] == 'scored' and r['raw_signal_level'] == 'ALERT'))]
    return sorted(candidates, key=key)


def shift_month(report_date, offset):
    dt = date.fromisoformat(report_date)
    year, month0 = divmod(dt.year * 12 + dt.month - 1 + offset, 12)
    return date(year, month0+1, calendar.monthrange(year, month0+1)[1]).isoformat()


def surrounding_periods(row, reference, before=3, after=3, cutoff=None):
    lookup = {r['report_date']: r for r in reference if series_key(r) == series_key(row)}
    output = []
    for offset in range(-before, after+1):
        period = shift_month(row['report_date'], offset)
        source = lookup.get(period)
        if source:
            item = dict(source, context_status='RECORDED', relative_month=offset)
        else:
            available = availability_date(period)  # reuse policy even for missing/censored placeholders
            item = {'report_date': period, 'availability_date': available, 'relative_month': offset,
                    'context_status': 'CENSORED_BY_CUTOFF' if cutoff and available > cutoff else 'MISSING_SOURCE_PERIOD'}
        item['known_by_signal_date'] = item['availability_date'] <= row['availability_date']
        output.append(item)
    return output


def raw_adjusted_classification(row):
    raw = row['raw_signal_level'] == 'ALERT'
    adjusted = row['residual_signal_level'] == 'ALERT'
    if raw and adjusted: return 'RAW_AND_ADJUSTED'
    if raw: return 'RAW_ONLY'
    if adjusted: return 'ADJUSTED_ONLY'
    return 'OTHER'


def paired_sensitivity(row, other, kind):
    if other is None or other.get('residual_evaluation_status') != 'scored':
        return 'NOT_ASSESSED', 'Missing or unscored saved counterfactual; not evidence of robustness.'
    base_score, other_score = number(row['residual_signal_score']), number(other['residual_signal_score'])
    same_sign = sign(base_score) == sign(other_score)
    residual = number(row['residual'])
    difference = abs(number(other['residual']) - residual) / max(abs(residual), 1e-12)
    unchanged = other['residual_signal_level'] == row['residual_signal_level'] and same_sign and difference <= .25
    moderate = same_sign and other['residual_signal_level'] in {'WATCH', 'ALERT'}
    if kind == 'cohort': label = 'ROBUST' if unchanged else 'PARTIALLY_ROBUST' if moderate else 'SENSITIVE'
    else: label = 'UNAFFECTED' if unchanged else 'MODERATELY_SENSITIVE' if moderate else 'HIGHLY_SENSITIVE'
    reason = f"Saved alternative={other['residual_signal_level']}; score={other_score:.6g}; relative residual change={difference:.2%}."
    return label, reason


def trailing_run(row, contexts, field):
    """Decision-time persistence only; never use T+1 in suitability."""
    expected_sign = sign(number(row['residual_signal_score']))
    run = 0
    for r in reversed([r for r in contexts if r['relative_month'] <= 0]):
        level = r.get(field + '_level', '')
        score = number(r.get(field + '_score'))
        if r['context_status'] != 'RECORDED' or level not in {'WATCH', 'ALERT'} or sign(score) != expected_sign:
            break
        run += 1
    return run


def suitability_scores(statistical, materiality, persistence, sensitivity, quality, narrative):
    values = [statistical, materiality, persistence, sensitivity, quality, narrative]
    if any(type(v) is not int or not 0 <= v <= 3 for v in values):
        raise ValueError('Suitability dimensions must be integers from 0 through 3')
    return dict(zip(['statistical_robustness', 'economic_materiality', 'persistence', 'sensitivity_robustness',
                     'data_quality_confidence', 'narrative_usefulness'], values))


def classify(total, adjusted, quality_risk, sensitivity_score, severe_sensitivity, coverage_complete, direct_negative=False):
    if not adjusted or direct_negative: return 'REJECTED_FOR_DEMO'
    if quality_risk == 'HIGH': return 'RESEARCH_ONLY'
    if severe_sensitivity: return 'RESEARCH_ONLY'
    if total >= 12 and coverage_complete and sensitivity_score == 3:
        return 'FLAGSHIP'
    if total >= 11: return 'SUPPORTING'
    return 'RESEARCH_ONLY'


def candidate_id(row):
    prefix = 'market' if row['analysis_level'] == 'market' else 'institution_' + row['institution_code']
    metric = {'monthly_claims': 'claims', 'monthly_premiums': 'premiums', 'claims_to_premiums_ratio': 'ratio'}[row['metric']]
    return prefix + '_' + metric + '_' + row['report_date'][:7].replace('-', '_')


def evaluate_candidate(row, reference, all_rows, alternatives, cutoff):
    context = surrounding_periods(row, reference, cutoff=cutoff)
    companions = {r['baseline_method']: r for r in all_rows if key(r) == key(row) and r['baseline_window'] == '12' and r['baseline_method'] in {'standard_z', 'cusum'}}
    for r in context:
        if r['context_status'] == 'RECORDED':
            same = {x['baseline_method']: x for x in all_rows if key(x) == key(r) and x['baseline_window'] == '12' and x['baseline_method'] == 'cusum'}
            c = same.get('cusum', {})
            r.update(cusum_level=c.get('residual_signal_level', ''), cusum_score=c.get('residual_signal_score', ''),
                     cusum_positive=c.get('residual_cusum_positive', ''), cusum_negative=c.get('residual_cusum_negative', ''))
    prior = [r for r in reference if series_key(r) == series_key(row) and r['report_date'] <= row['report_date'] and r['availability_date'] <= row['availability_date']]
    negative_prior = [r for r in prior if r['negative_review_sensitive'] == 'True']
    alternative_rows = {name: table.get(key(row)) for name, table in alternatives.items()}
    if row['analysis_level'] == 'market':
        cohort, cohort_reason = paired_sensitivity(row, alternative_rows['fixed_cohort_sensitivity'], 'cohort')
        negative, negative_reason = paired_sensitivity(row, alternative_rows['negative_fit_sensitivity'], 'negative')
        coverage_complete = all(x and x.get('residual_evaluation_status') == 'scored' for x in alternative_rows.values())
    else:
        cohort, cohort_reason = 'NOT_APPLICABLE', 'Market roster sensitivity does not alter independent institution series; portfolio composition is not assessed.'
        if not negative_prior:
            negative, negative_reason = 'UNAFFECTED', 'No negative-sensitive source observation in this institution/metric through the signal date; exclusion would remove no fitting inputs. Structural check, not a new model run.'
        else:
            negative, negative_reason = 'NOT_ASSESSED', 'Institution-level negative-fit counterfactual was not saved; source history contains negative-sensitive periods.'
        coverage_complete = False  # institution-level window/fit counterfactuals were not generated in Phase 3
    window_row = alternative_rows['trend_window_sensitivity']
    window_level = window_row['residual_signal_level'] or 'NOT_SCORED' if window_row else 'NOT_ASSESSED'
    window_reversal = bool(window_row and window_row.get('residual_evaluation_status') == 'scored' and
                           sign(number(window_row['residual_signal_score'])) != sign(number(row['residual_signal_score'])))
    severe = cohort == 'SENSITIVE' or negative == 'HIGHLY_SENSITIVE' or window_level == 'NORMAL' or window_reversal
    sensitive = cohort == 'PARTIALLY_ROBUST' or negative == 'MODERATELY_SENSITIVE' or window_level == 'WATCH'
    sensitivity_score = 0 if severe else 1 if sensitive else 3 if coverage_complete and cohort == 'ROBUST' and negative == 'UNAFFECTED' and window_level == 'ALERT' else 2 if negative == 'UNAFFECTED' else 1
    direct_negative = row['negative_review_sensitive'] == 'True'
    recent_negative = any(r.get('negative_review_sensitive') == 'True' for r in context if -3 <= r['relative_month'] < 0)
    unsafe = row['relative_deviation_status'] != 'safe' or row['model_status'] != 'modeled'
    composition_risk = 'material_composition_change' in row['composition_flags'] or any(number(row.get(k)) not in {None, 0} for k in ['excluded_institutions', 'premium_excluded_institutions', 'claims_excluded_institutions'])
    if direct_negative or unsafe or composition_risk or (row['analysis_level'] == 'institution' and recent_negative):
        risk, quality_score = 'HIGH', 0
    elif row['quality_flags'] or row['source_quality_flags'] or recent_negative:
        risk, quality_score = 'MEDIUM', 2
    else:
        risk, quality_score = 'LOW', 3
    direction = sign(number(row['residual_signal_score']))
    def agrees(method, levels):
        other = companions.get(method, {})
        return other.get('residual_evaluation_status') == 'scored' and other.get('residual_signal_level') in levels and sign(number(other.get('residual_signal_score'))) == direction
    adjusted = row['residual_signal_level'] == 'ALERT'
    statistical = 0 if not adjusted else 3 if agrees('standard_z', {'ALERT'}) and agrees('cusum', {'WATCH', 'ALERT'}) else 2 if agrees('standard_z', {'WATCH', 'ALERT'}) or agrees('cusum', {'WATCH', 'ALERT'}) else 1
    robust_run, cusum_run = trailing_run(row, context, 'residual_signal'), trailing_run(row, context, 'cusum')
    run = max(robust_run, cusum_run)
    persistence = min(3, max(0, run-1))
    view = raw_adjusted_classification(row)
    narrative = {'ADJUSTED_ONLY': 3, 'RAW_AND_ADJUSTED': 2, 'RAW_ONLY': 1, 'OTHER': 0}[view]
    dimensions = suitability_scores(statistical, {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(row['materiality_level'], 0), persistence, sensitivity_score, quality_score, narrative)
    total = sum(dimensions.values())
    classification = classify(total, adjusted, risk, sensitivity_score, severe, coverage_complete, direct_negative)
    reason = ('Raw-only downgrade control, not an adjusted anomaly flagship.' if not adjusted else
        'High source-quality risk or nearby negative-adjustment interpretation.' if risk == 'HIGH' else
        'Adjusted ALERT downgraded by a scored sensitivity.' if severe else
        'All saved market sensitivities retain direction and sufficient strength.' if classification == 'FLAGSHIP' else
        'Useful statistical contrast; institution counterfactual coverage is incomplete.' if row['analysis_level'] == 'institution' else
        'Limited corroboration, persistence, materiality or sensitivity robustness.')
    names = []
    for item in sorted(prior, key=lambda x: x['report_date']):
        if item['institution_name'] and (not names or names[-1]['institution_name'] != item['institution_name']):
            names.append({'report_date': item['report_date'], 'institution_name': item['institution_name']})
    return {'id': candidate_id(row), 'row': dict(row), 'companions': companions, 'context': context,
        'name_history_through_signal': names,
        'view_classification': view, 'cohort_robustness': cohort, 'cohort_reason': cohort_reason,
        'negative_adjustment_sensitivity': negative, 'negative_reason': negative_reason,
        'window_sensitivity_level': window_level, 'alternative_rows': alternative_rows,
        'counterfactual_coverage_complete': coverage_complete, 'data_quality_risk': risk,
        'direct_negative': direct_negative, 'recent_negative': recent_negative,
        'decision_time_robust_run': robust_run, 'decision_time_cusum_run': cusum_run,
        'score_dimensions': dimensions, 'suitability': total, 'classification': classification,
        'selection_reason': reason, 'selected': False}


def select_shortlist(candidates):
    """At most two markets and two distinct institutions; no fabricated minimum."""
    ranked = sorted(candidates, key=lambda c: (-c['suitability'], -c['score_dimensions']['statistical_robustness'],
        -c['score_dimensions']['data_quality_confidence'], -c['score_dimensions']['narrative_usefulness'],
        -abs(number(c['row']['residual_signal_score']) or 0), c['id']))
    markets = [c for c in ranked if c['classification'] == 'FLAGSHIP' and c['row']['analysis_level'] == 'market'][:2]
    institutions = []
    for c in ranked:
        if c['row']['analysis_level'] == 'institution' and c['classification'] in {'FLAGSHIP', 'SUPPORTING'} and c['row']['institution_code'] not in {x['row']['institution_code'] for x in institutions}:
            institutions.append(c)
            if len(institutions) == 2: break
    chosen = markets + institutions
    for c in chosen: c['selected'] = True
    return chosen, ranked
