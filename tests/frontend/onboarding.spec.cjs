const { test, expect, chromium } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('node:fs');
const path = require('node:path');
const KEY = 'nmi-preview-demo-v1';
const fixture = { version: 1, profile: { name: 'Sample learner', country: 'Jordan', grade: 11, language: 'en', avatar: true, subjects: ['math'] }, chats: [] };
async function guard(page) { await page.route('**/*', route => new URL(route.request().url()).origin === 'http://127.0.0.1:8765' ? route.continue() : route.abort()); }
async function onboard(page, grade = '11') {
  await page.locator('#onboarding-name').fill('Sample learner'); await page.locator('#onboarding-country').selectOption('US'); await page.locator('#onboarding-grade').selectOption(grade); await page.locator('#onboarding-form button[type=submit]').click(); await expect(page.locator('#onboarding')).toBeHidden();
}
test.beforeEach(async ({ page }) => guard(page));
for (const language of ['ar', 'en']) for (const theme of ['light', 'dark']) {
  test(`onboarding ${language} ${theme}: validation, all grades, profile and return visit`, async ({ page }) => {
    await page.addInitScript(({language, theme}) => { localStorage.setItem('nmi-preview-language', language); localStorage.setItem('nmi-preview-theme', theme); }, { language, theme });
    await page.goto('/'); await expect(page.locator('#onboarding')).toBeVisible();
    expect(await page.locator('#onboarding-grade option:not([disabled])').evaluateAll(nodes => nodes.map(n => n.value))).toEqual(['9','10','11','12']);
    expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
    await page.screenshot({ path: `.cache/screenshots/onboarding-${language}-${theme}.png` });
    await page.keyboard.press('Escape'); await expect(page.locator('#onboarding')).toBeVisible();
    await page.locator('#onboarding-form button[type=submit]').click(); await expect(page.locator('#onboarding-name')).toBeFocused(); await expect(page.locator('#onboarding-name')).toHaveAttribute('aria-invalid','true');
    await page.locator('#onboarding-name').fill('Sample learner'); await page.locator('#onboarding-form button[type=submit]').click(); await expect(page.locator('#onboarding-country')).toBeFocused();
    await page.locator('#onboarding-country').selectOption('US'); await page.locator('#onboarding-form button[type=submit]').click(); await expect(page.locator('#onboarding-grade')).toBeFocused();
    await onboard(page, '9'); await expect(page.locator('#welcome')).toBeVisible();
    for (const grade of ['9','10','11','12']) {
      await page.locator('.sidebar a[href="#profile"]').click(); await page.locator('#edit-profile').click(); await onboard(page, grade);
      expect(await page.evaluate(key => JSON.parse(localStorage.getItem(key)).profile.grade, KEY)).toBe(Number(grade));
    }
    await page.locator('#subject-choices input[value=math]').check(); await page.locator('#edit-profile').click(); await page.locator('#onboarding-avatar').uncheck(); await page.locator('#onboarding-form button[type=submit]').click(); await expect(page.locator('#profile-avatar')).toBeHidden();
    await page.reload(); await expect(page.locator('#onboarding')).toBeHidden(); await expect(page.locator('#profile-name')).toHaveText('Sample learner'); await expect(page.locator('#subject-choices input[value=math]')).toBeChecked();
  });
}
for (const [name, raw] of [['corrupt','{bad'], ['wrong version',JSON.stringify({...fixture,version:2})], ['unsupported grade',JSON.stringify({...fixture,profile:{...fixture.profile,grade:8}})], ['oversized','x'.repeat(1000001)]]) {
  test(`storage ${name}: preserve original bytes and allow explicit reset`, async ({ page }) => {
    await page.addInitScript(({ key, raw }) => { if (!sessionStorage.getItem('seeded')) { localStorage.setItem(key,raw); sessionStorage.setItem('seeded','yes'); } }, { key: KEY, raw });
    await page.goto('/'); await onboard(page); await expect(page.locator('#storage-status')).toBeVisible();
    expect(await page.evaluate(key => localStorage.getItem(key),KEY)).toBe(raw);
    await page.locator('.sidebar a[href="#settings"]').click(); page.once('dialog',d => d.dismiss()); await page.locator('#reset-demo').click(); expect(await page.evaluate(key => localStorage.getItem(key),KEY)).toBe(raw);
    page.once('dialog',d => d.accept()); await page.locator('#reset-demo').click(); await expect(page.locator('#onboarding')).toBeVisible(); expect(await page.evaluate(key => localStorage.getItem(key),KEY)).toBeNull();
  });
}
test('storage quota failure keeps the in-memory demo usable', async ({ page }) => {
  await page.addInitScript(() => { Storage.prototype.setItem = () => { throw new DOMException('Full','QuotaExceededError'); }; });
  await page.goto('/'); await onboard(page); await expect(page.locator('#storage-status')).toBeVisible(); await page.locator('#question').fill('Sample question'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
});
test('storage another tab cannot be silently overwritten', async ({ page, context }) => {
  await page.goto('/'); await onboard(page);
  const second = await context.newPage(); await guard(second); await second.goto('/');
  await second.locator('#question').fill('A sample in tab two'); await second.locator('#question').press('Enter'); await expect(second.locator('.assistant-message')).toHaveCount(1);
  await expect(page.locator('#storage-status')).toBeVisible(); await page.locator('#question').fill('Different sample in tab one'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
  const saved = await page.evaluate(key => JSON.parse(localStorage.getItem(key)).chats, KEY); expect(saved).toHaveLength(1); expect(saved[0].messages[0].text).toBe('A sample in tab two'); await second.close();
});
test('browser restart restores onboarding, preferences and conversations', async () => {
  const directory = fs.mkdtempSync(path.resolve('.cache/browser-tmp/restart-'));
  const options = { executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, chromiumSandbox: true, viewport: { width: 1440, height: 900 } };
  let context = await chromium.launchPersistentContext(directory, options);
  try {
    let page = context.pages()[0]; await guard(page); await page.goto('http://127.0.0.1:8765/'); await page.locator('#onboarding-language').selectOption('en'); await onboard(page,'12'); await page.locator('#theme').click();
    await page.locator('#question').fill('A sample question about fractions'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
    await context.close(); context = await chromium.launchPersistentContext(directory, options); page = context.pages()[0]; await guard(page); await page.goto('http://127.0.0.1:8765/');
    await expect(page.locator('#onboarding')).toBeHidden(); await expect(page.locator('html')).toHaveAttribute('lang','en'); await expect(page.locator('html')).toHaveAttribute('data-theme','dark'); await expect(page.locator('#history-list .history-link')).toHaveCount(4);
    await page.locator('#history-list a[href="#chat/local-1"]').click(); await expect(page.locator('.student-bubble')).toHaveText('A sample question about fractions'); await expect(page.locator('.assistant-message')).toHaveCount(1);
    await page.locator('.sidebar a[href="#profile"]').click(); await expect(page.locator('#profile-name')).toHaveText('Sample learner'); await expect(page.locator('#profile-meta')).toContainText('Grade 12');
    await page.screenshot({path:'.cache/screenshots/restored-profile.png'});
  } finally { await context.close(); }
});
