"""Matched-comparison reporting, never interpreting lack of warm-up as NORMAL."""
from collections import Counter, defaultdict

from ingestion.cnbs import atomic_write, write_json
from statistical.reporting import table
from statistical.methods import month_number


def primary(rows, level=None):
    return [r for r in rows if r['baseline_method'] == 'robust_z' and r['baseline_window'] == 12 and
            (level is None or r['analysis_level'] == level)]


def identity(r):
    return (r['analysis_level'], r['resource'], r['institution_code'], r['report_date'],
            r['baseline_method'], r['baseline_window'], r['ewma_span'])


def matched_comparison(rows, first, second):
    common = [r for r in rows if r[first + '_evaluation_status'] == 'scored' and r[second + '_evaluation_status'] == 'scored']
    alerts = [r for r in common if r[first + '_signal_level'] == 'ALERT']
    return {'matched_observations': len(common), 'first_alerts': len(alerts),
        'alerts_remaining': sum(r[second + '_signal_level'] == 'ALERT' for r in alerts),
        'alerts_downgraded_watch': sum(r[second + '_signal_level'] == 'WATCH' for r in alerts),
        'alerts_now_normal': sum(r[second + '_signal_level'] == 'NORMAL' for r in alerts),
        'hidden_adjusted_alerts': sum(r[first + '_signal_level'] == 'NORMAL' and r[second + '_signal_level'] == 'ALERT' for r in common),
        'not_jointly_scored': len(rows) - len(common)}


def ranked(rows, limit=10):
    return sorted([r for r in rows if r['residual_signal_score'] is not None],
        key=lambda r: (-abs(r['residual_signal_score']), r['report_date'], r['resource'], r['institution_code']))[:limit]


def signal_table(rows):
    return table(['Level', 'Metric', 'Code', 'Report date', 'Availability', 'Observed', 'Expected', 'Residual', 'Residual robust z', 'Raw', 'Adjusted', 'Materiality', 'Composition'],
        [[r[k] for k in ['analysis_level', 'metric', 'institution_code', 'report_date', 'availability_date', 'observed_value',
          'expected_value', 'residual', 'residual_signal_score', 'raw_signal_level', 'residual_signal_level', 'materiality_level', 'composition_flags']] for r in rows])


def sensitivity(reference, alternative):
    lookup = {identity(r): r for r in primary(alternative, 'market')}
    paired = [(r, lookup[identity(r)]) for r in primary(reference, 'market') if identity(r) in lookup and
              r['residual_evaluation_status'] == 'scored' and lookup[identity(r)]['residual_evaluation_status'] == 'scored']
    alerts = [(a, b) for a, b in paired if a['residual_signal_level'] == 'ALERT']
    return {'jointly_scored': len(paired), 'reference_alerts': len(alerts),
        'alerts_retained': sum(b['residual_signal_level'] == 'ALERT' for a, b in alerts),
        'alerts_downgraded': sum(b['residual_signal_level'] != 'ALERT' for a, b in alerts),
        'new_alerts': sum(a['residual_signal_level'] != 'ALERT' and b['residual_signal_level'] == 'ALERT' for a, b in paired),
        'level_agreement': sum(a['residual_signal_level'] == b['residual_signal_level'] for a, b in paired),
        'reference_unmatched_or_unscored': len(primary(reference, 'market')) - len(paired)}


def sensitivity_signal_table(reference, alternative):
    lookup = {identity(r): r for r in primary(alternative, 'market')}
    rows = []
    for r in ranked([r for r in primary(reference, 'market') if r['residual_signal_level'] == 'ALERT'], 15):
        other = lookup.get(identity(r))
        rows.append([r['metric'], r['report_date'], r['availability_date'], r['residual_signal_score'],
            r['residual_signal_level'], other['residual_signal_level'] or 'NOT_SCORED' if other else 'MISSING',
            other['residual_evaluation_status'] if other else 'MISSING',
            r['materiality_level']])
    return table(['Metric', 'Report date', 'Availability', 'Reference score', 'Reference', 'Alternative', 'Alternative status', 'Reference materiality'], rows)


