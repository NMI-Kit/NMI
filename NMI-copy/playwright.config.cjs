const { defineConfig } = require('@playwright/test');
const path = require('node:path');
const python = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
module.exports = defineConfig({
  testDir: './tests/frontend', outputDir: './.cache/test-results', workers: 1,
  timeout: 30000, retries: 0, reporter: [['list'], ['json', { outputFile: '.cache/frontend-results.json' }]],
  use: { baseURL: 'http://127.0.0.1:8765', browserName: 'chromium',
    headless: true, launchOptions: { executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', chromiumSandbox: true }, trace: 'off', screenshot: 'only-on-failure' },
  webServer: { command: `"${python}" -B tools/serve_preview.py`, url: 'http://127.0.0.1:8765',
    reuseExistingServer: process.env.NMI_REUSE_STATIC_TEST_SERVER === '1', timeout: 15000 }
});

