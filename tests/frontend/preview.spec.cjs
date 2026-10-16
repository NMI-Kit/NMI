const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('preview/preview.js', 'utf8');
const translations = vm.runInNewContext(source.slice(0, source.indexOf('const $')) + '; COPY;');
const demoState = { version: 1, profile: { name: 'Demo learner', country: 'Jordan', grade: 10, language: 'ar', avatar: true, subjects: [] }, chats: [] };
async function completeOnboarding(page, grade = '10') {
  await page.locator('#onboarding-name').fill('Demo learner');
  await page.locator('#onboarding-country').selectOption('US');
  await page.locator('#onboarding-grade').selectOption(grade);
  await page.locator('#onboarding-form button[type="submit"]').click();
  await expect(page.locator('#onboarding')).not.toBeVisible();
}

async function languageSetup(page, language, theme) {
  await page.addInitScript(({ language, theme }) => {
    localStorage.setItem('nmi-preview-language', language);
    localStorage.setItem('nmi-preview-theme', theme);
  }, { language, theme });
}
async function noViolations(page) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(results.violations).toEqual([]);
}
async function composerVisible(page) {
  const box = await page.locator('#question-form').boundingBox();
  expect(box.y).toBeGreaterThan(0);
  expect(box.y + box.height).toBeLessThanOrEqual(page.viewportSize().height);
}

test.beforeEach(async ({ page }, testInfo) => {
  await page.route('**/*', route => new URL(route.request().url()).origin === 'http://127.0.0.1:8765' ? route.continue() : route.abort());
  if (!/^(onboarding|storage|browser restart)/.test(testInfo.title)) await page.addInitScript(state => { if (!localStorage.getItem('nmi-preview-demo-v1')) localStorage.setItem('nmi-preview-demo-v1', JSON.stringify(state)); }, demoState);
});

for (const language of ['ar', 'en']) {
  for (const theme of ['light', 'dark']) {
    for (const [width, height] of [[1280, 800], [1440, 900], [1920, 1080]]) {
      test(`${language} ${theme} ${width}: welcome, chat, math, and accessibility`, async ({ page }) => {
        const errors = [], outside = []; const copy = translations[language];
        page.on('pageerror', e => errors.push(e.message));
        page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
        page.on('request', request => { if (new URL(request.url()).origin !== 'http://127.0.0.1:8765') outside.push(request.url()); });
        await page.setViewportSize({ width, height }); await languageSetup(page, language, theme); await page.goto('/');
        await expect(page.locator('html')).toHaveAttribute('lang', language);
        await expect(page.locator('html')).toHaveAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
        await expect(page.getByRole('heading', { name: copy.welcome, exact: true })).toBeVisible();
        await expect(page.locator('#messages')).toBeHidden();
        await expect(page.locator('#history-list .history-link')).toHaveCount(3);
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        await composerVisible(page); await noViolations(page);
        await page.screenshot({ path: `.cache/screenshots/chat-first-${language}-${theme}-${width}-welcome.png` });
        await page.keyboard.press('Tab'); await expect(page.locator('.skip-link')).toBeFocused();
        await page.keyboard.press('Enter'); await expect(page.locator('#main')).toBeFocused();
        await page.getByRole('button', { name: copy.send, exact: true }).click();
        await expect(page.getByRole('textbox', { name: copy.questionLabel, exact: true })).toHaveAttribute('aria-invalid', 'true');
        await page.getByRole('button', { name: copy.suggestMath, exact: true }).click();
        await expect(page.locator('#question')).toHaveValue(copy.mathPrompt);
        await page.locator('#question').press('Enter');
        await expect(page.locator('.assistant-message')).toHaveCount(1);
        await expect(page.locator('#welcome')).toBeHidden();
        await expect(page.locator('.student-bubble')).toHaveText(copy.mathPrompt);
        await expect(page.locator('math')).toHaveAttribute('dir', 'ltr');
        await expect(page.locator('math mfrac')).toHaveCount(5);
        await expect(page.locator('.learning-note')).not.toHaveAttribute('open', '');
        await composerVisible(page); await noViolations(page);
        await page.screenshot({ path: `.cache/screenshots/chat-first-${language}-${theme}-${width}-chat.png` });
        await page.getByRole('button', { name: copy.hint, exact: true }).click();
        await expect(page.locator('.assistant-message')).toHaveCount(2);
        await expect(page.getByText(copy.mathHint, { exact: true })).toBeVisible();
        await page.getByRole('button', { name: copy.check, exact: true }).click();
        await expect(page.locator('.assistant-message')).toHaveCount(3);
        await expect(page.getByText(copy.mathCheck, { exact: true })).toBeVisible();
        await page.locator('#question').fill('Keep this draft');
        await page.locator('#language').selectOption(language === 'ar' ? 'en' : 'ar'); await expect(page.locator('#question')).toHaveValue('Keep this draft');
        await expect(page.locator('html')).toHaveAttribute('dir', language === 'ar' ? 'ltr' : 'rtl');
        await page.locator('#theme').click(); await expect(page.locator('html')).toHaveAttribute('data-theme', theme === 'light' ? 'dark' : 'light');
        expect(errors).toEqual([]); expect(outside).toEqual([]);
      });
    }
  }
}

