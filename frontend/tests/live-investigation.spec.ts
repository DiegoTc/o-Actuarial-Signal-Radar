import { test, expect } from '@playwright/test';
import fs from 'node:fs';

// Read-only live evidence verification. Never submits another paid/model request.
test.describe('saved real AMD/Evolus investigations',()=>{
 test.skip(process.env.RUN_LIVE_VALIDATION!=='1','Requires already validated real workflow reports');
 for (const id of ['market_claims_2025_09','market_ratio_2025_03']) {
  test(`${id} completed Spanish view preserves the original snapshot`,async({page})=>{
   const pkg=JSON.parse(fs.readFileSync(`../data/processed/investigations/${id}.json`,'utf8'));
   const response=await page.request.get(`http://localhost:3000/api/investigations/${id}?language=es`);
   expect(response.ok()).toBeTruthy();const job=await response.json();
   expect(job.state).toBe('COMPLETED');expect(job.human_review_required).toBe(true);
   expect(job.provider).toBe('amd_token_factory');expect(job.model_name).toBe('DeepSeek-V4-Flash');
   for(const [key,value] of Object.entries(job.investigation.signal_snapshot)) expect(value).toEqual(pkg[key]);
   await page.goto(`http://localhost:3000/cases/${id}`);
   await expect(page.locator('.investigation-panel .status-tag')).toHaveText('COMPLETED');
   await expect(page.getByRole('heading',{name:'Resumen ejecutivo',exact:true})).toBeVisible();
   await expect(page.locator('.investigation-panel')).toContainText('HUMAN_REVIEW_REQUIRED');
   await expect(page.locator('.investigation-panel')).toContainText('Resultado guardado de una ejecución real');
   await expect(page.locator('.result-sections')).toContainText('Preguntas de investigación');
   await page.screenshot({path:`../.local/token-factory/${id}.completed.png`,fullPage:true});
  });
 }
});
