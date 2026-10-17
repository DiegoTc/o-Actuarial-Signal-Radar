export type Language = 'es' | 'en';
export type Signal = Record<string, unknown> & {
  signal_id: string; report_date: string; availability_date: string; metric: string;
  analysis_level: string; institution_code: string; institution_name: string;
  adjusted_signal_level: string; raw_signal_level: string; materiality_level: string;
  case_classification: string; observed_value: number | null; expected_value: number | null;
  residual: number | null; relative_residual: number | null; residual_signal_score: number | null;
};
export type Job = { state: string; human_review_required: boolean; workflow_id?: string; execution_id?: string; library_id?: string; knowledge_available?: boolean; knowledge_documents?: number; investigation?: Record<string, unknown>; error_code?: string; language?: string; provider?: string; model_name?: string; amd_verified?: boolean; saved_result?: boolean };
export const states = ['NOT_STARTED','SUBMITTING','EVOLUS_RECEIVED','PENDING_AMD_MODEL','COMPLETED','VALIDATION_WARNING','ERROR'];
export function parseJob(value: unknown): Job {
  const v = value as Job;
  if (!v || !states.includes(v.state) || v.human_review_required !== true) throw Error('INVALID_RESPONSE');
  return v;
}
export function parseSignals(value: unknown): Signal[] {
  const v = value as { signals: Signal[] };
  if (!v || !Array.isArray(v.signals) || v.signals.some(r => typeof r.signal_id !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(r.availability_date) || !['NORMAL','WATCH','ALERT','NOT_SCORED'].includes(r.adjusted_signal_level))) throw Error('INVALID_RESPONSE');
  return v.signals;
}
export async function request(path: string, init?: RequestInit) {
  const r = await fetch(path, { ...init, cache: 'no-store' });
  if (!r.ok) { const body = await r.json().catch(() => ({})); throw Error(typeof body.error === 'string' ? body.error : 'SERVICE_UNAVAILABLE'); }
  return r.json();
}
export function format(value: unknown, metric = '', language: Language = 'es'): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value !== 'number') return String(value);
  if (metric === 'ratio_delta') return format(value, 'claims_to_premiums_ratio', language).replace('%', ' pp');
  if (metric === 'claims_to_premiums_ratio') return new Intl.NumberFormat(language === 'es' ? 'es-HN' : 'en-US', { style: 'percent', maximumFractionDigits: 2 }).format(value);
  return new Intl.NumberFormat(language === 'es' ? 'es-HN' : 'en-US', { maximumFractionDigits: 2 }).format(value);
}
// Formatting only: all expected values, residuals, scores and classifications come from the Python artifact API.