for (const language of ['ar', 'en']) {
  for (const theme of ['light', 'dark']) {
    test(`${language} ${theme}: navigation, search, settings, code, and contextual notes`, async ({ page }) => {
      const copy = translations[language]; await page.setViewportSize({width:1440,height:900}); await languageSetup(page, language, theme); await page.goto('/');
      for (const id of ['progress', 'curriculum', 'library', 'profile', 'settings']) {
        await page.locator(`.sidebar a[href="#${id}"]`).click();
        await expect(page.locator(`#${id}`)).toBeVisible(); await expect(page.locator('#composer-dock')).toBeHidden(); await noViolations(page);
        await page.screenshot({ path: `.cache/screenshots/chat-first-${language}-${theme}-${id}.png` });
      }
      await page.locator('.sidebar a[href="#progress"]').click(); await page.locator('#sample-toggle').click(); await expect(page.locator('#sample-progress')).toBeVisible(); await noViolations(page); await page.locator('#sample-progress').screenshot({ path: `.cache/screenshots/chat-first-${language}-${theme}-sample.png` });
      await page.locator('#search-chats').click(); await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.locator('#chat-search')).toBeFocused();
      await page.locator('#chat-search').fill('zzzzzz-no-match'); await expect(page.locator('#search-status')).toHaveText(copy.noResults);
      await page.locator('#chat-search').fill(copy.codeTitle); await expect(page.locator('#search-results a')).toHaveCount(1);
      await noViolations(page); await page.locator('#search-results a').click(); await expect(page.getByRole('dialog')).toBeHidden();
      await expect(page.locator('pre')).toHaveCSS('direction', 'ltr');
      await expect(page.locator('code')).toContainText('def greet(name):'); await noViolations(page);
      await page.screenshot({ path: `.cache/screenshots/chat-first-${language}-${theme}-code.png` });
      await expect(page.locator('#messages .learning-note, #messages progress')).toHaveCount(0); await expect(page.locator('.conversation-only')).toBeVisible();
      await page.evaluate(() => { window.__copied = ''; Object.defineProperty(navigator, 'clipboard', { value: { writeText: async text => { window.__copied = text; } }, configurable: true }); });
      await page.getByRole('button', { name: copy.copyCode, exact: true }).click();
      expect(await page.evaluate(() => window.__copied)).toContain('def greet');
      await page.locator('#search-chats').click(); await page.keyboard.press('Escape'); await expect(page.locator('#search-chats')).toBeFocused();
      await page.locator('#new-chat').click(); await expect(page.locator('#welcome')).toBeVisible();
      await page.locator('#toggle-sidebar').click(); await expect(page.locator('#toggle-sidebar')).toHaveAttribute('aria-expanded', 'false');
      await page.locator('#toggle-sidebar').click(); await expect(page.locator('#toggle-sidebar')).toHaveAttribute('aria-expanded', 'true');
    });
  }
}

