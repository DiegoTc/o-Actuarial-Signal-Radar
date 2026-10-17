// Offline JavaScript execution checks. No API calls, model calls, or credentials.
import assert from 'node:assert/strict';
let input='';for await(const part of process.stdin)input+=part;
const fixture=JSON.parse(input);
function run(handoff) {
  const original=structuredClone(handoff); let data=handoff;
  for(const step of fixture.steps) {
    if(step.stepType===14) break;
    if(step.inputMode===3)data={original,result:data};
    data=new Function('input','data','params',JSON.parse(step.stepConfigJson).script)(JSON.stringify(data),data,{language:'es'});
  }
  return data;
}
let checks=0;
for(const signal of fixture.packages) {
  const handoff={signal_package:Object.fromEntries(Object.entries(signal).reverse()),
    signal_package_json:JSON.stringify(signal),language:'es',validation_mode:'PRE_AMD_HANDOFF_ONLY',
    library_id:fixture.library_id,knowledge_context:fixture.chunks.filter(c=>
      !c.id.startsWith('knowledge:market_')||c.id==='knowledge:'+signal.signal_id).map(c=>({...c,document_id:'OFFLINE_FIXTURE'}))};
  const result=run(structuredClone(handoff));
  assert.deepEqual(result.signal_package,signal);checks++;
  assert.equal(result.signal_package_json,handoff.signal_package_json);checks++;
  assert.equal(result.human_review_required,true);checks++;
  assert.equal(result.investigation_status,'PENDING_AMD_MODEL');checks++;
  assert.deepEqual(result.possible_hypotheses,[]);checks++;
  const bad=[];
  for(const key of ['report_date','availability_date','residual']) {
    const value=structuredClone(handoff);delete value.signal_package[key];bad.push(value);
  }
  for(const [key,value] of [['residual',signal.residual+1],['availability_date','2025-02-30'],
      ['observed_value',false],['strict_point_in_time_status','VALIDATED']]) {
    const candidate=structuredClone(handoff);candidate.signal_package[key]=value;bad.push(candidate);
  }
  bad.push({...structuredClone(handoff),validation_mode:'LIVE_AMD'});
  bad.push({...structuredClone(handoff),knowledge_context:[]});
  for(const candidate of bad){assert.throws(()=>run(candidate));checks++;}
}
console.log(`${checks} offline workflow JavaScript assertions passed; no remote execution.`);
