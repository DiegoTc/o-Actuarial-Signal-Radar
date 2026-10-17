import type { Language, Signal } from './data';

/** Explanatory copy only. No scores, thresholds or analytical values are calculated here. */
export const humanCopy = {
 es: {
  investigationRunning:'Investigación en curso. Esperando la respuesta de Evolus + AMD… Puedes seguir revisando la señal; el estado se actualiza automáticamente.',
  intro:'Actuarial Signal Radar aprende cómo se ha comportado históricamente el mercado de seguros de vehículos en Honduras. Cada mes compara lo que ocurrió con lo que normalmente habría esperado. Si encuentra una diferencia poco común y relevante, genera una señal para que un analista la investigue.',
  principle:'Primero detectamos. Luego la IA investiga. La persona decide.',
  how:'¿Cómo detectamos una señal?',
  steps:[['¿Qué suele pasar?','Usamos meses anteriores para construir una referencia.'],['¿Qué pasó realmente?','Leemos el valor reportado por CNBS.'],['¿Qué tan diferente fue?','Comparamos observado contra esperado.'],['¿Qué tan inusual es?','Lo comparamos con el comportamiento histórico reciente.'],['¿Qué hacemos?','NORMAL → VIGILANCIA → ALERTA']],
  next:'Las alertas pasan a investigación.', technical:'Ver metodología técnica',
  methodology:'El comportamiento esperado combina tendencia histórica y estacionalidad. La diferencia entre lo observado y lo esperado se llama residual. El detector principal es un z-score robusto sobre una ventana de 12 meses de residuales. Z-score estándar, EWMA y CUSUM aportan evidencia complementaria. Solo se utiliza historia previa disponible bajo el lag conservador; la observación actual no entra en su propia referencia.',
  noAiDetection:'La IA no decide si existe una alerta.',
  definitions:[['Tendencia','Dirección general del comportamiento a través del tiempo.'],['Estacionalidad','Patrones que tienden a repetirse en ciertos meses.'],['EWMA','Da más peso a observaciones recientes para detectar cambios.'],['CUSUM','Ayuda a detectar desviaciones persistentes a través del tiempo.']],
  coverage:'¿Tenemos pocos datos?', coverageIntro:'No en cobertura; sí en granularidad.', coverageText:'La fuente cubre el mercado hondureño disponible, pero los datos públicos están agregados mensualmente. Una serie como siniestros mensuales de vehículos tiene alrededor de 100 observaciones temporales, no millones de siniestros individuales.',
  coverageLabels:['Cobertura','Historia','Granularidad','Puntos por serie'], coverageValues:['Mercado hondureño disponible','', 'Mensual agregada','≈ 100'],
  ml:'¿Por qué no usamos Machine Learning para detectar la alerta?', mlIntro:'La capa de detección utiliza deliberadamente un modelo estadístico interpretable. Para el volumen y granularidad actual de los datos mensuales, permite generar señales auditables sin introducir complejidad innecesaria.',
  mlReasons:['Alrededor de 100 meses por serie: los modelos complejos pueden sobreajustarse.','Un método estadístico es más fácil de auditar: mismos datos y configuración, misma señal.','Los problemas de calidad de datos permanecen visibles.','Buscamos desviaciones inusuales; no pronosticamos el futuro.'],
  deliberate:'Es una decisión metodológica, no una limitación accidental.', future:'¿Cuándo sí tendría sentido Machine Learning?',
  futureIntro:'Con datos más ricos —siniestros individuales, frecuencia, severidad, tipo de vehículo, región, cobertura, causa, costo de reparación y características de pólizas— se podrían evaluar modelos más complejos frente a la línea base actual. No necesariamente serían mejores.',
  today:'HOY', todayData:'≈ 100 meses por serie', todayModel:'Modelo estadístico interpretable', futureLabel:'FUTURO', futureData:'Miles o millones de registros individuales + múltiples variables', futureModel:'Isolation Forest / XGBoost / Autoencoder: posibles comparaciones futuras; no implementadas',
  ai:'Entonces, ¿para qué usamos IA?', roles:['Detección estadística','Investigación con IA','Revisión humana'], questions:['¿Hay algo raro?','¿Qué deberíamos investigar?','¿Qué significa y qué hacemos?'],
  responsibilities:[['Valor esperado y diferencia vs esperado','Z-score robusto y NORMAL / VIGILANCIA / ALERTA','Detección reproducible'],['Resumir y explicar lo que cambió','Proponer hipótesis e identificar información faltante','Recomendar comprobaciones y traducir hallazgos a lenguaje de negocio'],['Validar el contexto','Aceptar o rechazar hipótesis','Tomar la decisión final']],
  aiBoundary:'La alerta fue detectada estadísticamente. La siguiente sección contiene la investigación con IA recibida a través de Evolus + AMD; no cambia la clasificación del detector.',
  awaiting:'La señal ya fue detectada estadísticamente. Aquí se mostrará la investigación cuando exista una respuesta validada; no se inventan hallazgos.',
  mockBoundary:'Salida de prueba: no es una investigación real de AMD.', difference:'Diferencia vs esperado', unusual:'Qué tan inusual', impact:'Impacto económico', exploratory:'Materialidad exploratoria',
  unusualLevels:{ALERT:'Muy inusual',WATCH:'Merece seguimiento',NORMAL:'Dentro de lo habitual',NOT_SCORED:'Sin puntuar'}, impactLevels:{HIGH:'Alto',MEDIUM:'Medio',LOW:'Bajo'},
  unusualNote:'Descripción de la clasificación guardada; no es un nuevo puntaje ni una probabilidad.',
  ratioLead:'Viendo solo el valor bruto, el período parecía normal. Después de ajustar por tendencia y estacionalidad, el comportamiento resultó suficientemente inusual para generar una alerta.',
  claimsLead:'Esto fue una desviación extremadamente inusual frente al comportamiento reciente.',
 },
 en: {
  investigationRunning:'Investigation in progress. Waiting for Evolus + AMD… You can keep reviewing the signal; status updates automatically.',
  intro:'Actuarial Signal Radar learns how the Honduran motor insurance market has historically behaved. Each month it compares what actually happened with what would normally have been expected. If the difference is unusual and meaningful, it creates a signal for investigation.',
  principle:'We detect first. AI investigates second. Humans decide.', how:'How do we detect a signal?',
  steps:[['What usually happens?','We use earlier months to build a reference.'],['What actually happened?','We read the value reported by CNBS.'],['How different was it?','We compare observed with expected.'],['How unusual is it?','We compare it with recent historical behavior.'],['What do we do?','NORMAL → WATCH → ALERT']],
  next:'Alerts move to investigation.', technical:'View technical methodology',
  methodology:'Expected behavior combines historical trend and seasonality. The difference between observed and expected is called the residual. The primary detector is a robust z-score over a 12-month window of residuals. Standard z-score, EWMA and CUSUM provide complementary evidence. Only prior history available under the conservative lag is used; the current observation never enters its own reference.',
  noAiDetection:'AI does not decide whether an alert exists.',
  definitions:[['Trend','The general direction of behavior over time.'],['Seasonality','Patterns that tend to repeat in particular months.'],['EWMA','Gives more weight to recent observations to detect changes.'],['CUSUM','Helps detect persistent deviations over time.']],
  coverage:'Do we have too little data?', coverageIntro:'Not in coverage; yes in granularity.', coverageText:'The source covers the available Honduran market, but public data are aggregated monthly. A series such as monthly motor claims has around 100 observations over time, not millions of individual claims.',
  coverageLabels:['Coverage','History','Granularity','Points per series'], coverageValues:['Available Honduran market','','Monthly aggregates','≈ 100'],
  ml:'Why don’t we use Machine Learning to detect the alert?', mlIntro:'The detection layer deliberately uses an interpretable statistical model. For the current volume and granularity of monthly data, this produces auditable signals without unnecessary complexity.',
  mlReasons:['Around 100 months per series: complex models can overfit.','A statistical method is easier to audit: the same data and configuration produce the same signal.','Data-quality issues remain visible.','We look for unusual deviations; we do not forecast the future.'],
  deliberate:'This is a methodological decision, not an accidental limitation.', future:'When would Machine Learning make sense?',
  futureIntro:'With richer data—individual claims, frequency, severity, vehicle type, region, coverage, cause, repair costs and policy characteristics—more complex models could be benchmarked against the current baseline. They would not necessarily be better.',
  today:'TODAY', todayData:'≈ 100 months per series', todayModel:'Interpretable statistical model', futureLabel:'FUTURE', futureData:'Thousands or millions of individual records + multiple variables', futureModel:'Isolation Forest / XGBoost / Autoencoder: possible future comparisons; not implemented',
  ai:'So what do we use AI for?', roles:['Statistical detection','AI investigation','Human review'], questions:['Is anything unusual?','What should we investigate?','What does it mean, and what should we do?'],
  responsibilities:[['Expected value and difference from expected','Robust z-score and NORMAL / WATCH / ALERT','Reproducible detection'],['Summarize and explain what changed','Propose hypotheses and identify missing information','Recommend checks and translate findings into business language'],['Validate context','Accept or reject hypotheses','Make the final decision']],
  aiBoundary:'The alert was detected statistically. The next section contains the AI investigation received through Evolus + AMD; it does not change the detector classification.',
  awaiting:'The signal has already been detected statistically. A validated investigation response will appear here when available; findings are never invented.', mockBoundary:'Test output: this is not a real AMD investigation.',
  difference:'Difference from expected', unusual:'How unusual', impact:'Economic impact', exploratory:'Exploratory materiality',
  unusualLevels:{ALERT:'Very unusual',WATCH:'Warrants monitoring',NORMAL:'Within usual behavior',NOT_SCORED:'Unscored'}, impactLevels:{HIGH:'High',MEDIUM:'Medium',LOW:'Low'},
  unusualNote:'Description of the saved classification; not a new score or a probability.',
  ratioLead:'Looking only at the raw value, the period appeared normal. After adjusting for trend and seasonality, its behavior was unusual enough to trigger an alert.',
  claimsLead:'This was an extremely unusual deviation relative to recent behavior.',
 }
};

// Translate existing classifications only; never infer a classification from a numerical value.
export function humanSignalLevel(signal: Signal, language: Language): string {
 const levels: Record<string,string> = humanCopy[language].unusualLevels;
 return levels[signal.adjusted_signal_level] || '—';
}
export function humanImpact(level: string, language: Language): string {
 const levels: Record<string,string> = humanCopy[language].impactLevels;
 return levels[level] || '—';
}
