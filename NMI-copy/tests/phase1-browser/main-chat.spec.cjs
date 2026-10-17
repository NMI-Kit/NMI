const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const ORIGIN='http://127.0.0.1:8768';
const CAPABILITY='synthetic-local-unlock-not-a-real-secret';

test('main chat: unlock, mocked official OAuth, persistence, locales, timeouts and no fallback',async({page,browser})=>{
  const errors=[],external=[];let authorization,posts=0;
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/*',route=>{
    const url=new URL(route.request().url());
    if(url.origin==='https://auth.openai.com'&&url.pathname==='/api/accounts/authorize'){
      authorization=url;return route.fulfill({contentType:'text/html',body:'<title>Offline OAuth fixture</title>'});
    }
    if(url.origin!==ORIGIN){external.push(url.origin);return route.abort();}
    if(url.pathname==='/api/chat')posts++;
    return route.continue();
  });
  await page.setViewportSize({width:1440,height:900});
  await page.goto('/#local-access=incomplete');
  await page.locator('#language').selectOption('en');
  await expect(page.locator('#live-status')).toContainText('incomplete');
  await expect(page).toHaveURL(ORIGIN+'/');
  await page.goto('/#local-access='+CAPABILITY);
  await expect(page.locator('#live-gate')).not.toContainText('private');
  expect(await page.evaluate(async()=> (await fetch('/api/state')).status)).toBe(200);
  await page.locator('#open-live').click();
  await page.locator('#live-profile button').click();
  await expect(page.locator('#live-profile')).toBeHidden();
  await page.locator('#open-live').click();
  await page.locator('#live-signin').click();
  await expect(page).toHaveURL(/auth\.openai\.com/);
  expect(authorization.searchParams.get('code_challenge_method')).toBe('S256');
  const callback=new URL(authorization.searchParams.get('redirect_uri'));
  callback.searchParams.set('state',authorization.searchParams.get('state'));
  callback.searchParams.set('code','synthetic-browser-code');callback.searchParams.set('client_id','oaiapp_browser');
  await page.goto(callback.href);await expect(page).toHaveURL(ORIGIN+'/');
  await page.locator('#open-live').click();await page.locator('#live-models').click();
  await expect(page.locator('#live-auth-status')).toContainText('Connected');
  await expect(page.locator('#live-provider-field')).toBeHidden();
  await expect(page.locator('#live-model')).toHaveCount(0);
  await page.locator('#new-chat').click();await page.locator('#live-consent').check();
  let count=0;
  for(const language of ['en','ar'])for(const theme of ['light','dark']){
    await page.setViewportSize({width:theme==='light'?1280:1440,height:theme==='light'?800:900});
    await page.locator('#language').selectOption(language);
    if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme').click();
    await expect(page.locator('html')).toHaveAttribute('dir',language==='ar'?'rtl':'ltr');
    const message=language==='ar'
      ? (theme==='light'?'ما معنى الكسر؟':'مش فاهم، ممكن مثال أصغر؟')
      : (theme==='light'?'Why do plants need light?':'Could you give me a simpler example?');
    await page.locator('#live-intent').selectOption(theme==='dark'?'confusion':'question');
    await page.locator('#question').fill(message);await page.locator('#send').click();
    await expect(page.locator('#messages article')).toHaveCount(++count*2);
    await expect(page.locator('#messages article').last()).toHaveText('NMISynthetic response to: '+message);
    await expect(page.locator('#question')).toHaveValue('');
    await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','false');
    const box=await page.locator('#question-form').boundingBox();expect(box.y+box.height).toBeLessThanOrEqual(page.viewportSize().height);
    expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
    await page.screenshot({path:`.cache/screenshots/phase1-${language}-${theme}.png`});
  }
  await page.locator('#language').selectOption('en');
  await page.locator('a[href="#progress"]').first().click();await page.locator('#history-list a').click();
  await expect(page.locator('#messages article')).toHaveCount(8);
  await page.reload();await expect(page.locator('#messages article')).toHaveCount(8);
  await page.locator('#live-consent').check();
  let rejectRefresh=false;
  await page.route('**/api/state',route=>rejectRefresh?route.abort():route.continue());
  await page.locator('#question').fill('Saved before refresh failed');rejectRefresh=true;
  await page.locator('#send').click();
  await expect(page.locator('#messages article')).toHaveCount(10);
  await expect(page.locator('#live-status')).toContainText('reply was saved');
  rejectRefresh=false;await page.locator('#live-refresh').click();
  await expect(page.locator('#messages article')).toHaveCount(10);
  await page.locator('#question').fill('__interrupted__');await page.locator('#send').click();
  await expect(page.locator('#live-status')).toContainText('No valid tutor reply');
  await expect(page.locator('#question')).toHaveValue('__interrupted__');
  await expect(page.locator('#messages article')).toHaveCount(10);
  await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','false');

  const other=await browser.newContext();const otherPage=await other.newPage();
  await otherPage.goto(ORIGIN+'/#local-access='+CAPABILITY);
  await otherPage.locator('#language').selectOption('en');
  await expect(otherPage.locator('#live-status')).toContainText('another browser session');
  await other.close();

  await page.clock.install();
  let release;
  await page.route('**/api/chat',async route=>{await new Promise(resolve=>{release=resolve;});await route.abort();});
  await page.locator('#question').fill('Uncertain transport');await page.locator('#send').click();
  await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','true');
  await page.clock.runFor(150010);
  await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','false');
  await expect(page.locator('#live-retry')).toBeVisible();
  await expect(page.locator('#question')).toHaveValue('Uncertain transport');
  release();await page.locator('#live-retry').click();
  await expect(page.locator('#live-status')).toContainText('No saved receipt');
  expect(posts).toBe(6); // Read-only reconciliation does not resend the seventh request.
  const persisted=await page.evaluate(async()=>{const v=await(await fetch('/api/state')).json();return {history:v.history,attempts:v.attempts};});
  expect(persisted.history).toHaveLength(10);expect(persisted.attempts).toEqual([]);
  const storage=await page.evaluate(()=>JSON.stringify({...localStorage}));
  expect(storage).not.toContain('Synthetic response');expect(storage).not.toContain('SYNTHETIC_BROWSER');
  expect(errors).toEqual([]);expect(external).toEqual([]);
});

test('failed live script cannot fall back to scripted demo replies',async({page})=>{
  await page.route('**/live.js',route=>route.abort());
  await page.goto('/');await page.locator('#language').selectOption('en');
  await page.locator('#question').fill('A genuine tutor question');await page.locator('#send').click();
  await expect(page.locator('#form-status')).toContainText('connection did not start');
  await page.evaluate(()=>requestReply('math'));
  await expect(page.locator('#messages article')).toHaveCount(0);
  expect(await page.evaluate(()=>pending)).toBeNull();
});
