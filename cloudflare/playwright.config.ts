// Runs the unchanged dashboard scenarios against the isolated local Worker.
export default {testDir:'../.local/cloudflare/frontend/tests',testMatch:'*.spec.ts',use:{channel:'chrome',headless:true},reporter:'list',workers:1};
