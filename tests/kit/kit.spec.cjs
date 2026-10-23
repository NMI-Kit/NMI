'use strict';
// The kit page on an iPhone width, an Android width and a desktop width. Static files only, no network but the local server.
const { test, expect, devices } = require('@playwright/test');

const iphone = devices['iPhone 13'];
const pixel = devices['Pixel 7'];
const profiles = {
  iphone: { viewport: iphone.viewport, userAgent: iphone.userAgent, deviceScaleFactor: iphone.deviceScaleFactor, isMobile: true, hasTouch: true },
  android: { viewport: pixel.viewport, userAgent: pixel.userAgent, deviceScaleFactor: pixel.deviceScaleFactor, isMobile: true, hasTouch: true },
  desktop: { viewport: { width: 1280, height: 900 } }
};

async function noSideScroll(page, label) {
  const sizes = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
  expect(sizes.scroll, label + ' horizontal scroll').toBeLessThanOrEqual(sizes.inner);
}

async function bigTargets(page, selector, label) {
  const small = await page.$$eval(selector, (nodes) => nodes.filter((n) => n.offsetParent !== null && n.getBoundingClientRect().height < 44).map((n) => n.textContent.trim().slice(0, 30)));
  expect(small, label + ' touch targets under 44px').toEqual([]);
}

// clipboard and share are mocked: the page must copy first, then call share with the same text
async function mockShare(page, behaviour) {
  await page.addInitScript((b) => {
    window.__copied = [];
    window.__shared = [];
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: (t) => { window.__copied.push(t); return Promise.resolve(); } } });
    if (b === 'none') Object.defineProperty(navigator, 'share', { configurable: true, value: undefined });
    else Object.defineProperty(navigator, 'share', { configurable: true, value: (d) => {
      window.__shared.push(d);
      return b === 'cancel' ? Promise.reject(new DOMException('cancelled', 'AbortError')) : Promise.resolve();
    } });
  }, behaviour);
}

async function walkToReady(page, { grade = 'العاشر', units = '3 وحدات', mode = 'practice', topics = ['النموذج الخطي'], custom = [] } = {}) {
  await page.goto('/index.html');
  await expect(page.getByRole('heading', { name: 'شو مستواك؟' })).toBeVisible();
  await expect(page.locator('#next-1')).toBeDisabled();
  await page.getByRole('button', { name: 'رياضيات' }).click();
  await page.getByRole('button', { name: grade, exact: true }).click();
  await page.getByRole('group', { name: 'الوحدات' }).getByRole('button', { name: units }).click();
  await page.locator('#next-1').click();
  await expect(page.getByRole('heading', { name: 'شو بدك تراجع؟' })).toBeVisible();
  await expect(page.locator('#next-2')).toBeDisabled();
  for (const title of topics) await page.getByLabel(title, { exact: true }).check();
  for (const text of custom) {
    await page.locator('#custom-input').fill(text);
    await page.locator('#custom-add').click();
  }
  await page.locator('#next-2').click();
  await expect(page.getByRole('heading', { name: 'شو بدك تعمل؟' })).toBeVisible();
  await page.locator(`button[data-mode="${mode}"]`).click();
  await expect(page.getByRole('heading', { name: 'جاهز' })).toBeVisible();
}

