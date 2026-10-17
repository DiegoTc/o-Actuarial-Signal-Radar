import type { Language } from './data';
export function integrationLabel(status: string | undefined, language: Language): string {
  if (status === 'VERIFIED') return language === 'es' ? 'AMD Token Factory + Evolus: VERIFICADOS' : 'AMD Token Factory + Evolus: VERIFIED';
  if (status === 'CONFIGURED') return language === 'es' ? 'AMD Token Factory: CONFIGURADO' : 'AMD Token Factory: CONFIGURED';
  return language === 'es' ? 'EVOLUS LISTO · AMD PENDIENTE' : 'EVOLUS READY · AMD PENDING';
}
