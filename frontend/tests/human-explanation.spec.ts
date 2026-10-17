import {test,expect} from '@playwright/test';

test('human-first overview reveals technical and future detail progressively in both languages',async({page})=>{
 await page.goto('http://127.0.0.1:3000');
 await expect(page.locator('.human-intro')).toContainText('mercado de seguros de vehículos en Honduras');
 await expect(page.getByRole('heading',{name:'¿Cómo detectamos una señal?'})).toBeVisible();
 await expect(page.locator('.human-steps li')).toHaveCount(5);
 const technical=page.locator('.technical-methodology');
 await expect(technical).not.toHaveAttribute('open','');
 await technical.locator('summary').click();await expect(technical).toHaveAttribute('open','');
 await expect(technical).toContainText('12 meses de residuales');
 await expect(technical).toContainText('residual = observed − expected');
 await expect(page.getByRole('heading',{name:'¿Tenemos pocos datos?'})).toBeVisible();
 await expect(page.locator('.coverage-grid')).toContainText('2018–2026');
 const ml=page.locator('.human-accordion').first();await ml.locator('summary').click();
 await expect(ml).toContainText('misma señal');await expect(ml).toContainText('decisión metodológica');
 const future=page.locator('.human-accordion').last();await future.locator('summary').click();
 await expect(future).toContainText('No necesariamente serían mejores');
 await expect(page.locator('.responsibility-grid').first()).toContainText('Tomar la decisión final');
 await page.screenshot({path:'../.local/phase53/overview.es.png',fullPage:true});
 await page.getByRole('button',{name:'Change language'}).click();
 await expect(page.locator('.human-intro')).toContainText('Honduran motor insurance market');
 await expect(page.getByRole('heading',{name:'How do we detect a signal?'})).toBeVisible();
 await expect(page.getByText('View technical methodology',{exact:true})).toBeVisible();
 await expect(page.getByRole('heading',{name:'So what do we use AI for?'})).toBeVisible();
 await page.screenshot({path:'../.local/phase53/overview.en.png',fullPage:true});
});
for(const id of ['market_claims_2025_09','market_ratio_2025_03']){
 test(`${id} leads with meaning, preserves source values and separates real AI from detection`,async({page})=>{
  await page.goto(`http://127.0.0.1:3000/cases/${id}`);
  const lead=page.locator('.case-human-lead');await expect(lead).toBeVisible();
  if(id.includes('claims'))await expect(lead).toContainText('L 42.9 millones');
  else await expect(lead).toContainText('Viendo solo el valor bruto');
  await expect(page.locator('.compact-flow')).toContainText('Detección estadística');
  await expect(page.locator('.compact-flow')).toContainText('Investigación con IA');
  await expect(page.locator('.compact-flow')).toContainText('HUMAN_REVIEW_REQUIRED');
  await expect(page.locator('.signal-secondary')).toContainText('Muy inusual');
  await expect(page.locator('.ai-result-boundary')).toContainText('Evolus + AMD');
  await expect(page.locator('.ai-result-boundary')).toContainText('no cambia la clasificación');
  await expect(page.locator('.result-sections')).toBeVisible();
  await page.screenshot({path:`../.local/phase53/${id}.es.png`,fullPage:true});
  await page.getByRole('button',{name:'Change language'}).click();
  await expect(page.locator('.compact-flow')).toContainText('Statistical detection');
  // Saved real investigations are language-specific. Switching languages must not invent a translated model result.
  await expect(page.locator('.ai-result-boundary, .investigation-boundary')).toContainText(/does not change the detector classification|findings are never invented/);
 });
}
test('human explanation remains readable on mobile with keyboard disclosure',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('http://127.0.0.1:3000');
 const summary=page.locator('.technical-methodology summary');await summary.focus();await page.keyboard.press('Enter');
 await expect(page.locator('.technical-methodology')).toHaveAttribute('open','');
 await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:'../.local/phase53/mobile.es.png',fullPage:true});
 await page.screenshot({path:'../.local/phase53/mobile-viewport.es.png'});
 for(const id of ['market_claims_2025_09','market_ratio_2025_03']){
  await page.goto(`http://127.0.0.1:3000/cases/${id}`);
  await expect(page.locator('.case-human-lead')).toBeVisible();
  for(const language of ['es','en']){
   if(language==='en')await page.getByRole('button',{name:'Change language'}).click();
   await expect(page.locator('.compact-flow')).toBeVisible();
   await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
   await page.screenshot({path:`../.local/phase53/${id}.mobile.${language}.png`,fullPage:true});
  }
  await page.getByRole('button',{name:'Change language'}).click();
 }

});