for (const [name, profile] of Object.entries(profiles)) {
  test.describe(name, () => {
    test.use(profile);

    test('four steps in order, back button, no side scroll, big targets', async ({ page }) => {
      await page.goto('/index.html');
      await expect(page).toHaveTitle('عدّة NMI');
      await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
      await expect(page.locator('#progress')).toHaveText('الخطوة 1 من 4');
      await noSideScroll(page, name + ' step 1');
      await bigTargets(page, 'button, a.linkbtn', name + ' step 1');
      await expect(page.locator('#back')).toBeHidden();

      await page.getByRole('button', { name: 'رياضيات' }).click();
      await page.getByRole('button', { name: 'العاشر', exact: true }).click();
      // the example bank only covers grade 10: grades 11 and 12 are tagged "تجريبي"
      await expect(page.getByRole('group', { name: 'الوحدات' }).getByText('تجريبي')).toHaveCount(0);
      await page.getByRole('button', { name: 'الحادي عشر' }).click();
      await expect(page.getByRole('group', { name: 'الوحدات' }).getByText('تجريبي')).toHaveCount(3);
      await page.getByRole('button', { name: 'العاشر', exact: true }).click();
      await page.getByRole('group', { name: 'الوحدات' }).getByRole('button', { name: '3 وحدات' }).click();
      await expect(page.getByRole('heading', { name: 'مستوى هدف (اختياري)' })).toBeVisible();
      await page.locator('#next-1').click();

      await expect(page.locator('#progress')).toHaveText('الخطوة 2 من 4');
      await noSideScroll(page, name + ' step 2');
      await bigTargets(page, 'button, label.topic', name + ' step 2');
      await page.getByLabel('النموذج الخطي', { exact: true }).check();
      await page.getByLabel('الإحصاء', { exact: true }).check();
      await expect(page.locator('#next-2')).toBeEnabled();
      await page.getByLabel('الإحصاء', { exact: true }).uncheck();
      await page.locator('#next-2').click();

      await expect(page.locator('#progress')).toHaveText('الخطوة 3 من 4');
      await expect(page.locator('button.mode')).toHaveCount(4);
      expect(await page.$$eval('button.mode .mode-title', (n) => n.map((x) => x.textContent))).toEqual(['افهم', 'تدرّب', 'امتحان تجريبي', 'خطة']);
      expect(await page.$$eval('button.mode', (n) => n.map((x) => x.dataset.mode))).toEqual(['explain', 'practice', 'mock', 'plan']);
      await noSideScroll(page, name + ' step 3');
      await bigTargets(page, 'button.mode', name + ' step 3');
      // the title and its description are two lines, the description smaller (they used to be glued together)
      for (const box of await page.locator('button.mode').all()) {
        const title = await box.locator('.mode-title').boundingBox();
        const note = await box.locator('.mode-note').boundingBox();
        expect(note.y, 'description under the title').toBeGreaterThanOrEqual(title.y + title.height - 1);
        const sizes = await box.evaluate((el) => [parseFloat(getComputedStyle(el.querySelector('.mode-title')).fontSize), parseFloat(getComputedStyle(el.querySelector('.mode-note')).fontSize)]);
        expect(sizes[1], 'description font smaller than the title').toBeLessThan(sizes[0]);
      }
      await expect(page.locator('button.mode[data-mode="explain"] .mode-note')).toHaveText('شرح موضوع خطوة خطوة.');
      await expect(page.locator('button.mode[data-mode="plan"] .mode-note')).toHaveText('خطة مراجعة لامتحانك بالأيام.');

      if (name === 'desktop') {
        await expect(page.locator('#back')).toBeHidden();  // the steps are all on the page, nothing to go back to
        await expect(page.getByLabel('النموذج الخطي', { exact: true })).toBeChecked();
      } else {
        await page.locator('#back').click();
        await expect(page.getByRole('heading', { name: 'شو بدك تراجع؟' })).toBeVisible();
        await expect(page.getByLabel('النموذج الخطي', { exact: true })).toBeChecked();  // the choice is kept
        await page.locator('#next-2').click();
      }
      await page.locator('button[data-mode="practice"]').click();

      await expect(page.locator('#progress')).toHaveText('الخطوة 4 من 4');
      await noSideScroll(page, name + ' step 4');
      await bigTargets(page, 'button, a.linkbtn, summary', name + ' step 4');
      await expect(page.locator('#summary')).toContainText('رياضيات، الصف العاشر، 3 وحدات');
      await expect(page.locator('#summary')).toContainText('موضوع واحد • تدرّب');
      await expect(page.locator('#open-app')).toHaveText('افتح بتطبيق الذكاء الاصطناعي');
      await expect(page.locator('#copy')).toHaveText('انسخ');
      const links = await page.$$eval('.apps a', (a) => a.map((x) => [x.textContent, x.href, x.target, x.rel]));
      expect(links).toEqual([['ChatGPT', 'https://chatgpt.com/', '_blank', 'noopener noreferrer'],
        ['Claude', 'https://claude.ai/new', '_blank', 'noopener noreferrer'],
        ['Gemini', 'https://gemini.google.com/app', '_blank', 'noopener noreferrer']]);
      await expect(page.getByText('صوّر حلّك على الورقة وابعته بالتطبيق.')).toBeVisible();
      await expect(page.getByText('بدك تتدرّب على امتحان كامل؟ نزّله وارفعه للأداة.')).toBeVisible();
      await expect(page.locator('#exams-link')).toHaveAttribute('href', 'https://meyda.education.gov.il/');
      await expect(page.locator('#exams-link')).toHaveText('امتحانات رسمية سابقة');
      // one link to the exams, the ministry site, and nothing else about exams
      expect(await page.$$eval('a[href]', (a) => a.map((x) => x.href).filter((h) => /education\.gov\.il|exam|bagrut/i.test(h)))).toEqual(['https://meyda.education.gov.il/']);
    });

    test('the ready screen shows the real prompt: chosen topics, the example, no ids', async ({ page }) => {
      await walkToReady(page, { topics: ['النموذج الخطي', 'الاحتمال'] });
      await page.locator('summary').click();
      const text = await page.locator('#preview').innerText();
      expect(text).toContain('الوحدات: 3');
      expect(text).toContain('الوضع اللي اختاره: تدرّب\n');
      expect(text).toContain('المواضيع اللي بدو يراجعها: الاحتمال، النموذج الخطي');  // the curriculum order
      expect(text).toContain('بصندوق 12 كرة');  // the example of the first chosen topic (probability)
      expect(text).not.toContain('شركتين تاكسي');
      expect(text).not.toMatch(/m\d+-\d+-\d+/);
      expect(text).not.toContain('ملف');
      await expect(page.locator('#length')).toContainText('حرف');
      await noSideScroll(page, name + ' preview');
    });

    test('the main button copies first and then shares the same text', async ({ page }) => {
      await mockShare(page, 'ok');
      await walkToReady(page);
      await page.locator('#open-app').click();
      await expect(page.locator('#status')).toContainText('تم');
      const { copied, shared } = await page.evaluate(() => ({ copied: window.__copied, shared: window.__shared }));
      expect(copied).toHaveLength(1);
      expect(shared).toHaveLength(1);
      expect(shared[0].text).toBe(copied[0]);
      expect(copied[0]).toContain('== الطالب ==');
    });

    for (const behaviour of ['cancel', 'none']) {
      test(`share ${behaviour === 'cancel' ? 'cancelled' : 'not supported'}: the prompt is copied and the page says so`, async ({ page }) => {
        await mockShare(page, behaviour);
        await walkToReady(page);
        await page.locator('#open-app').click();
        await expect(page.locator('#status')).toHaveText('انسخنا البرومبت، افتح التطبيق والصقه');
        const copied = await page.evaluate(() => window.__copied);
        expect(copied).toHaveLength(1);
        expect(copied[0]).toContain('== المصادر ==');
      });
    }

    test('the copy button copies the prompt', async ({ page }) => {
      await mockShare(page, 'ok');
      await walkToReady(page, { mode: 'explain' });
      await page.locator('#copy').click();
      await expect(page.locator('#status')).toHaveText('تم النسخ.');
      const copied = await page.evaluate(() => window.__copied);
      expect(copied).toHaveLength(1);
      expect(copied[0]).toContain('الوضع اللي اختاره: افهم');
      expect(copied[0].trim().split('\n').pop()).toBe('ابدأ مباشرة بشرح النموذج الخطي.');
      expect(copied[0]).not.toContain('-- دليل أنماط الامتحانات لمستواك --');  // "افهم" has no patterns guide
    });

    test('"all topics" is the own level only; target topics are ticked one by one; too long is a warning', async ({ page }) => {
      await page.goto('/index.html');
      await page.getByRole('button', { name: 'رياضيات' }).click();
      await page.getByRole('button', { name: 'العاشر', exact: true }).click();
      await page.getByRole('group', { name: 'الوحدات' }).getByRole('button', { name: '3 وحدات' }).click();
      await page.getByRole('group', { name: 'مستوى هدف' }).getByRole('button', { name: '5 وحدات' }).click();
      await expect(page.getByRole('group', { name: 'مستوى هدف' }).getByRole('button', { name: '4 وحدات' })).toBeVisible();
      await page.locator('#next-1').click();
      await expect(page.getByRole('heading', { name: 'مواضيع مستوى الهدف (5 وحدات)' })).toBeVisible();
      await page.locator('#all-topics').click();
      await expect(page.locator('input[data-topic]')).toHaveCount(14 + 13);
      await expect(page.locator('input[data-topic^="m10-3"]:checked')).toHaveCount(14);
      await expect(page.locator('input[data-topic^="m10-5"]:checked')).toHaveCount(0);  // the target topics are not part of "all"
      await page.locator('input[data-topic="m10-3-04"]').uncheck();
      await expect(page.locator('#all-topics')).toHaveAttribute('aria-pressed', 'false');
      await page.locator('input[data-topic="m10-3-04"]').check();
      await expect(page.locator('#all-topics')).toHaveAttribute('aria-pressed', 'true');
      await page.locator('input[data-topic="m10-5-02"]').check();
      await expect(page.locator('#all-topics')).toHaveAttribute('aria-pressed', 'true');
      await page.locator('#all-topics').click();  // off: clears the own level, keeps the target topic
      await expect(page.locator('input[data-topic^="m10-3"]:checked')).toHaveCount(0);
      await expect(page.locator('input[data-topic="m10-5-02"]')).toBeChecked();
      await page.locator('#all-topics').click();
      await page.locator('#next-2').click();
      await page.locator('button[data-mode="explain"]').click();
      await expect(page.locator('#too-long')).toHaveCount(0);  // a whole level and one target topic still fit
      await expect(page.locator('#summary')).toContainText('(هدف: 5 وحدات)');
      await expect(page.locator('#summary')).toContainText('موضوع');
      // every target topic as well: too long, a warning that does not block
      await page.goto('/index.html');
      await page.getByRole('button', { name: 'رياضيات' }).click();
      await page.getByRole('button', { name: 'العاشر', exact: true }).click();
      await page.getByRole('group', { name: 'الوحدات' }).getByRole('button', { name: '3 وحدات' }).click();
      await page.getByRole('group', { name: 'مستوى هدف' }).getByRole('button', { name: '5 وحدات' }).click();
      await page.locator('#next-1').click();
      await page.locator('#all-topics').click();
      for (const box of await page.locator('input[data-topic^="m10-5"]').all()) await box.check();
      await page.locator('#next-2').click();
      await page.locator('button[data-mode="practice"]').click();
      await expect(page.locator('#too-long')).toBeVisible();
      await expect(page.locator('#too-long')).toContainText('اخترت مواضيع كتير');
      await expect(page.locator('#summary')).toContainText('كل المواضيع + 13 موضوع من الهدف');
      await expect(page.locator('#open-app')).toBeEnabled();
    });

    test('topics the student adds: add, delete, the limit of 5, 60 characters, plain text, and they reach the prompt', async ({ page }) => {
      const dialogs = [];
      page.on('dialog', (d) => { dialogs.push(d.message()); d.dismiss(); });
      await page.goto('/index.html');
      await page.getByRole('button', { name: 'رياضيات' }).click();
      await page.getByRole('button', { name: 'العاشر', exact: true }).click();
      await page.getByRole('group', { name: 'الوحدات' }).getByRole('button', { name: '3 وحدات' }).click();
      await page.locator('#next-1').click();
      await expect(page.getByRole('heading', { name: 'ضيف موضوع مش موجود بالقائمة' })).toBeVisible();
      await expect(page.locator('#custom-add')).toHaveText('ضيف');
      await expect(page.locator('#next-2')).toBeDisabled();
      // an empty name is refused
      await page.locator('#custom-add').click();
      await expect(page.locator('#custom-msg')).toHaveText('اكتب اسم الموضوع أول.');
      // a custom topic alone is enough to go on, it shows as a ticked checkbox with a delete button
      await page.locator('#custom-input').fill('المعادلات التربيعية');
      await page.locator('#custom-add').click();
      await expect(page.locator('#custom-list input[type="checkbox"]')).toHaveCount(1);
      await expect(page.locator('#custom-list input[type="checkbox"]')).toBeChecked();
      await expect(page.locator('#custom-list')).toContainText('المعادلات التربيعية');
      await expect(page.locator('#custom-list button.del')).toHaveText('حذف');
      await expect(page.locator('#custom-input')).toHaveValue('');
      await expect(page.locator('#next-2')).toBeEnabled();
      // the same topic twice is refused
      await page.locator('#custom-input').fill('المعادلات التربيعية');
      await page.locator('#custom-add').click();
      await expect(page.locator('#custom-msg')).toHaveText('هالموضوع مضاف.');
      // 60 characters at most
      expect(await page.locator('#custom-input').getAttribute('maxlength')).toBe('60');
      await page.locator('#custom-input').fill('س'.repeat(80));
      expect((await page.locator('#custom-input').inputValue()).length).toBe(60);
      await page.locator('#custom-add').click();
      // html is only text
      await page.locator('#custom-input').fill('<img src=x onerror=alert(1)>');
      await page.locator('#custom-add').click();
      await expect(page.locator('#custom-list')).toContainText('<img src=x onerror=alert(1)>');
      await expect(page.locator('#custom-list img')).toHaveCount(0);
      // up to 5
      for (const text of ['ج', 'د']) {
        await page.locator('#custom-input').fill(text);
        await page.locator('#custom-add').click();
      }
      await expect(page.locator('#custom-list li')).toHaveCount(5);
      await expect(page.locator('#custom-input')).toBeDisabled();
      await expect(page.locator('#custom-add')).toBeDisabled();
      await expect(page.locator('#custom-msg')).toContainText('وصلت للحد');
      // delete one: the field is back
      await page.locator('#custom-list li').nth(1).locator('button.del').click();  // the 60-character one
      await expect(page.locator('#custom-list li')).toHaveCount(4);
      await expect(page.locator('#custom-input')).toBeEnabled();
      // untick one: it stays on the list but not in the prompt
      await page.locator('#custom-list li').nth(3).locator('input').uncheck();  // the last one, 'د'
      await page.locator('#next-2').click();
      await page.locator('button[data-mode="explain"]').click();
      await expect(page.locator('#summary')).toContainText('3 من عندك');
      await page.locator('summary').click();
      const text = await page.locator('#preview').innerText();
      expect(text).toContain('-- مواضيع كتبها الطالب بنفسه --');
      expect(text).toContain('- المعادلات التربيعية');
      expect(text).toContain('- <img src=x onerror=alert(1)>');
      const lines = text.split(/\r?\n/);
      expect(lines).toContain('- ج');
      expect(lines).not.toContain('- د');
      expect(text).toContain('هاي مواضيع كتبها الطالب بنفسه. ممكن تكون من منهاجه بكلام تاني');
      expect(text).not.toContain('ما تحكي إنها من منهاجه');
      expect(text).toContain('المواضيع اللي بدو يراجعها: المعادلات التربيعية، <img src=x onerror=alert(1)>، ج\n');
      expect(text).not.toContain('(ما اختار الطالب');
      await expect(page.locator('#preview img')).toHaveCount(0);
      expect(dialogs).toEqual([]);
    });

    test('a level without the example bank is tagged experimental on the ready screen', async ({ page }) => {
      await walkToReady(page, { grade: 'الحادي عشر', units: '4 وحدات', topics: ['الاحتمال'] });
      await expect(page.locator('#experimental')).toContainText('تجريبي');
      await expect(page.locator('#experimental')).toContainText('نمط الامتحان');
    });
  });
}

