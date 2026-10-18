"""Synthetic fixtures stay in disposable test folders; no fabricated research outcomes."""
import copy
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from research.forecasting.audit import sha256
from research.forecasting.monitoring.src import evaluation as ev
from research.forecasting.monitoring.src import snapshots as ss
from research.forecasting.monitoring.src.cli import download, plan, safe_output


def raw_rows(values=None):
    values=values or [('2026-06-30','60'),('2026-07-31','100'),('2026-08-31','90')]
    return [{'Fecha Reporte':d,'CodInstitucion':'0601','Institucion':'Synthetic test insurer',
             'RamoPadre':'Seguros Generales','Ramo':'Vehículos Automotores','CodMoneda':'1','Moneda':'Nacional','Saldo':v}
            for d,v in values]


def payload(rows):
    f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return f.getvalue().encode()


def register_test(tmp_path,name='synthetic-fixture',rows=None):
    incoming=tmp_path/f'incoming-{name}';incoming.mkdir()
    data=payload(rows or raw_rows())
    (incoming/'raw.csv').write_bytes(data)
    receipt=dict(resource_id=ss.CONFIG['resource_id'],source_url=ss.CONFIG['source_url'],
                 sha256=hashlib.sha256(data).hexdigest(),file_size=len(data),http_status=200,
                 download_timestamp='2026-10-03T16:41:14+00:00',fixture='SYNTHETIC_UNIT_TEST_ONLY')
    ss.dump_json(incoming/'receipt.json',receipt)
    ss.dump_json(incoming/'metadata.json',dict(success=True,result=dict(resources=[dict(id=ss.CONFIG['resource_id'],url=ss.CONFIG['source_url'])])))
    registry=ss.register(incoming/'raw.csv',incoming/'receipt.json',incoming/'metadata.json',name,
                         raw_root=tmp_path/'ignored-test-store',registry=tmp_path/'test-registry')
    return registry,incoming


def snapshot_info(download='2026-10-03T16:41:14+00:00'):
    return dict(snapshot_id='synthetic',raw_sha256='0'*64,download_timestamp=download)


def market_row(value='150000000',date='2026-08-31',flags=''):
    return dict(report_date=date,observed_value_HNL=value,quality_flags=flags,
                contributing_institutions='1',contributor_codes='0601')


def test_frozen_research_is_preserved():
    refs=ev.frozen_references()
    assert refs
    assert len(ev.forecasts())==7
    assert ev.forecasts()[0]['point_forecast_HNL']=='157402825.05'


