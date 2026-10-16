const {defineConfig}=require('@playwright/test');
const path=require('node:path');
module.exports=defineConfig({
  testDir:'./tests/chatgpt-browser',outputDir:'.cache/chatgpt-browser-results',workers:1,timeout:60000,retries:0,
  reporter:[['list'],['json',{outputFile:'.cache/chatgpt-browser-results.json'}]],
  use:{baseURL:'http://127.0.0.1:8768',browserName:'chromium',headless:true,
    launchOptions:{executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',chromiumSandbox:true},trace:'off',screenshot:'only-on-failure'},
  webServer:{command:`"${path.join(__dirname,'.venv/Scripts/python.exe')}" -B tests/local/chatgpt_browser_server.py`,url:'http://127.0.0.1:8768',reuseExistingServer:false,timeout:20000}
});
