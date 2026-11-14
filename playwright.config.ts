import {defineConfig,devices} from '@playwright/test';
const serverCommand=process.env.CI?'npm run start':'npm run dev';
export default defineConfig({testDir:'./e2e',fullyParallel:true,reporter:[['list'],['html',{outputFolder:'playwright-report',open:'never'}]],use:{baseURL:'http://127.0.0.1:3000',trace:'retain-on-failure'},projects:[{name:'chromium',use:{...devices['Desktop Chrome']}}],webServer:{command:serverCommand,url:'http://127.0.0.1:3000',reuseExistingServer:!process.env.CI,timeout:120000}});
