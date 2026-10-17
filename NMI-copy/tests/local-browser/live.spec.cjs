const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
test('Flask cannot generate a scripted reply if its live adapter fails to load',async({page})=>{
  let sends=0;
  await page.route('**/*',route=>{
    const url=new URL(route.request().url());
    if(url.origin!=='http://127.0.0.1:8767'||url.pathname==='/live.js')return route.abort();
    if(url.pathname==='/api/chat')sends++;
    return route.continue();
  });
  await page.setViewportSize({width:1440,height:900});
  await page.goto('/');
  await page.locator('#language').selectOption('en');
  await page.locator('#question').fill('Why is the sky blue?');
  await page.locator('#question').press('Enter');
  await expect(page.locator('#form-status')).toContainText('connection did not start');
  await expect(page.locator('#question')).toHaveValue('Why is the sky blue?');
  await expect(page.locator('.assistant-message')).toHaveCount(0);
  expect(sends).toBe(0);
});
test('local Flask chat: bilingual themes, consent, persistence, intent, failure and demo separation',async({page,browser})=>{
  const errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',route=>{if(new URL(route.request().url()).origin!=='http://127.0.0.1:8767'){external.push(route.request().url());return route.abort();}return route.continue();});
  await page.setViewportSize({width:1440,height:900});
  await page.goto('/#local-access=synthetic-local-unlock-not-a-real-secret');
  await expect(page.locator('#question-form')).toBeVisible();
  await page.locator('#open-live').click();
  await expect(page.locator('#onboarding')).toBeHidden();
  expect(page.url()).not.toContain('local-access');
  await page.locator('#live-country').selectOption('QA');await page.locator('#live-grade').selectOption('11');
  await page.locator('#live-profile button').click();
  await expect(page.locator('#send')).toBeDisabled();
  await page.locator('#live-consent').check();
  for(const language of ['ar','en']) for(const theme of ['light','dark']) {
    await page.setViewportSize(theme==='light'?{width:1280,height:800}:{width:1440,height:900});
    await page.locator('#language').selectOption(language);
    if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme').click();
    await expect(page.locator('html')).toHaveAttribute('dir',language==='ar'?'rtl':'ltr');
    if(language==='en' && theme==='dark')await page.route('**/api/chat',async route=>{await route.fetch();await route.abort('failed');},{times:1});
    await page.locator('#question').fill(language==='en' && theme==='light'?'Show safe text':'Explain addition');await page.locator('#send').click();
    if(language==='en' && theme==='dark') {await expect(page.locator('#live-retry')).toBeVisible();await page.locator('#live-retry').click();}
    await expect(page.locator('#question')).toHaveValue('');
    const composer=await page.locator('#question-form').boundingBox();expect(composer.y+composer.height).toBeLessThanOrEqual(page.viewportSize().height);
    if(language==='en' && theme==='light') {await expect(page.locator('#messages')).toContainText('<img src=x onerror=alert(1)>');await expect(page.locator('#messages img[src=x]')).toHaveCount(0);}
    expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
    await page.screenshot({path:`.cache/screenshots/local-${language}-${theme}.png`});
  }
  await expect(page.locator('#messages article')).toHaveCount(8);
  await page.locator('#live-intent').selectOption('answer');await page.locator('#question').fill('4');await page.locator('#send').click();
  await expect(page.locator('#question')).toHaveValue('');
  await expect(page.locator('#live-attempts')).toContainText('Recorded learning attempts: 1');
  expect(await page.evaluate(()=>localStorage.getItem('nmi-preview-demo-v1'))).toBeNull();
  await page.reload();await expect(page.locator('#onboarding')).toBeHidden();await expect(page.locator('#question-form')).toBeVisible();
  await expect(page.locator('#messages article')).toHaveCount(10);
  await expect(page.locator('#live-consent')).not.toBeChecked();await page.locator('#live-consent').check();
  await page.locator('#question').fill('__timeout__');await page.locator('#send').click();
  await expect(page.locator('#live-status')).toContainText('timed out');
  await expect(page.locator('#question')).toHaveValue('__timeout__');
  await expect(page.locator('#messages article')).toHaveCount(10);
  await expect(page.locator('#live-status')).not.toContainText('SYNTHETIC_PRIVATE');
  const stranger=await browser.newContext();const second=await stranger.newPage();await second.goto('/');
  const result=await second.evaluate(async()=>{const r=await fetch('/api/state');return r.status;});expect(result).toBe(401);await stranger.close();
  expect(await page.evaluate(()=>localStorage.getItem('nmi-preview-demo-v1'))).toBeNull();
  await expect(page.locator('#messages article')).toHaveCount(10);
  expect(errors).toEqual([]);expect(external).toEqual([]);
});