def report_results(scenarios, config, manifest, report_dir):
    base = scenarios['primary_dynamic']
    reference = primary(base)
    summary = {'replay_mode': 'LAGGED_RETROSPECTIVE_BACKTEST', 'strict_point_in_time': 'NOT_VALIDATED',
        'evaluation_end': manifest['evaluation_end'], 'comparisons': {}, 'scenario_counts': {}, 'sensitivities': {},
        'top_market_signals': ranked(primary(base, 'market')), 'top_institution_signals': ranked(primary(base, 'institution')),
        'materiality_counts': {}, 'detector_comparison': []}
    intro = ('Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.\n\n'
        'Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; '
        'trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. '
        'No historical events were used to fit thresholds.\n\n')
    compare_rows = []
    for level in ['market', 'institution']:
        for first, second in [('raw', 'trend'), ('trend', 'residual'), ('raw', 'residual')]:
            result = matched_comparison(primary(base, level), first, second)
            summary['comparisons'][level + '/' + first + '_to_' + second] = result
            compare_rows.append([level, first + ' -> ' + second, *result.values()])
    compare_table = table(['Level', 'Comparison', 'Jointly scored', 'Original ALERT', 'Remain ALERT', 'Now WATCH', 'Now NORMAL', 'Hidden ALERT', 'Unmatched/unscored'], compare_rows)
    for name, rows in scenarios.items():
        subset = primary(rows)
        summary['scenario_counts'][name] = {'rows_all_methods': len(rows), 'reference_rows': len(subset),
            'model_status': dict(Counter(r['model_status'] for r in subset)),
            'adjusted_levels': dict(Counter(r['residual_signal_level'] or 'NOT_SCORED' for r in subset))}
    for name in ['fixed_cohort_sensitivity', 'negative_fit_sensitivity', 'trend_window_sensitivity']:
        summary['sensitivities'][name] = sensitivity(base, scenarios[name])
    unique = reference
    modeled = [r for r in unique if r['model_status'] == 'modeled']
    scored = [r for r in unique if r['residual_evaluation_status'] == 'scored']
    dates = sorted({r['availability_date'] for r in unique})
    summary['first_availability_date'] = dates[0] if dates else None
    summary['last_availability_date'] = dates[-1] if dates else None
    summary['first_expected_availability_date'] = min((r['availability_date'] for r in modeled), default=None)
    summary['first_residual_scored_availability_date'] = min((r['availability_date'] for r in scored), default=None)
    for level in ['market', 'institution']:
        subset = [r for r in scored if r['analysis_level'] == level]
        summary['materiality_counts'][level] = dict(Counter(r['materiality_level'] or 'NOT_CLASSIFIED' for r in subset if r['residual_signal_level'] == 'ALERT'))
    summary_text = '# Expected behavior summary\n\n' + intro
    summary_text += table(['Measure', 'Value'], [[k, summary[k]] for k in ['evaluation_end', 'first_availability_date', 'last_availability_date', 'first_expected_availability_date', 'first_residual_scored_availability_date']])
    summary_text += '\n\n## Trend and seasonal adjustment effects\n\n' + compare_table
    summary_text += ('\n\nA downgrade is counted only when both compared views are scored. Warm-up, zero scale and missing forecasts are never counted as disappearing signals. '
        'Trend-only and full-adjustment comparisons have different common samples; their reductions cannot be added. '
        'A raw ALERT becoming adjusted NORMAL is consistent with the chosen model accounting for some variation; it does not establish growth or seasonality as the actual cause.\n\n')
    summary_text += table(['Scenario', 'All-method rows', 'Primary-reference rows', 'Model statuses', 'Adjusted levels'],
        [[name, *counts.values()] for name, counts in summary['scenario_counts'].items()])
    summary_text += '\n\n## Strongest market residual signals\n\n' + signal_table(summary['top_market_signals'])
    summary_text += '\n\n## Strongest institution residual signals\n\n' + signal_table(summary['top_institution_signals'])
    summary_text += ('\n\nSee [methodology](../../docs/expected-behavior-methodology.md), [raw/adjusted comparison](raw_vs_adjusted_signals.md), '
        '[seasonality](seasonality_analysis.md), [trend](trend_analysis.md), [materiality](materiality_analysis.md), '
        '[cohorts](cohort_sensitivity.md) and [negative adjustments](negative_adjustment_sensitivity.md). '
        'Isolation Forest is deferred: deterministic residual modeling and its sensitivities are the focus. No causal or production-performance claims are established.\n')
    raw_adjusted = '# Raw versus adjusted signals\n\n' + intro + compare_table
    raw_adjusted += '\n\n## Raw ALERT, adjusted NORMAL (matched primary reference)\n\n'
    disappeared = [r for r in reference if r['raw_evaluation_status'] == r['residual_evaluation_status'] == 'scored' and
                   r['raw_signal_level'] == 'ALERT' and r['residual_signal_level'] == 'NORMAL']
    raw_adjusted += signal_table(sorted(disappeared, key=lambda r: (-abs(r['raw_signal_score']), r['availability_date']))[:15])
    raw_adjusted += '\n\nThese are model-consistent adjustments, not proof of a seasonal or growth cause.\n\n## Raw NORMAL, adjusted ALERT\n\n'
    hidden = [r for r in reference if r['raw_evaluation_status'] == r['residual_evaluation_status'] == 'scored' and
              r['raw_signal_level'] == 'NORMAL' and r['residual_signal_level'] == 'ALERT']
    raw_adjusted += signal_table(ranked(hidden, 15))
    raw_adjusted += '\n\n## Residual detector stability\n\n'
    grouped = defaultdict(list)
    for r in base:
        if r['analysis_level'] == 'market': grouped[(r['baseline_method'], r['baseline_window'], r['ewma_span'])].append(r)
    comparisons = []
    for method, rows in sorted(grouped.items(), key=lambda x: str(x[0])):
        scored_rows = [r for r in rows if r['residual_evaluation_status'] == 'scored']
        c = Counter(r['residual_signal_level'] for r in scored_rows)
        pairs, switches = 0, 0
        by_metric = defaultdict(list)
        for r in scored_rows: by_metric[r['metric']].append(r)
        for values in by_metric.values():
            values.sort(key=lambda r: r['report_date'])
            for a, b in zip(values, values[1:]):
                if month_number(b['report_date']) - month_number(a['report_date']) == 1:
                    pairs += 1; switches += a['residual_signal_level'] != b['residual_signal_level']
        result = {'method': method[0], 'window': method[1], 'span': method[2], 'scored': len(scored_rows),
            'normal': c['NORMAL'], 'watch': c['WATCH'], 'alert': c['ALERT'],
            'alert_fraction': c['ALERT'] / len(scored_rows) if scored_rows else None,
            'signal_switch_fraction': switches / pairs if pairs else None}
        summary['detector_comparison'].append(result); comparisons.append(list(result.values()))
    raw_adjusted += table(['Method', 'Window', 'Span', 'Scored', 'NORMAL', 'WATCH', 'ALERT', 'Alert fraction', 'Switch fraction'], comparisons)
    raw_adjusted += ('\n\nSwitch fraction measures level changes between consecutive scored same-series months. Lower turnover is not accuracy. '
        'Different windows have unequal warm-up. Robust 12-month residual z is an interpretable reference; CUSUM adds persistent-shift context. '
        'On the reference 12-month scale, CUSUM has the lowest observed switch fraction in this run, but fewer alerts and lower turnover do not demonstrate higher accuracy. Neither has validated actuarial performance. Keep raw signals and materiality alongside them.\n')
    seasonal_rows = []
    for metric in sorted({r['metric'] for r in primary(base, 'market')}):
        for month in range(1, 13):
            values = [r for r in primary(base, 'market') if r['metric'] == metric and int(r['report_date'][5:7]) == month and r['model_status'] == 'modeled']
            if values:
                latest = max(values, key=lambda r: r['report_date'])
                seasonal_rows.append([metric, month, latest['report_date'], latest['availability_date'], latest['seasonal_history_count'], latest['seasonal_effect']])
    seasonality = '# Seasonality analysis\n\n' + intro
    seasonality += ('Additive month-of-year effect = median of prior same-month prequential trend innovations. '
        'Each historical innovation used a trend estimated before that observation. At least two prior-year same-month innovations are required; '
        'lookback is six years. No centered smoothing, future March values, global seasonal fit or zero-imputed seasonal effect is used. '
        'Multiplicative seasonality is intentionally unsupported because negative/near-zero accounting amounts complicate ratio-based scaling.\n\n')
    seasonality += table(['Metric', 'Month', 'Latest report', 'Availability', 'Prior same-month samples', 'Effect'], seasonal_rows)
    seasonality += '\n\n## Additional adjustment after trend-only modeling\n\n' + compare_table + '\n\nThe table describes matched signals, not a causal decomposition.\n'
    trend = '# Trend analysis\n\n' + intro
    trend += (f"Default: {config['trend_method']}, {config['trend_window']}-month calendar window, at least {config['minimum_trend_history']} usable prior observations. "
        'Trailing mean and trailing linear projection are configurable alternatives. No centered windows are used. Partial trend histories receive explicit flags; missing observations are not filled. '
        'The 24-month sensitivity retains the same 75% minimum coverage fraction (18 prior observations).\n\n')
    trend += compare_table + '\n\n## Trend-window sensitivity (market, jointly scored robust 12-month residual reference)\n\n'
    trend += table(['Measure', 'Value'], summary['sensitivities']['trend_window_sensitivity'].items())
    trend += '\n\n' + sensitivity_signal_table(base, scenarios['trend_window_sensitivity'])
    materiality = '# Economic materiality analysis\n\n' + intro
    materiality += ('Exploratory bands use only prior available absolute modeled residuals from the same series: MEDIUM at the prior 75th percentile, '
        'HIGH at the prior 95th percentile, LOW below the medium band (zero deviation always LOW). At least 12 prior residuals in the previous 36 calendar months are required. '
        'Percentiles are empirical nearest-rank estimates. These bands are relative historical-impact rankings, not validated currency budgets or cross-institution capital thresholds. '
        'Signed Lempira deviation is reported separately for monetary measures; ratio deviations are ratio points and are never labeled Lempiras.\n\n')
    materiality += table(['Level', 'Adjusted ALERT materiality counts'], summary['materiality_counts'].items())
    materiality += '\n\n## Strong adjusted market deviations and amounts\n\n' + signal_table(summary['top_market_signals'])
    materiality += '\n\nA large statistical score need not have HIGH materiality. Warm-up may prevent materiality classification even when a detector can score; neither status is silently filled.\n'
    cohort = '# Market cohort sensitivity\n\n' + intro
    cohort += ('Dynamic eligible reporters are the primary market. Fixed complete-history cohort: `' + ', '.join(config['fixed_cohort_codes']) + '`. '
        'These ten codes were identified in Phase 1.5; selection uses full-history completeness and therefore introduces hindsight/survivorship bias. '
        'Fixed-cohort findings are sensitivity results only and never influence dynamic expectations or thresholds. Neither cohort bridges 0616 to 0618. '
        'Contributor counts, exclusions and prior-roster mismatch are retained. A roster symmetric-difference/union fraction of at least 10% flags material composition change.\n\n')
    cohort += table(['Measure', 'Value'], summary['sensitivities']['fixed_cohort_sensitivity'].items())
    cohort += '\n\n## Major-signal agreement\n\n' + sensitivity_signal_table(base, scenarios['fixed_cohort_sensitivity'])
    cohort += '\n\nAgreement/disagreement is measured on jointly scored matched periods only. Unmatched periods are not evidence that a signal disappeared. See fixed_vs_dynamic_cohort.png under charts/.\n'
    negative = '# Negative accounting adjustment sensitivity\n\n' + intro
    negative += ('Both runs retain and evaluate all negative amounts. The alternative excludes negative-review-sensitive observations from trend, seasonal and materiality fitting only; '
        'residual detectors continue evaluating and retaining all modeled residuals. For market totals/ratios, a period with any negative contributor is excluded from expected-model fitting, even if its total is positive. '
        'This conservative period-level choice is explicitly broader than dropping a negative aggregate. It can reduce model availability and is not declared correct.\n\n')
    negative += table(['Measure', 'Value'], summary['sensitivities']['negative_fit_sensitivity'].items())
    negative += '\n\n## Major-signal agreement\n\n' + sensitivity_signal_table(base, scenarios['negative_fit_sensitivity'])
    negative += '\n\n## Warm-up/status differences\n\n' + table(['Scenario', 'Model statuses', 'Reference adjusted levels'],
        [[name, summary['scenario_counts'][name]['model_status'], summary['scenario_counts'][name]['adjusted_levels']] for name in ['primary_dynamic', 'negative_fit_sensitivity']])
    for name, content in [('expected_behavior_summary.md', summary_text), ('raw_vs_adjusted_signals.md', raw_adjusted),
        ('seasonality_analysis.md', seasonality), ('trend_analysis.md', trend), ('materiality_analysis.md', materiality),
        ('cohort_sensitivity.md', cohort), ('negative_adjustment_sensitivity.md', negative)]:
        atomic_write(report_dir / name, (content + '\n').encode())
    write_json(report_dir / 'summary.json', summary)
    return summary
