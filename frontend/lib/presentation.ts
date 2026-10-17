import type { Language, Signal } from './data';
import { format } from './data';

/** Unit conversion and rounding for display only; never derive analytical quantities. */
export function displayValue(value: number | null, metric: string, language: Language, difference=false): string {
  if(value===null) return '—';
  const sign=difference&&value>0?'+':'';
  if(metric==='claims_to_premiums_ratio') return sign+format(value,difference?'ratio_delta':metric,language);
  const magnitude=new Intl.NumberFormat(language==='es'?'es-HN':'en-US',{minimumFractionDigits:1,maximumFractionDigits:1}).format(Math.abs(value)/1e6);
  return `${value<0?'−':sign}L ${magnitude} M`;
}
export function exactValue(value: number | null, metric: string): string {
  if(value===null) return '—';
  return (metric==='claims_to_premiums_ratio'?'':'L ')+String(value);
}
export function interpretation(signal:Signal, language:Language): string {
  if(signal.residual===null) return '';
  const above=signal.residual>=0;
  const amount=displayValue(Math.abs(signal.residual),signal.metric,language).replace(' M','');
  if(signal.metric==='claims_to_premiums_ratio') {
    const points=format(Math.abs(signal.residual),'ratio_delta',language).replace(' pp','');
    return language==='es'?`La razón siniestros/primas estuvo ${points} puntos porcentuales ${above?'por encima':'por debajo'} de lo esperado.`:`The claims-to-premiums ratio was ${points} percentage points ${above?'above':'below'} expected.`;
  }
  const subject=signal.metric==='monthly_claims'?(language==='es'?'Los siniestros':'Claims'):(language==='es'?'Las primas':'Premiums');
  return language==='es'?`${subject} estuvieron aproximadamente ${amount} millones ${above?'por encima':'por debajo'} de lo esperado para ese período.`:`${subject} were approximately ${amount} million ${above?'above':'below'} the expected level for that period.`;
}
export function residualAxis(value:number, metric:string, language:Language):string {
  return metric==='claims_to_premiums_ratio'?format(value,'ratio_delta',language):displayValue(value,metric,language);
}
