import type {Language, Signal} from '../lib/data';
import {humanCopy} from '../lib/human-copy';
import {interpretation} from '../lib/presentation';

export function HumanMethodology({language}:{language:Language}) {
 const c=humanCopy[language];
 return <section className="panel human-methodology"><h2>{c.how}</h2><ol className="human-steps">{c.steps.map(([title,text])=><li key={title}><strong>{title}</strong><p>{text}</p></li>)}</ol><p className="human-next">{c.next}</p><details className="technical-methodology"><summary>{c.technical}</summary><p>{c.methodology}</p><code>residual = observed − expected</code><dl className="human-definitions">{c.definitions.map(([term,text])=><div key={term}><dt><abbr title={text}>{term}</abbr></dt><dd>{text}</dd></div>)}</dl></details></section>;
}
export function ResponsibilityFlow({language,compact=false}:{language:Language;compact?:boolean}) {
 const c=humanCopy[language];
 return <section className={`responsibility-flow ${compact?'compact-flow':'panel'}`} aria-label={c.principle}>{!compact&&<><h2>{c.ai}</h2><p>{c.noAiDetection}</p></>}<div className="responsibility-grid">{c.roles.map((role,i)=><article key={role}><span className="eyebrow">0{i+1}</span><h3>{role}</h3><p><strong>{compact?(i===0?(language==='es'?'Observado · Esperado · Diferencia · Señal':'Observed · Expected · Difference · Signal'):i===1?'Evolus + AMD':'HUMAN_REVIEW_REQUIRED'):c.questions[i]}</strong></p>{!compact&&<ul>{c.responsibilities[i].map(text=><li key={text}>{text}</li>)}</ul>}</article>)}</div><p className="human-principle">{c.principle}</p></section>;
}
export function DataAndModelExplainer({language,start,end}:{language:Language;start:string;end:string}) {
 const c=humanCopy[language];
 return <section className="panel data-explainer"><h2>{c.coverage}</h2><p><strong>{c.coverageIntro}</strong></p><p>{c.coverageText}</p><dl className="coverage-grid">{c.coverageLabels.map((label,i)=><div key={label}><dt>{label}</dt><dd>{i===1?`${start.slice(0,4)}–${end.slice(0,4)}`:c.coverageValues[i]}</dd></div>)}</dl><details className="human-accordion"><summary>{c.ml}</summary><p>{c.mlIntro}</p><ul>{c.mlReasons.map(reason=><li key={reason}>{reason}</li>)}</ul><strong>{c.deliberate}</strong></details><details className="human-accordion"><summary>{c.future}</summary><p>{c.futureIntro}</p><div className="future-grid"><article><h3>{c.today}</h3><p>{c.todayData}</p><p>↓ {c.todayModel}</p></article><article><h3>{c.futureLabel}</h3><p>{c.futureData}</p><p>↓ {c.futureModel}</p></article></div></details></section>;
}
export function CaseLead({signal,language}:{signal:Signal;language:Language}) {
 const c=humanCopy[language];
 const contrast=signal.metric==='claims_to_premiums_ratio'&&signal.raw_signal_level==='NORMAL'&&signal.adjusted_signal_level==='ALERT';
 return <div className="case-human-lead">{contrast&&<p className="human-ratio-lead">{c.ratioLead}</p>}<p className="case-interpretation">{interpretation(signal,language)}</p>{signal.signal_id==='market_claims_2025_09'&&signal.adjusted_signal_level==='ALERT'&&<p>{c.claimsLead}</p>}</div>;
}
