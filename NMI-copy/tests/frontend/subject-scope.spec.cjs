const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const fixture = {version:1,profile:{name:'Scope demo',country:'United States',countryCode:'US',grade:11,language:'en',avatar:true,subjects:['math','science','code','writing']},chats:[]};
test.beforeEach(async ({page}) => {
  await page.route('**/*',route => new URL(route.request().url()).origin === 'http://127.0.0.1:8765' ? route.continue() : route.abort());
  await page.addInitScript(fixture => { if (!localStorage.getItem('nmi-preview-demo-v1')) localStorage.setItem('nmi-preview-demo-v1',JSON.stringify(fixture)); },fixture);
});
for (const language of ['ar','en']) for (const theme of ['light','dark']) {
  test(`scope ${language} ${theme}: three academic subjects, unrestricted saved chat, languages`, async ({page}) => {
    await page.setViewportSize({width:1440,height:900}); await page.goto('/'); await page.locator('#language').selectOption(language);
    await page.goto('/#settings'); await page.locator('#settings-theme').selectOption(theme);
    expect(await page.locator('#language option').evaluateAll(nodes=>nodes.map(n=>n.value))).toEqual(['ar','en']);
    for (const route of ['progress','curriculum','profile']) {
      await page.locator(`.sidebar a[href="#${route}"]`).click();
      const ids = route === 'profile' ? await page.locator('#subject-choices input').evaluateAll(nodes=>nodes.map(n=>n.value)) : await page.locator(`#${route}-subjects [data-academic-subject]`).evaluateAll(nodes=>nodes.map(n=>n.dataset.academicSubject));
      expect(ids).toEqual(['math','physics','chemistry']);
      expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
      await page.screenshot({path:`.cache/screenshots/scope-${language}-${theme}-${route}.png`});
    }
    await expect(page.locator('#legacy-interests')).toBeVisible();
    for (const topic of ['Tell me about history','Help me write a sentence','Explain a Python function','Tell me about music']) {
      await page.locator('#new-chat').click(); await page.locator('#question').fill(topic); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
      await expect(page.locator('#messages progress, #messages .learning-note')).toHaveCount(0); await expect(page.locator('.conversation-only')).toBeVisible();
    }
    await page.reload(); await expect(page.locator('.student-bubble')).toHaveText('Tell me about music'); await expect(page.locator('#onboarding')).toBeHidden();
    const state = await page.evaluate(()=>JSON.parse(localStorage.getItem('nmi-preview-demo-v1')));
    expect(state.chats).toHaveLength(4); expect(state.profile.subjects).toEqual(fixture.profile.subjects); expect(state).not.toHaveProperty('progress'); expect(state).not.toHaveProperty('mastery');
    await page.locator('.sidebar a[href="#progress"]').click(); await page.locator('#sample-toggle').click();
    expect(await page.locator('#sample-progress [data-academic-subject]').evaluateAll(nodes=>[...new Set(nodes.map(n=>n.dataset.academicSubject))])).toEqual(['math','physics','chemistry']);
    await page.locator('.sidebar a[href="#library"]').click();
    for (const subject of ['physics','chemistry']) {
      await page.locator(`#academic-prompts [data-academic-subject="${subject}"]`).click(); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1); await expect(page.locator('.learning-note')).toHaveCount(1);
      await page.locator('.sidebar a[href="#library"]').click();
    }
    await page.locator('.sidebar a[href="#profile"]').click(); await page.locator('#edit-profile').click();
    expect(await page.locator('#onboarding-country option:not([disabled])').evaluateAll(nodes=>nodes.map(n=>n.value))).toEqual(['US','GB','CA','DE','CH','SG','AU','NL','QA','AE']);
    for (const code of ['US','GB','CA','DE','CH','SG','AU','NL','QA','AE']) await page.locator('#onboarding-country').selectOption(code);
    await page.locator('#onboarding-form button[type=submit]').click(); await page.reload();
    expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('nmi-preview-demo-v1')).profile.countryCode)).toBe('AE');
  });
}
test('animations run for new replies and dialogs, never replay old messages on language change', async ({page}) => {
  await page.emulateMedia({reducedMotion:'no-preference'}); await page.goto('/');
  await page.locator('#question').fill('Explain physics'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
  await expect(page.locator('.assistant-message')).toHaveCSS('animation-name','arrive'); await expect(page.locator('.assistant-message')).toHaveCSS('animation-duration','0.22s');
  await page.locator('#language').selectOption('en'); await expect(page.locator('.assistant-message')).toHaveCSS('animation-name','none');
  await page.locator('#search-chats').click(); await expect(page.locator('#search-dialog')).toHaveCSS('animation-name','dialog-enter'); await page.keyboard.press('Escape');
  await page.locator('.sidebar a[href="#settings"]').click(); await expect(page.locator('#settings')).toHaveCSS('animation-name','arrive');
  await page.emulateMedia({reducedMotion:'reduce'}); await page.locator('#search-chats').click(); await expect(page.locator('#search-dialog')).toHaveCSS('animation-name','none'); await page.keyboard.press('Escape');
  await expect(page.locator('#settings')).toHaveCSS('animation-name','none');
  await page.locator('#new-chat').click(); await page.locator('#question').fill('Explain chemistry'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1); await expect(page.locator('.assistant-message')).toHaveCSS('animation-name','none');
});
test('switching from math to another topic never inherits academic presentation or scores', async ({page}) => {
  await page.goto('/'); await page.locator('#question').fill('Explain fractions'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
  await page.locator('#question').fill('Now help me write a sentence'); await page.locator('#question').press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(2);
  await expect(page.locator('.assistant-message').last().locator('progress, .learning-note')).toHaveCount(0); await expect(page.locator('.assistant-message').last().locator('.conversation-only')).toBeVisible();
  await page.reload(); await expect(page.locator('.assistant-message')).toHaveCount(2);
  expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('nmi-preview-demo-v1')).chats[0].messages.map(m=>m.kind).filter(Boolean))).toEqual(['math','writing']);
  expect(await page.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem('nmi-preview-demo-v1'))).sort())).toEqual(['chats','profile','version']);
});
test('legacy returning country is preserved when profile edit is cancelled', async ({page}) => {
  await page.addInitScript(()=>localStorage.setItem('nmi-preview-demo-v1',JSON.stringify({version:1,profile:{name:'Legacy demo',country:'Jordan',grade:10,language:'en',avatar:false,subjects:['science','writing']},chats:[]})));
  await page.goto('/#profile'); await expect(page.locator('#onboarding')).toBeHidden(); await expect(page.locator('#profile-meta')).toContainText('Jordan');
  await page.locator('#edit-profile').click(); await expect(page.locator('#legacy-country-note')).toBeVisible(); await expect(page.locator('#onboarding-country')).toHaveValue('');
  await page.locator('#onboarding-form button[type=submit]').click(); await expect(page.locator('#onboarding-country')).toHaveAttribute('aria-invalid','true');
  await page.locator('#cancel-onboarding').click(); expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('nmi-preview-demo-v1')).profile.country)).toBe('Jordan');
});

