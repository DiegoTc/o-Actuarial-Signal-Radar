import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {availableYears,yearRows,yearCounts,comparisonRows,scoringText,timeSelection,timeLabels,scoringStages,firstScoredObservation,scoringLabels} from '../lib/time-exploration';
import type {Signal} from '../lib/data';
// Python standard-library CSV parsing preserves quoted fields in the unchanged source.
function savedRows():Signal[]{
 const source=execFileSync('python3',['-c',`import csv,json
with open('../data/processed/cnbs/expected-behavior/primary_dynamic.csv') as f:
 rows=[r for r in csv.DictReader(f) if r['analysis_level']=='market' and r['baseline_method']=='robust_z' and r['baseline_window']=='12']
 fields=['report_date','availability_date','metric','observed_value','expected_value','residual','residual_signal_score','residual_signal_level','residual_evaluation_status']
 print(json.dumps([{k:r[k] for k in fields} for r in rows]))`],{encoding:'utf8'});
 return JSON.parse(source).map((r:Record<string,string>)=>({...r,observed_value:r.observed_value?Number(r.observed_value):null,expected_value:r.expected_value?Number(r.expected_value):null,residual:r.residual?Number(r.residual):null,residual_signal_score:r.residual_signal_score?Number(r.residual_signal_score):null,adjusted_signal_level:r.residual_signal_level||'NOT_SCORED'} as Signal));
}
const rows=savedRows().filter(r=>r.metric==='monthly_claims').toSorted((a,b)=>a.report_date.localeCompare(b.report_date));
test('historical default and latest available year',()=>{const selection=timeSelection('',availableYears(rows));assert.equal(selection.view,'historical');assert.equal(selection.year,'2026');assert.deepEqual(selection.years,['2024','2025','2026']);});
test('year selections only contain actual saved months',()=>{assert.equal(yearRows(rows,'2020').length,12);assert.equal(yearRows(rows,'2026').length,7);assert.equal(yearRows(rows,'2040').length,0);});
test('November 2020 spike is unscored, not normal',()=>{const row=yearRows(rows,'2020').find(r=>r.report_date==='2020-11-30')!;assert.equal(row.observed_value,226427838.52);assert.equal(row.expected_value,75397334.19750005);assert.equal(row.residual,151030504.32249996);assert.equal(row.residual_signal_score,null);assert.equal(row.adjusted_signal_level,'NOT_SCORED');assert.equal(row.availability_date,'2021-02-01');assert.match(scoringText(row,'es'),/^Sin puntuar — Historia previa insuficiente$/);assert.equal(yearCounts(yearRows(rows,'2020')).NORMAL,0);});
test('comparison is exact saved observed values, no aggregation or zero filling',()=>{const before=JSON.stringify(rows);const result=comparisonRows(rows,['2023','2024','2025','2026']);assert.equal(result.length,12);for(const year of ['2023','2024','2025','2026'])for(const r of yearRows(rows,year))assert.equal(result[Number(r.report_date.slice(5,7))-1]['y'+year],r.observed_value);assert.equal(result[10].y2026,null);assert.equal(result[10].row2026,null);assert.equal(JSON.stringify(rows),before);});
test('missing months stay empty in descriptive pivot',()=>{const sparse=rows.filter(r=>r.report_date!=='2025-02-28');assert.equal(comparisonRows(sparse,['2025'])[1].y2025,null);assert.equal(yearRows(sparse,'2025').length,11);});
test('query selection validates years, removes duplicates, caps at four',()=>{const s=timeSelection('?view=compare&years=2020,2020,2021,2022,2023,2024,bad',availableYears(rows));assert.deepEqual(s.years,['2020','2021','2022','2023']);assert.equal(timeSelection('?view=bad&year=2099',availableYears(rows)).year,'2026');});
test('month labels are bilingual and chronological',()=>{assert.deepEqual(timeLabels.en.monthNames,['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);assert.equal(timeLabels.es.monthNames[0],'Ene');assert.equal(timeLabels.es.monthNames[11],'Dic');});

test('saved data, expected and residual availability do not imply a score or classification',()=>{
 const row=rows.find(r=>r.report_date==='2020-11-30')!;
 assert.deepEqual(scoringStages(row),{observed:true,expected:true,residual:true,score:false,classification:false});
 assert.deepEqual(scoringStages({...row,observed_value:0,expected_value:null,residual:null}),{observed:true,expected:false,residual:false,score:false,classification:false});
 assert.equal(scoringStages({...row,residual_signal_score:99}).classification,false);
 assert.equal(scoringStages({...row,residual_signal_score:NaN}).score,false);
});
test('first scored date is sourced, chronological and ignores unclassified rows',()=>{
 const row=firstScoredObservation([...rows].reverse())!;
 assert.equal(row.report_date,'2021-10-31');assert.equal(row.availability_date,'2022-01-01');
 assert.equal(firstScoredObservation(yearRows(rows,'2020')),undefined);
});
test('saved yearly counts distinguish all unscored observations from normal',()=>{
 const all=savedRows();
 for(const metric of ['monthly_claims','claims_to_premiums_ratio']){
  assert.deepEqual(yearCounts(yearRows(all.filter(r=>r.metric===metric),'2020')),{NORMAL:0,WATCH:0,ALERT:0,NOT_SCORED:12});
 }
 assert.deepEqual(yearCounts(yearRows(rows,'2025')),{NORMAL:9,WATCH:0,ALERT:3,NOT_SCORED:0});
 assert.deepEqual(yearCounts(yearRows(all.filter(r=>r.metric==='claims_to_premiums_ratio'),'2025')),{NORMAL:8,WATCH:2,ALERT:2,NOT_SCORED:0});
});
test('bilingual spike explanation preserves unscored status and residual history limitation',()=>{
 assert.match(scoringLabels.es.spike,/no se clasifica como ALERTA/);assert.match(scoringLabels.es.spike,/historial de residuales/);
 assert.match(scoringLabels.en.spike,/not classified as ALERT/);assert.match(scoringLabels.en.spike,/residual history/);
});
