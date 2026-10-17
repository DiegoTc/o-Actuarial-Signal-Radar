/** Descriptive selection/pivoting of saved observations; no detector calculations. */
import type { Language, Signal } from './data';
export type TimeView = 'historical'|'year'|'compare';
export const timeLabels = {
 es: {view:'Vista',historical:'Histórico',year:'Por año',compare:'Comparar años',selectYear:'Año',selectYears:'Años (máximo 4)',help:'Histórico muestra la tendencia completa. Por año permite analizar cada mes con más detalle. Comparar años ayuda a identificar patrones estacionales.',unscored:'Sin puntuar',insufficient:'Historia previa insuficiente',scored:'Puntuado',status:'Estado de puntuación',reason:'Motivo guardado',unscoredExplanation:'Este período tiene datos observados, pero no suficiente historia previa para emitir NORMAL, VIGILANCIA o ALERTA.',otherUnscored:'La observación no tiene puntuación; consulta el motivo guardado.',observedOnly:'Comparación descriptiva de valores observados. Sin promediar años, normalizar ni crear nuevos valores esperados. Los meses ausentes quedan vacíos.',firstScored:'Primera observación puntuada',flagship:'Ver caso FLAGSHIP',months:'Mes',allMonths:'Meses disponibles',monthDetail:'Detalle mensual',missing:'Sin observación guardada',normal:'Normal',watch:'Vigilancia',alert:'Alerta',sourceHistory:'Residuales previos disponibles',monthNames:['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']},
 en: {view:'View',historical:'Historical',year:'By year',compare:'Compare years',selectYear:'Year',selectYears:'Years (maximum 4)',help:'Historical shows the full trend. By year provides month-level detail. Compare years helps reveal seasonal patterns.',unscored:'Unscored',insufficient:'Insufficient prior history',scored:'Scored',status:'Scoring status',reason:'Saved reason',unscoredExplanation:'This period has observed data, but insufficient prior history to assign NORMAL, WATCH, or ALERT.',otherUnscored:'This observation has no score; inspect the saved reason.',observedOnly:'Descriptive comparison of observed values. No averaging across years, normalization or newly estimated expected values. Missing months remain empty.',firstScored:'First scored observation',flagship:'View FLAGSHIP case',months:'Month',allMonths:'Available months',monthDetail:'Monthly detail',missing:'No saved observation',normal:'Normal',watch:'Watch',alert:'Alert',sourceHistory:'Available prior residuals',monthNames:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']},
};
export function availableYears(rows:Signal[]):string[]{return [...new Set(rows.map(r=>r.report_date.slice(0,4)))].sort();}
export function yearRows(rows:Signal[],year:string):Signal[]{return rows.filter(r=>r.report_date.startsWith(year+'-')).toSorted((a,b)=>a.report_date.localeCompare(b.report_date));}
export function yearCounts(rows:Signal[]){return Object.fromEntries(['NORMAL','WATCH','ALERT','NOT_SCORED'].map(level=>[level,rows.filter(r=>r.adjusted_signal_level===level).length]));}
export function scoringText(row:Signal,language:Language):string{
 const t=timeLabels[language];
 if(row.adjusted_signal_level==='NOT_SCORED') return `${t.unscored} — ${String(row.residual_evaluation_status).startsWith('insufficient')?t.insufficient:t.otherUnscored}`;
 return ({NORMAL:t.normal,WATCH:t.watch,ALERT:t.alert} as Record<string,string>)[row.adjusted_signal_level]||t.unscored;
}
export function comparisonRows(rows:Signal[],years:string[]):Record<string,any>[] {
 const selected=years.slice(0,4);
 return Array.from({length:12},(_,i)=>{
  const month=String(i+1).padStart(2,'0');const result:Record<string,any>={month};
  for(const year of selected){const row=rows.find(r=>r.report_date.startsWith(`${year}-${month}-`));result['y'+year]=row?.observed_value??null;result['row'+year]=row??null;}
  return result;
 });
}
export function timeSelection(query:string,years:string[]){
 const q=new URLSearchParams(query);const view=q.get('view');const latest=years.at(-1)||'';
 return {view:(view==='year'||view==='compare'?view:'historical') as TimeView,year:years.includes(q.get('year')||'')?q.get('year')!:latest,
 years:q.has('years')?[...new Set((q.get('years')||'').split(',').filter(y=>years.includes(y)))].slice(0,4):years.slice(-3)};
}
export const metricAliases:Record<string,string>={claims:'monthly_claims',premiums:'monthly_premiums',ratio:'claims_to_premiums_ratio'};

/** Availability of saved fields only. Never infer a detector classification from magnitude. */
export function scoringStages(row:Signal){
 const present=(value:unknown)=>typeof value==='number'&&Number.isFinite(value);
 return {observed:present(row.observed_value),expected:present(row.expected_value),residual:present(row.residual),score:present(row.residual_signal_score),classification:['NORMAL','WATCH','ALERT'].includes(row.adjusted_signal_level)};
}
export function firstScoredObservation(rows:Signal[]):Signal|undefined{
 return rows.filter(r=>['NORMAL','WATCH','ALERT'].includes(r.adjusted_signal_level)).toSorted((a,b)=>a.report_date.localeCompare(b.report_date))[0];
}
export const scoringLabels={
 es:{observed:'Datos observados',expected:'Esperado calculado',residual:'Residual calculado',score:'Puntuación robusta',classification:'Clasificación',available:'Disponible',unavailable:'No disponible',progress:'Disponibilidad de datos y puntuación',spike:'El pico de noviembre de 2020 es muy grande, pero no se clasifica como ALERTA porque en ese momento todavía no existía suficiente historial de residuales para calcular el z-score robusto.',warmup:'Calibración / sin puntuar',scoredPeriod:'Inicio del período puntuado',warmupDetail:'Antes de la primera puntuación pueden existir datos observados, valores esperados y residuales. Su disponibilidad no garantiza una puntuación. Consulta el estado guardado de cada mes, también en períodos posteriores. Cada observación conserva su propia fecha de disponibilidad simulada.'},
 en:{observed:'Observed data',expected:'Expected value calculated',residual:'Residual calculated',score:'Robust score',classification:'Classification',available:'Available',unavailable:'Not available',progress:'Data and scoring availability',spike:'The November 2020 spike is very large, but it is not classified as ALERT because there was not yet enough residual history to calculate the robust z-score.',warmup:'Calibration / unscored',scoredPeriod:'Start of scored period',warmupDetail:'Before the first score, observed data, expected values and residuals may exist. Their availability does not guarantee a score. Inspect each month’s saved status, including later periods. Each observation keeps its own simulated availability date.'},
};
