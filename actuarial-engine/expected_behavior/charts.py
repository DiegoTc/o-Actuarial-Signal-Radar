"""Static report artifacts; economic and simulated availability axes are explicit."""
import os
import tempfile
from datetime import date

from expected_behavior.reporting import primary


def create_charts(scenarios, report_dir):
    # Keep font caches outside project artifacts and make plotting headless.
    with tempfile.TemporaryDirectory() as cache:
        os.environ['MPLCONFIGDIR'] = cache
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams.update({'font.size': 9, 'figure.dpi': 110})
        chart_dir = report_dir / 'charts'
        chart_dir.mkdir(parents=True, exist_ok=True)
        rows = primary(scenarios['primary_dynamic'], 'market')
        def series(metric, scenario='primary_dynamic'):
            return sorted([r for r in primary(scenarios[scenario], 'market') if r['metric'] == metric], key=lambda r: r['report_date'])
        def dates(rs, field='report_date'):
            return [date.fromisoformat(r[field]) for r in rs]
        def numbers(rs, field):
            return [r[field] if r[field] is not None else float('nan') for r in rs]
        def finish(fig, filename, axis_note='Economic axis: report_date. Availability: first day of third following calendar month.'):
            fig.text(.01, .01, axis_note + '\nLagged retrospective backtest; strict point-in-time NOT VALIDATED.', fontsize=8)
            fig.tight_layout(rect=(0, .08, 1, 1))
            fig.savefig(chart_dir / filename, metadata={'Software': 'Actuarial Signal Radar Phase 3'})
            plt.close(fig)
        for metric, short in [('monthly_premiums', 'premiums'), ('monthly_claims', 'claims'), ('claims_to_premiums_ratio', 'ratio')]:
            rs = series(metric)
            fig, ax = plt.subplots(figsize=(11, 4))
            ax.plot(dates(rs), numbers(rs, 'observed_value'), label='Observed', linewidth=1)
            ax.plot(dates(rs), numbers(rs, 'expected_value'), label='Prior-only expected', linewidth=1.4)
            ax.set(title=f'Market {metric}: observed vs expected', xlabel='report_date', ylabel='Ratio points' if short == 'ratio' else 'Lempiras')
            ax.legend(); ax.grid(alpha=.2)
            finish(fig, 'claims_to_premiums_observed_vs_expected.png' if short == 'ratio' else f'observed_vs_expected_{short}.png')
            if short != 'ratio':
                fig, ax = plt.subplots(figsize=(11, 4))
                ax.plot(dates(rs), numbers(rs, 'residual'), label='Observed minus expected', linewidth=1)
                ax.axhline(0, color='black', linewidth=.6)
                ax.set(title=f'Market {short} residuals', xlabel='report_date', ylabel='Signed Lempiras')
                ax.grid(alpha=.2)
                finish(fig, f'residual_{short}.png')
        rs = series('monthly_claims')
        fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
        mapping = {'NORMAL': 0, 'WATCH': 1, 'ALERT': 2}
        for ax, view in zip(axes, ['raw', 'residual']):
            y = [mapping.get(r[view + '_signal_level'], float('nan')) for r in rs]
            ax.scatter(dates(rs, 'availability_date'), y, s=18, color='steelblue' if view == 'raw' else 'darkorange')
            ax.set(title=f'Claims {view}: robust z / 12-month detector', yticks=[0, 1, 2], yticklabels=['NORMAL', 'WATCH', 'ALERT'])
            ax.grid(alpha=.2)
        axes[-1].set_xlabel('Simulated availability_date')
        finish(fig, 'raw_vs_adjusted_signal_timeline.png', 'Signal axis: availability_date; report periods remain in the paired CSV.')
        fig, ax = plt.subplots(figsize=(9, 5))
        palette = {'HIGH': 'firebrick', 'MEDIUM': 'darkorange', 'LOW': 'steelblue', '': 'gray'}
        for level in ['LOW', 'MEDIUM', 'HIGH', '']:
            subset = [r for r in rows if r['metric'] != 'claims_to_premiums_ratio' and r['residual_signal_score'] is not None and r['materiality_level'] == level]
            ax.scatter([abs(r['residual_signal_score']) for r in subset], [abs(r['residual']) / 1e6 for r in subset], color=palette[level], label=level or 'Unclassified', alpha=.7, s=22)
        ax.set(title='Market monetary deviations: statistical score vs impact', xlabel='Absolute residual robust z (12-month detector)', ylabel='Absolute deviation (million Lempiras)')
        ax.legend(title='Exploratory materiality'); ax.grid(alpha=.2)
        finish(fig, 'materiality_vs_statistical_signal.png', 'Each point is a report period eligible by the cutoff; paired CSV provides report_date and availability_date.')
        fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
        for name, label in [('primary_dynamic', 'Dynamic eligible market'), ('fixed_cohort_sensitivity', 'Fixed ex-post cohort')]:
            rs = series('monthly_claims', name)
            axes[0].plot(dates(rs), numbers(rs, 'observed_value'), label=label, linewidth=1)
            axes[1].plot(dates(rs), numbers(rs, 'residual'), label=label, linewidth=1)
        axes[0].set(title='Claims: cohort sensitivity (fixed selection uses hindsight)', ylabel='Observed Lempiras')
        axes[1].set(ylabel='Residual Lempiras', xlabel='report_date')
        for ax in axes: ax.legend(); ax.grid(alpha=.2)
        finish(fig, 'fixed_vs_dynamic_cohort.png')
        return sorted(chart_dir.glob('*.png'))