test.describe('desktop layout', () => {
  test.use(profiles.desktop);
  test('the steps stay on one page, and the manifest and icon load', async ({ page, request }) => {
    await walkToReady(page);
    await expect(page.locator('section.step')).toHaveCount(4);
    await expect(page.locator('#back')).toBeHidden();
    await noSideScroll(page, 'desktop');
    const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href');
    const manifest = await (await request.get('/' + manifestHref)).json();
    expect(manifest.display).toBe('standalone');
    for (const icon of manifest.icons) expect((await request.get('/' + icon.src)).ok(), icon.src).toBeTruthy();
    expect((await request.get('/apple-touch-icon.png')).ok()).toBeTruthy();
  });

  test('changing the level on the one page hides the later steps until "next"', async ({ page }) => {
    await walkToReady(page);
    await page.getByRole('group', { name: 'الوحدات' }).getByRole('button', { name: '4 وحدات' }).click();
    await expect(page.locator('section.step')).toHaveCount(1);
    await expect(page.locator('#next-1')).toBeEnabled();
  });
});

test.describe('failures', () => {
  test.use(profiles.android);
  test('a missing data file shows a clear message, not a blank page', async ({ page }) => {
    await page.route('**/data.json', (route) => route.fulfill({ status: 404, body: 'no' }));
    await page.goto('/index.html');
    await expect(page.getByRole('alert')).toContainText('ما قدرنا نحمّل المنهاج');
  });
});
