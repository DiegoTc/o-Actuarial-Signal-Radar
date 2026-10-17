import type {Language,Signal} from '../lib/data';
import {scoringStages,scoringLabels,timeLabels,scoringText} from '../lib/time-exploration';

/** Present saved availability separately from the saved detector decision. */
export default function ScoringStatus({row,language}:{row:Signal;language:Language}){
 const t=scoringLabels[language],time=timeLabels[language],stages=scoringStages(row);
 return <div className="scoring-status" aria-label={t.progress}>
 <dl className="scoring-stages">{(Object.keys(stages) as (keyof typeof stages)[]).map(key=><div key={key} data-stage={key} data-available={stages[key]}><dt>{t[key]}</dt><dd>{key==='classification'?scoringText(row,language):stages[key]?`✓ ${t.available}`:t.unavailable}</dd></div>)}</dl>
 {!stages.classification&&<p className="scoring-reason">{time.reason}: {String(row.residual_evaluation_status).startsWith('insufficient')?time.insufficient:String(row.residual_evaluation_status||'—')} · {time.sourceHistory}: {String(row.residual_history_count??'—')}</p>}
 </div>;
}
