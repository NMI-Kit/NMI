const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
test('private-link recovery, session restoration and sign-in-only UI',async({page,context,browser})=>{
  const errors=[],forbidden=[];let claims=0;
  page.on('pageerror',error=>errors.push(error.message));
  await context.route('**/*',route=>{
    const url=new URL(route.request().url());
    if(url.origin!=='http://127.0.0.1:8769'||url.pathname.startsWith('/api/chatgpt/')||url.pathname==='/api/chat') {
      forbidden.push(url.pathname);return route.abort();
    }
    if(url.pathname==='/api/session')claims++;
    return route.continue();
  });
  await page.setViewportSize({width:1440,height:900});
  await page.goto('/');
  await expect(page.locator('#question-form')).toBeVisible();
  await page.locator('#language').selectOption('en');
  await expect(page.locator('#live-provider')).toHaveValue('chatgpt');
  await expect(page.locator('#live-signin')).toBeDisabled();
  // Same-document navigation must process the link without a reload.
  await page.evaluate(()=>{location.hash='local-access=incomplete';});
  await expect(page.locator('#live-status')).toContainText('incomplete');
  expect(claims).toBe(0);
  await page.evaluate(()=>{location.hash='local-access=synthetic-stale-launch-capability';});
  await expect(page.locator('#live-status')).toContainText('another launch');
  await expect(page.locator('#live-status')).toBeVisible();
  await expect(page.locator('#live-profile')).toBeHidden();
  await page.evaluate(()=>{location.hash='local-access=synthetic-local-unlock-not-a-real-secret';});
  await expect(page.locator('#live-signin')).toBeEnabled();
  await expect(page.locator('#live-gate')).toContainText('Tutoring requests are disabled');
  await page.locator('#open-live').click();
  await expect(page.locator('#live-profile')).toBeVisible();
  await expect(page.locator('#live-status')).toHaveText('');
  await expect(page).toHaveURL('http://127.0.0.1:8769/#settings');
  expect(claims).toBe(2);
  // An old test server's cookie must not replace this port's owner session.
  await context.addCookies([{name:'nmi_local_session_8770',value:'synthetic-other-server',url:'http://127.0.0.1:8769/'}]);
  await page.reload();
  await expect(page.locator('#live-signin')).toBeEnabled();
  await page.locator('#open-live').click();
  await expect(page.locator('#live-profile')).toBeVisible();
  // An old unauthenticated bootstrap response must not overwrite a newer unlock.
  let firstState=true,releaseState;
  const heldState=new Promise(resolve=>{releaseState=resolve;});
  await page.route('**/api/state',async route=>{
    if(!firstState)return route.continue();
    firstState=false;await heldState;
    return route.fulfill({status:401,contentType:'application/json',body:JSON.stringify({error:'access',message:'Synthetic stale response'})});
  });
  await page.reload();
  await expect.poll(()=>firstState).toBe(false);
  await page.evaluate(()=>{location.hash='local-access=synthetic-local-unlock-not-a-real-secret';});
  await expect(page.locator('#live-signin')).toBeEnabled();
  const staleResponse=page.waitForResponse(response=>response.url().endsWith('/api/state') && response.status()===401);
  releaseState();await staleResponse;
  await expect(page.locator('#live-status')).toHaveText('');
  await expect(page.locator('#live-signin')).toBeEnabled();
  await page.unroute('**/api/state');
  // Lost/blocked cookie after accepting a link must display a visible diagnosis.
  await page.route('**/api/state',route=>route.fulfill({status:401,contentType:'application/json',body:JSON.stringify({error:'access',message:'Synthetic session rejection'})}));
  await page.evaluate(()=>{location.hash='local-access=synthetic-local-unlock-not-a-real-secret';});
  await expect(page.locator('#live-status')).toContainText('browser session could not be verified');
  await expect(page.locator('#live-signin')).toBeDisabled();
  await page.unroute('**/api/state');
  await page.reload();
  await expect(page.locator('#live-signin')).toBeEnabled();
  for(const language of ['en','ar']) for(const theme of ['light','dark']) {
    await page.locator('#language').selectOption(language);
    if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme').click();
    await expect(page.locator('html')).toHaveAttribute('dir',language==='ar'?'rtl':'ltr');
    await expect(page.locator('#live-gate')).toContainText(language==='ar'?'طلبات التعليم معطّلة':'Tutoring requests are disabled');
    await expect(page.locator('#live-signin')).toBeEnabled();
    await expect(page.locator('#send')).toBeDisabled();
    expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
    await page.screenshot({path:`.cache/screenshots/unlock-${language}-${theme}.png`});
  }
  const state=await page.evaluate(async()=>await(await fetch('/api/state')).json());
  expect(state.profile).toBeNull();expect(state.history).toEqual([]);expect(state.attempts).toEqual([]);
  const other=await browser.newContext();
  try {
    const stranger=await other.newPage();
    await stranger.goto('http://127.0.0.1:8769/#local-access=synthetic-local-unlock-not-a-real-secret');
    await expect(stranger.locator('#live-status')).toBeVisible();
    await expect(stranger.locator('#live-signin')).toBeDisabled();
  } finally {await other.close();}
  expect(errors).toEqual([]);expect(forbidden).toEqual([]);
});
