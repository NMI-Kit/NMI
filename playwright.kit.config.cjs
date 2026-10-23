const { defineConfig } = require('@playwright/test');
const path = require('node:path');
const python = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
// Phone and desktop widths of the kit page (kit/), served as plain static files like GitHub Pages does.
module.exports = defineConfig({
  testDir: './tests/kit', testMatch: '**/*.spec.cjs', outputDir: './.cache/kit-results', workers: 1,
  timeout: 30000, retries: 0, reporter: [['list'], ['json', { outputFile: '.cache/kit-results.json' }]],
  use: { baseURL: 'http://127.0.0.1:8772', browserName: 'chromium', headless: true,
    launchOptions: { executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', chromiumSandbox: true },
    trace: 'off', screenshot: 'only-on-failure' },
  webServer: { command: `"${python}" -B -m http.server 8772 --bind 127.0.0.1 --directory kit`, url: 'http://127.0.0.1:8772/index.html',
    reuseExistingServer: false, timeout: 15000 }
});