test('approved ribbon identity loads in both themes, stays unmirrored, and respects reduced motion', async ({page}) => {
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.goto('/');
  await expect(page.locator('.brand')).toHaveAccessibleName('NMI');
  await expect(page.locator('.brand')).toHaveText('');
  await expect(page.locator('.welcome-identity')).toHaveText('');
  await expect(page.locator('.welcome-identity img')).toHaveCSS('animation-name','brand-enter');
  for (const theme of ['light','dark']) {
    await page.locator('.sidebar a[href="#settings"]').click();
    await page.locator('#settings-theme').selectOption(theme);
    for (const language of ['ar','en']) {
      await page.locator('#language').selectOption(language);
      await page.locator('#new-chat').click();
      await expect(page.locator('.brand img')).toHaveAttribute('src',`assets/nmi-mark-${theme}.svg`);
      await expect(page.locator('.brand img')).toHaveCSS('transform','none');
      await expect(page.locator('#nmi-favicon')).toHaveAttribute('href',`assets/nmi-mark-${theme}.svg`);
      expect(await page.locator('[data-nmi-mark]').evaluateAll(images=>images.every(img=>img.complete && img.naturalWidth>0))).toBe(true);
      await page.screenshot({path:`.cache/screenshots/identity-${language}-${theme}.png`});
    }
  }
  await page.locator('#question').fill('Explain fractions');
  await page.locator('#question').press('Enter');
  await expect(page.locator('.assistant-heading img')).toHaveAttribute('src','assets/nmi-mark-dark.svg');
  await page.locator('#theme').click();
  await expect(page.locator('.assistant-heading img')).toHaveAttribute('src','assets/nmi-mark-light.svg');
  for (const asset of ['light','dark','white','black']) {
    const response=await page.request.get(`/assets/nmi-mark-${asset}.svg`);
    expect(response.status()).toBe(200);
    const svg=await response.text();
    expect(svg).not.toMatch(/<script|<image|<foreignObject|<text\b|onload=|https?:\/\/(?!www\.w3\.org)/i);
  }
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.locator('#new-chat').click();
  await expect(page.locator('.welcome-identity img')).toHaveCSS('animation-name','none');
});