test('composer keyboard behavior, safe text, stop, and independent in-tab chats', async ({ page }) => {
  await page.goto('/');
  const input = page.locator('#question');
  const payload = '<img src=x onerror="alert(1)">';
  await input.fill(payload); await input.press('Shift+Enter'); await input.press('x');
  await expect(input).toHaveValue(payload + '\nx');
  await input.press('Enter'); await page.locator('#stop').click();
  await expect(page.locator('.assistant-message')).toHaveCount(0); await expect(page.locator('.student-bubble')).toHaveText(payload + '\nx');
  await expect(page.locator('#messages img')).toHaveCount(0);
  await input.fill('First draft'); await page.locator('#new-chat').click(); await expect(input).toHaveValue('');
  await input.fill('A completely different topic'); await input.press('Enter');
  await expect(page.locator('.assistant-message')).toHaveCount(1);
  await page.locator('#history-list a[href="#chat/local-1"]').click(); await expect(input).toHaveValue('First draft');
  await expect(page.locator('.student-bubble')).toHaveText(payload + '\nx');
  await expect(page.locator('.student-bubble')).toHaveCount(1);
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual(['nmi-preview-demo-v1']);
  page.on('dialog', dialog => dialog.accept());
  await page.reload(); await expect(page.locator('#history-list .history-link')).toHaveCount(5); await expect(page.locator('.student-bubble')).toHaveText(payload + '\nx');
});

test('long message, IME composition, repeated submit, and composer remains reachable', async ({ page }) => {
  await page.goto('/');
  const input = page.locator('#question');
  await input.fill('A'.repeat(4000));
  await input.dispatchEvent('keydown', { key: 'Enter', isComposing: true });
  await expect(page.locator('.student-message')).toHaveCount(0);
  await input.press('Enter'); await input.press('Enter');
  await expect(page.locator('.student-message')).toHaveCount(1);
  await expect(page.locator('.assistant-message')).toHaveCount(1);
  await composerVisible(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('language/theme settings and demo chats persist', async ({ page }) => {
  await page.goto('/#settings');
  await page.locator('#settings-language').selectOption('en'); await page.locator('#settings-theme').selectOption('dark');
  await page.locator('#new-chat').click(); await page.locator('#question').fill('A question'); await page.locator('#question').press('Enter');
  await expect(page.locator('.assistant-message')).toHaveCount(1); await page.reload();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en'); await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.locator('.student-message')).toHaveCount(1);
  expect(await page.evaluate(() => Object.keys(localStorage).sort())).toEqual(['nmi-preview-demo-v1', 'nmi-preview-language', 'nmi-preview-theme']);
});

test('blocked storage, reduced motion, and keyboard settings work', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('Blocked', 'SecurityError'); } }));
  await page.goto('/');
  await completeOnboarding(page);
  await page.locator('#language').focus(); await page.keyboard.press('ArrowDown'); await page.keyboard.press('Enter');
  await page.locator('#theme').focus(); await page.keyboard.press('Space');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en'); await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.locator('#send')).toHaveCSS('transition-duration', '0s');
  await page.locator('#question').fill('An idea'); await page.locator('#question').press('Enter');
  await expect(page.locator('.assistant-message')).toHaveCount(1);
  await expect(page.locator('.assistant-message')).toHaveCSS('animation-name', 'none');
});

test('skip link preserves utility route and stale deep links recover', async ({ page }) => {
  await page.goto('/#progress'); await page.locator('.skip-link').focus(); await page.keyboard.press('Enter');
  await expect(page.locator('#progress')).toBeVisible(); await expect(page.locator('#main')).toBeFocused();
  await page.goto('/#chat/local-999'); await expect(page.locator('#welcome')).toBeVisible();
});

test('translations have exact parity, valid Arabic and no missing UI labels', async ({ page }) => {
  expect(Object.keys(translations.ar).sort()).toEqual(Object.keys(translations.en).sort());
  expect(translations.ar.welcome).toMatch(/[\u0600-\u06ff]/);
  for (const copy of Object.values(translations)) for (const value of Object.values(copy)) expect(value).not.toMatch(/\?{2,}|undefined/);
  await page.goto('/');
  expect(await page.locator('[data-i18n]').evaluateAll(nodes => nodes.every(n => n.textContent.trim().length > 0))).toBe(true);
});

test('preview server still refuses backend files and traversal', async ({ request }) => {
  for (const url of ['/ai_test.py', '/student.json', '/.env', '/../AGENTS.md', '/assets/']) expect((await request.get(url)).status()).toBe(404);
});
