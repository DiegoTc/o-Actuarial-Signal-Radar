import test from 'node:test';
import assert from 'node:assert/strict';
import { parseJob, parseSignals, format } from '../lib/data';
import { labels } from '../lib/i18n';
import { integrationLabel } from '../lib/integration';
test('integration badges distinguish configured from verified in both languages',()=>{
 assert.match(integrationLabel('VERIFIED','es'),/VERIFICADOS/);
 assert.match(integrationLabel('VERIFIED','en'),/VERIFIED/);
 assert.doesNotMatch(integrationLabel('CONFIGURED','en'),/VERIFIED/);
 assert.match(integrationLabel(undefined,'es'),/PENDIENTE/);
});
test('completed AMD result retains review and provider metadata',()=>{
 const job=parseJob({state:'COMPLETED',human_review_required:true,provider:'amd_token_factory',model_name:'Qwen3.8-27B'});
 assert.equal(job.provider,'amd_token_factory');assert.equal(job.human_review_required,true);
});
test('pending is a real accepted state, not an error',()=>assert.equal(parseJob({state:'PENDING_AMD_MODEL',human_review_required:true}).state,'PENDING_AMD_MODEL'));
test('response must require human review',()=>assert.throws(()=>parseJob({state:'COMPLETED',human_review_required:false})));
test('malformed response rejected',()=>{assert.throws(()=>parseJob(null));assert.throws(()=>parseSignals({signals:'bad'}));assert.throws(()=>parseJob({state:'invented',human_review_required:true}));});
test('both languages have matching keys and distinct labels',()=>{assert.deepEqual(Object.keys(labels.es).sort(),Object.keys(labels.en).sort());assert.equal(labels.es.observed,'Observado');assert.equal(labels.en.observed,'Observed');assert.match(labels.es.pending,/no está conectado/);});
test('formatting preserves missing values and is deterministic',()=>{assert.equal(format(null),'—');assert.equal(format(11.015446,'','en'),'11.02');assert.equal(format(0.1086,'claims_to_premiums_ratio','en'),'10.86%');});

test('ratio differences display percentage points',()=>assert.equal(format(.1086,'ratio_delta','en'),'10.86 pp'));

import { displayValue, interpretation, residualAxis } from '../lib/presentation';
import type { Signal } from '../lib/data';
import fs from 'node:fs';
const claims=JSON.parse(fs.readFileSync('../data/processed/investigations/market_claims_2025_09.json','utf8'));
const ratio=JSON.parse(fs.readFileSync('../data/processed/investigations/market_ratio_2025_03.json','utf8'));
test('compact flagship values are formatted from saved inputs',()=>{
 assert.equal(displayValue(claims.observed_value,claims.metric,'en'),'L 185.4 M');
 assert.equal(displayValue(claims.expected_value,claims.metric,'en'),'L 142.4 M');
 assert.equal(displayValue(claims.residual,claims.metric,'en',true),'+L 42.9 M');
 assert.equal(displayValue(ratio.residual,ratio.metric,'en',true),'+10.86 pp');
});
test('residual axis uses percentage points, never ratio percent',()=>{
 assert.equal(residualAxis(ratio.residual,ratio.metric,'en'),'10.86 pp');
 assert.ok(!residualAxis(ratio.residual,ratio.metric,'en').includes('%'));
 assert.match(residualAxis(claims.residual,claims.metric,'en'),/^L .* M$/);
});
test('human interpretation uses saved difference with no mutation',()=>{
 const before=JSON.stringify([claims,ratio]);
 assert.match(interpretation(claims as Signal,'es'),/L 42.9 millones por encima/);
 assert.match(interpretation(ratio as Signal,'en'),/10.86 percentage points above expected/);
 assert.equal(JSON.stringify([claims,ratio]),before);
});
test('explanations preserve caveats in both languages',()=>{
 for(const language of ['es','en'] as const){
  assert.ok(labels[language].alertMeaning);assert.ok(labels[language].absoluteTip);assert.ok(labels[language].relativeTip);
  assert.equal(labels[language].howSteps.length,6);assert.ok(labels[language].pendingNoFindings);
 }
 assert.match(labels.es.robustTip,/No es una probabilidad/);
 assert.match(labels.en.economic,/not a regulatory or capital threshold/);
 assert.equal(labels.es.raw,'Señal bruta');assert.equal(labels.es.availability,'Disponible para análisis (simulado)');
});