def test_missing_outcomes_are_null_not_zero():
    rows=ev.compare(ev.forecasts(),[],snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    assert len(rows)==7 and all(r['observed_value_HNL'] is None for r in rows)
    assert all(r['absolute_error_HNL'] is None and r['inside_95'] is None for r in rows)
    m=ev.summaries(rows)['receipt_based_metrics']
    assert m['n']==0 and m['MAE_HNL'] is None and m['coverage_95'] is None


def test_exact_month_matching_and_zero_is_observed():
    rows=ev.compare(ev.forecasts(),[market_row('0')],snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    assert rows[0]['observed_value_HNL']=='0' and rows[1]['observed_value_HNL'] is None
    assert rows[0]['percentage_error'] is None and rows[0]['absolute_error_HNL']=='157402825.05'
    m=ev.summaries(rows)['receipt_based_metrics']
    assert m['n']==1 and m['WAPE_pct'] is None


@pytest.mark.parametrize('date',['2026-08-01','2026-08-30'])
def test_non_month_end_is_rejected(date):
    with pytest.raises(ValueError,match='month-end'):
        ev.compare(ev.forecasts(),[market_row(date=date)],snapshot_info(),[],'2026-10-18T02:00:00+00:00')


def test_duplicate_market_month_cannot_silently_override():
    with pytest.raises(ValueError,match='Duplicate market'):
        ev.compare(ev.forecasts(),[market_row(),market_row('20')],snapshot_info(),[],'2026-10-18T02:00:00+00:00')


def test_receipt_comparison_does_not_change_simulated_lag():
    rows=ev.compare(ev.forecasts(),[market_row()],snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    assert rows[0]['simulated_outcome_eligibility_date']=='2026-11-01'
    assert rows[0]['actual_source_publication_date'] is None
    assert rows[0]['target_timing_category']=='RETROSPECTIVE_BEFORE_INFORMATION_SET'
    s=ev.summaries(rows)
    assert s['receipt_based_metrics']['n']==1 and s['simulated_lag_eligible_metrics']['n']==0


def test_snapshot_downloaded_after_asof_cannot_leak_outcome():
    rows=ev.compare(ev.forecasts(),[market_row('1e30')],snapshot_info('2026-10-19T00:00:00+00:00'),[],
                    '2026-10-18T02:00:00+00:00')
    assert rows[0]['observed_value_HNL'] is None
    assert rows[0]['monitoring_status']=='SNAPSHOT_NOT_YET_RETRIEVED'


def test_cannot_backdate_to_july_forecast():
    with pytest.raises(ValueError,match='predate actual forecast'):
        ev.compare(ev.forecasts(),[],snapshot_info(),[],'2026-07-31T23:59:59+00:00')


def test_periods_not_completed_do_not_become_observed():
    rows=ev.compare(ev.forecasts(),[market_row('999',date='2027-02-28')],snapshot_info(),[],
                    '2026-10-18T02:00:00+00:00')
    assert rows[-1]['observed_value_HNL'] is None and rows[-1]['monitoring_status']=='TARGET_PERIOD_NOT_ENDED'


def test_negative_actuals_and_quality_flags_remain():
    rows=ev.compare(ev.forecasts(),[market_row('-10',flags='market_partial_coverage;negative_increment_review')],
                    snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    assert rows[0]['observed_value_HNL']=='-10'
    assert 'market_partial_coverage' in rows[0]['accounting_quality_warnings']
    assert 'negative_market_increment_retained' in rows[0]['accounting_quality_warnings']


def test_interval_bounds_are_inclusive():
    f=ev.forecasts()
    rows=ev.compare(f,[market_row(f[0]['upper_95_HNL'])],snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    assert rows[0]['inside_95'] is True and rows[0]['inside_80'] is False


def test_error_metric_formulas():
    rows=[dict(observed_value_HNL='10',signed_error_HNL='-2',inside_80=True,inside_95=True),
          dict(observed_value_HNL='20',signed_error_HNL='4',inside_80=False,inside_95=True),
          dict(observed_value_HNL=None)]
    m=ev.metrics(rows)
    assert m['n']==2 and m['missing_targets']==1
    assert m['MAE_HNL']==3 and m['RMSE_HNL']==pytest.approx(10**.5)
    assert m['WAPE_pct']==20 and m['bias_HNL']==1 and m['coverage_80']==.5


def test_comparison_does_not_mutate_forecasts():
    f=ev.forecasts();before=copy.deepcopy(f)
    ev.compare(f,[market_row()],snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    assert f==before


def test_registration_keeps_bytes_and_provenance(tmp_path):
    registry,incoming=register_test(tmp_path)
    manifest,folder=ss.verify_snapshot(registry)
    assert (folder/'raw.csv').read_bytes()==(incoming/'raw.csv').read_bytes()
    assert manifest['download_timestamp']=='2026-10-03T16:41:14+00:00'
    assert manifest['publication_status']=='UNRESOLVED'
    assert manifest['registered_utc']!=manifest['download_timestamp']


def test_negative_derivation_and_missing_prior_are_preserved(tmp_path):
    registry,_=register_test(tmp_path);m,p=ss.verify_snapshot(registry)
    rows=ss.read_market(p)
    assert rows[0]['observed_value_HNL']==''
    assert rows[-1]['observed_value_HNL']=='-10'
    assert m['negative_increments']==1 and m['blocked_rows']==1


def test_raw_sha_tampering_is_detected(tmp_path):
    registry,_=register_test(tmp_path);_,p=ss.verify_snapshot(registry)
    with (p/'raw.csv').open('ab') as f:f.write(b'changed')
    with pytest.raises(ValueError,match='checksum'):
        ss.verify_snapshot(registry)


def test_registry_cannot_override_identity(tmp_path):
    registry,_=register_test(tmp_path);m=json.loads(registry.read_text());m['download_timestamp']='2026-10-04T00:00:00+00:00'
    registry.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='disagrees'):
        ss.verify_snapshot(registry)


def test_snapshot_overwrite_is_refused(tmp_path):
    registry,incoming=register_test(tmp_path)
    with pytest.raises(ValueError,match='Snapshot exists'):
        ss.register(incoming/'raw.csv',incoming/'receipt.json',incoming/'metadata.json','synthetic-fixture',
                    raw_root=tmp_path/'ignored-test-store',registry=tmp_path/'test-registry')


@pytest.mark.parametrize('field,value',[('sha256','bad'),('resource_id','wrong'),('source_url','https://example.com/data'),
                                       ('download_timestamp','2026-10-03'),('http_status',404)])
def test_bad_receipts_stop_before_registration(tmp_path,field,value):
    _,incoming=register_test(tmp_path)
    receipt=json.loads((incoming/'receipt.json').read_text());receipt[field]=value
    ss.dump_json(incoming/'bad-receipt.json',receipt)
    with pytest.raises(ValueError):
        ss.register(incoming/'raw.csv',incoming/'bad-receipt.json',incoming/'metadata.json','other',
                    raw_root=tmp_path/'ignored-test-store',registry=tmp_path/'test-registry')


def test_schema_missing_field_is_rejected():
    rows=raw_rows()
    for r in rows:del r['Saldo']
    with pytest.raises(ValueError,match='Required source columns missing'):
        ss.derive(payload(rows))


def test_identical_bytes_are_not_revision_evidence(tmp_path):
    a,_=register_test(tmp_path,'copy-one');b,_=register_test(tmp_path,'copy-two')
    result=ss.revision_report(a,b)
    assert result['status']=='IDENTICAL_BYTES_NOT_A_DISTINCT_VINTAGE'
    assert result['changes']==[] and result['monthly_changes']==[]


def test_revision_propagates_to_next_month_without_mutating_snapshots(tmp_path):
    a,_=register_test(tmp_path,'before')
    b,_=register_test(tmp_path,'after',raw_rows([('2026-06-30','60'),('2026-07-31','110'),('2026-08-31','90')]))
    result=ss.revision_report(a,b)
    assert result['status']=='DISTINCT_RETAINED_BYTES_COMPARED'
    assert [r['change_type'] for r in result['changes']]==['AMOUNT_REVISION']
    changes={r['report_date']:r for r in result['monthly_changes']}
    assert Decimal(changes['2026-07-31']['difference_HNL'])==10
    assert Decimal(changes['2026-08-31']['difference_HNL'])==-10
    assert all('observed_snapshot_revision_sensitive' in r['quality_flags'] for r in changes.values())
    ss.verify_snapshot(a);ss.verify_snapshot(b)


def test_december_revision_does_not_change_january():
    old=raw_rows([('2025-11-30','40'),('2025-12-31','100'),('2026-01-31','20')])
    new=copy.deepcopy(old);new[1]['Saldo']='120'
    changes,keys=ss.compare_raw(payload(new),payload(old))
    derived,_,_=ss.derive(payload(new),keys)
    january=next(r for r in derived if r['report_date']=='2026-01-31')
    assert january['saldo_monthly_derived']=='20'
    assert 'observed_snapshot_revision_sensitive' not in january['saldo_derivation_flags']


def test_new_period_historical_addition_and_removal_are_distinct():
    old=raw_rows();new=copy.deepcopy(old)
    new.append(dict(old[-1],**{'Fecha Reporte':'2026-09-30','Saldo':'120'}))
    new.append(dict(old[0],**{'CodInstitucion':'0603'}));new.pop(1)
    changes,_=ss.compare_raw(payload(new),payload(old))
    kinds={r['change_type'] for r in changes}
    assert kinds=={'NEW_REPORTING_PERIOD_RECORD','ADDED_HISTORICAL_RECORD','REMOVED_HISTORICAL_RECORD'}


def test_numeric_format_only_change_is_not_amount_revision():
    old=raw_rows();new=copy.deepcopy(old);new[-1]['Saldo']='90.000'
    assert ss.compare_raw(payload(new),payload(old))[0]==[]


def test_invalid_value_is_not_reported_as_verified_numeric_revision():
    old=raw_rows();new=copy.deepcopy(old);new[-1]['Saldo']='not-a-number'
    changes,_=ss.compare_raw(payload(new),payload(old))
    assert changes[0]['change_type']=='INVALID_AMOUNT_CHANGE'


def test_code_change_is_not_silently_bridged():
    rows=raw_rows();rows[-1]['CodInstitucion']='0618'
    derived,market,_=ss.derive(payload(rows))
    last=derived[-1]
    assert last['saldo_derivation_status']=='blocked_missing_prior_month'
    assert last['saldo_monthly_derived']==''
    assert 'market_partial_coverage' in market[-1]['quality_flags']


def test_duplicate_revision_key_is_ambiguous():
    old=raw_rows();new=old+[old[-1]]
    changes,_=ss.compare_raw(payload(new),payload(old))
    assert changes[0]['change_type']=='AMBIGUOUS_KEY'


def test_no_network_without_explicit_acknowledgement(monkeypatch):
    from research.forecasting.monitoring.src import cli
    monkeypatch.setattr(cli,'fetch_document',lambda url:pytest.fail('Unexpected network access'))
    assert plan('Later outcome monitoring')['training_or_forecast_replacement'] is False
    with pytest.raises(ValueError,match='acknowledge'):
        download('new-synthetic','test-only',False)


def test_output_cannot_target_frozen_v1_or_production():
    with pytest.raises(ValueError):safe_output(ev.ROOT/'research/forecasting/results/2026-10-18-v1/new')
    with pytest.raises(ValueError):safe_output(ev.ROOT/'frontend/new-output')


def test_publication_evidence_cannot_be_inferred_or_unbound(tmp_path):
    p=tmp_path/'evidence.txt';p.write_text('Synthetic evidence, not a real publication')
    entry=dict(report_date='2026-08-31',raw_sha256='a'*64,verification_status='MANUALLY_VERIFIED',
               evidence_url='https://publicaciones.cnbs.gob.hn/synthetic-test',evidence_path=str(p),
               evidence_sha256=sha256(p),publication_timestamp='2026-09-30T00:00:00+00:00')
    assert ss.publication_entries([entry],'a'*64,'2026-10-03T00:00:00+00:00')[0]['publication_timestamp']==entry['publication_timestamp']
    with pytest.raises(ValueError,match='exact raw bytes'):
        ss.publication_entries([entry],'b'*64,'2026-10-03T00:00:00+00:00')


def test_evaluation_output_integrity_and_forecast_copy(tmp_path,monkeypatch):
    registry,_=register_test(tmp_path)
    before=ev.frozen_references()
    monkeypatch.setattr(ev,'chart',lambda out,rows:None)
    out=tmp_path/'evaluation'
    summary=ev.evaluate(registry,out,'2026-10-18T00:40:00+00:00')
    assert summary['receipt_based_metrics']['n']==1
    ev.verify_evaluation(out)
    assert ev.frozen_references()==before
    with pytest.raises(ValueError,match='exists'):ev.evaluate(registry,out)
    with (out/'forecast_monitoring.csv').open('a') as f:f.write('tamper\n')
    with pytest.raises(ValueError,match='checksum'):ev.verify_evaluation(out)


def test_future_evaluation_is_not_published_as_actual(tmp_path):
    with pytest.raises(ValueError,match='Future as-of'):
        ev.evaluate(tmp_path/'unused.json',tmp_path/'future','2099-01-01T00:00:00+00:00')


def test_plot_uses_exact_target_month_labels_and_outcome_vintage(tmp_path,monkeypatch):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.figure import Figure
    captured={}
    def inspect_plot(fig,*args,**kwargs):
        fig.canvas.draw()
        captured['labels']=[tick.get_text() for tick in fig.axes[0].get_xticklabels()]
        captured['title']=fig.axes[0].get_title()
    monkeypatch.setattr(Figure,'savefig',inspect_plot)
    rows=ev.compare(ev.forecasts(),[market_row()],snapshot_info(),[],'2026-10-18T02:00:00+00:00')
    ev.chart(tmp_path,rows)
    assert captured['labels']==['Aug 2026','Sep 2026','Oct 2026','Nov 2026','Dec 2026','Jan 2027','Feb 2027']
    assert 'synthetic' in captured['title']
