import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {humanCopy,humanSignalLevel,humanImpact} from '../lib/human-copy';
import type {Signal} from '../lib/data';

test('human descriptions translate saved classifications without creating numerical thresholds',()=>{
 const row=JSON.parse(fs.readFileSync('../data/processed/investigations/market_claims_2025_09.json','utf8'));
 const before=JSON.stringify(row);
 assert.equal(humanSignalLevel(row as Signal,'es'),'Muy inusual');
 assert.equal(humanSignalLevel(row as Signal,'en'),'Very unusual');
 assert.equal(humanImpact(row.materiality_level,'es'),'Alto');
 assert.equal(JSON.stringify(row),before);
 assert.equal(humanSignalLevel({...row,adjusted_signal_level:'NOT_SCORED',residual_signal_score:1000},'es'),'Sin puntuar');
 assert.equal(humanSignalLevel({...row,adjusted_signal_level:'UNKNOWN'},'en'),'—');
 assert.equal(humanImpact('UNKNOWN','es'),'—');
});
test('both languages explain methodology, granularity and statistics/AI/human responsibilities',()=>{
 assert.deepEqual(Object.keys(humanCopy.es).sort(),Object.keys(humanCopy.en).sort());
 for(const c of Object.values(humanCopy)){
  assert.equal(c.steps.length,5);assert.equal(c.roles.length,3);assert.equal(c.responsibilities.length,3);
  assert.match(c.methodology,/12/);assert.match(c.methodology,/EWMA/);assert.match(c.methodology,/CUSUM/);
  assert.match(c.coverageText,/100/);assert.match(c.futureModel,/not implemented|no implementadas/);
  assert.match(c.aiBoundary,/Evolus \+ AMD/);
 }
});
