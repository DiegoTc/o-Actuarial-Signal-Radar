"""Focused static evidence charts from saved outputs only."""
import os
import tempfile
from datetime import date

os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='case-study-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from preprocessing.availability import availability_date
from case_studies.selection import series_key, key, shift_month, number


def create_case_charts(candidate, reference, all_rows, output_dir, cutoff):
    row = candidate['row']
    low, high = shift_month(row['report_date'], -24), shift_month(row['report_date'], 6)
    series = sorted([r for r in reference if series_key(r) == series_key(row) and low <= r['report_date'] <= high and r['availability_date'] <= cutoff], key=lambda r: r['report_date'])
    dates = [date.fromisoformat(r['report_date']) for r in series]
    signal_date = date.fromisoformat(row['report_date'])
    chart_dir = output_dir/'charts'
    chart_dir.mkdir(parents=True, exist_ok=True)
    currency = row['metric'] != 'claims_to_premiums_ratio'
    scale = 1e6 if currency else 1
    def values(field):
        return [None if number(r.get(field)) is None else number(r[field])/scale for r in series]
    def figure(label):
        fig, ax = plt.subplots(figsize=(11, 5.3), layout='constrained')
        ax.set_title(f"{row['metric']} | report {row['report_date']} | simulated availability {row['availability_date']}\n{label}", fontsize=11, pad=60)
        ax.axvline(signal_date, color='black', linestyle=':', linewidth=1)
        if dates[-1] > signal_date:
            ax.axvspan(signal_date, dates[-1], alpha=.06, color='gray', label='Later follow-up (unknown at signal)')
        ax.set_xlabel('report_date — accounting period end')
        ticks = [dates[i] for i in range(0, len(dates), 6)]
        ax.set_xticks(ticks, [d.isoformat() for d in ticks])
        ax.tick_params(axis='x', labelsize=8)
        top = ax.secondary_xaxis('top')
        top.set_xticks([mdates.date2num(d) for d in ticks], [availability_date(d.isoformat()) for d in ticks])
        top.set_xlabel('availability_date — corresponding simulated availability', fontsize=9)
        top.tick_params(labelsize=8)
        ax.grid(alpha=.2)
        return fig, ax
    def save(fig, suffix):
        fig.savefig(chart_dir/(candidate['id']+'_'+suffix+'.png'), dpi=130, metadata={'Software':'Actuarial Signal Radar — saved-output case studies'})
        plt.close(fig)
    fig, ax = figure('Observed vs expected')
    ax.plot(dates, values('observed_value'), label='Observed', linewidth=1.5)
    ax.plot(dates, values('expected_value'), label='Expected', linewidth=1.5)
    ax.set_ylabel('L millions' if currency else 'claims_to_premiums_ratio')
    ax.legend(fontsize=8)
    save(fig, 'observed_expected')
    fig, ax = figure('Signed residual = observed − expected')
    ax.plot(dates, values('residual'), color='tab:purple', marker='.', label='Residual')
    ax.axhline(0, color='black', linewidth=.6)
    ax.set_ylabel('L millions' if currency else 'Ratio deviation (not Lempiras)')
    ax.legend(fontsize=8)
    save(fig, 'residual')
    fig, ax = figure('Raw vs adjusted robust-z signals — 12-month detector window')
    levels = {'NORMAL':0, 'WATCH':1, 'ALERT':2}
    for field, label, marker in [('raw_signal_level','Raw','o'),('residual_signal_level','Adjusted','x')]:
        ax.plot(dates, [levels.get(r[field], float('nan')) for r in series], marker=marker, label=label, alpha=.8)
    ax.set_yticks([0,1,2], ['NORMAL','WATCH','ALERT'])
    ax.legend(fontsize=8)
    save(fig, 'signals')
    companion = {key(r): r for r in all_rows if r['baseline_method']=='cusum' and r['baseline_window']=='12'}
    fig, ax = figure('Saved residual CUSUM state — 12-month baseline')
    for field, label in [('residual_cusum_positive','Positive cumulative state'),('residual_cusum_negative','Negative cumulative state')]:
        ax.plot(dates, [number(companion.get(key(r), {}).get(field)) for r in series], label=label)
    ax.axhline(0, color='black', linewidth=.6)
    ax.set_ylabel('Cumulative standardized departure (not z-score)')
    ax.legend(fontsize=8)
    save(fig, 'cusum')
