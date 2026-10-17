'use strict';
const path = require('node:path');
const fs = require('node:fs');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const temporary = path.join(root, '.cache', 'browser-tmp');
fs.mkdirSync(temporary, { recursive: true });
const result = spawnSync(process.execPath, [path.join(root, 'node_modules', '@playwright', 'test', 'cli.js'), 'test', ...process.argv.slice(2)], {
  cwd: root, stdio: 'inherit', windowsHide: true,
  env: { ...process.env, TMP: temporary, TEMP: temporary, TMPDIR: temporary, PLAYWRIGHT_HTML_OPEN: 'never' }
});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);

