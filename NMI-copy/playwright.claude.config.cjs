const {defineConfig}=require('@playwright/test');
const path=require('node:path');
module.exports=defineConfig({
  testDir:'./tests/claude-browser',outputDir:'.cache/claude-browser-results',workers:1,timeout:90000,retries:0,
  reporter:[['list'],['json',{outputFile:'.cache/claude-browser-results.json'}]],
  use:{baseURL:'http://127.0.0.1:8771',browserName:'chromium',headless:true,
    launchOptions:{executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',chromiumSandbox:true},
    trace:'off',screenshot:'only-on-failure'},
  webServer:{command:`"${path.join(__dirname,'.venv/Scripts/python.exe')}" -X utf8 -B tests/local/claude_browser_server.py`,
    url:'http://127.0.0.1:8771',reuseExistingServer:false,timeout:20000}
});
