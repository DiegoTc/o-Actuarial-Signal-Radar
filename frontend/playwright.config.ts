import { defineConfig } from '@playwright/test';
export default defineConfig({testDir:'./tests',testMatch:'*.spec.ts',use:{channel:'chrome',headless:true},reporter:'list'});
