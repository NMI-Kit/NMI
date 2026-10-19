const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const ORIGIN='http://127.0.0.1:8771';

test('Claude in main chat: unlock, Arabic/English, themes, context, usage, errors and persistence',async({page})=>{
  const errors=[],external=[];let posts=0;
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/*',route=>{
    const url=new URL(route.request().url());
    if(url.origin!==ORIGIN){external.push(url.origin);return route.abort();}
    if(url.pathname==='/api/chat')posts++;
    return route.continue();
  });
  await page.goto('/#local-access=incomplete');
  await page.locator('#language').selectOption('en');
  await expect(page.locator('#live-status')).toContainText('incomplete');
  await page.goto('/#local-access=synthetic-local-unlock-not-a-real-secret');
  await expect(page).toHaveURL(ORIGIN+'/');
  await expect(page.locator('#live-gate')).not.toContainText('private');
  await page.locator('#open-live').click();
  // Units are asked only for Israel from Grade 10, next to the grade.
  await expect(page.locator('#live-units-field')).toBeHidden();
  await expect(page.locator('#live-subject-field')).toBeHidden();
  await expect(page.locator('#live-grade option')).toHaveText(['9','10','11','12']);
  await page.locator('#live-country').selectOption('IL');
  // Options come from the server's curriculum folders: math, grades 10-12, units 3/4/5.
  await expect(page.locator('#live-subject-field')).toBeVisible();
  await expect(page.locator('#live-subject option')).toHaveCount(1);
  await expect(page.locator('#live-subject')).toHaveValue('math');
  await expect(page.locator('#live-grade option')).toHaveText(['10','11','12']);
  await expect(page.locator('#live-units-field')).toBeVisible();
  await expect(page.locator('#live-units option')).toHaveCount(3);
  await page.locator('#live-grade').selectOption('10');
  await page.locator('#live-units').selectOption('4');
  await page.locator('#live-profile button').click();
  await expect(page.locator('#live-profile')).toBeHidden();
  expect((await (await page.request.get('/api/state')).json()).profile).toEqual({country:'IL',grade:10,subject:'math',units:4});
  await page.locator('#open-live').click();
  await expect(page.locator('#live-provider-field')).toHaveCount(0);
  await expect(page.locator('#live-signin')).toHaveCount(0);
  expect(await page.locator('select[id*="model"]').count()).toBe(0);
  await page.locator('#new-chat').click();
  await page.locator('#live-consent').check();
  let count=0;
  for(const language of ['en','ar'])for(const theme of ['light','dark']){
    await page.setViewportSize({width:theme==='light'?1280:1440,height:theme==='light'?800:900});
    await page.locator('#language').selectOption(language);
    if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme').click();
    await expect(page.locator('html')).toHaveAttribute('dir',language==='ar'?'rtl':'ltr');
    const message=language==='ar'?(theme==='light'?'لماذا السماء زرقاء؟':'مش فاهم، اشرح بمثال أبسط'):
      (theme==='light'?'Why do plants need sunlight?':'Could you explain that differently?');
    await page.locator('#live-intent').selectOption(theme==='dark'?'confusion':'question');
    await page.locator('#question').fill(message);await page.locator('#send').click();
    await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','true');
    await expect(page.locator('#messages article')).toHaveCount(++count*2);
    await expect(page.locator('#messages article').last()).toContainText('Synthetic Claude reply: '+message);
    await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','false');
    await expect(page.locator('#live-usage')).toContainText(new Intl.NumberFormat(language).format(120));
    await expect(page.locator('#live-usage')).toContainText(new Intl.NumberFormat(language).format(80));
    expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
    await page.screenshot({path:`.cache/screenshots/claude-${language}-${theme}.png`});
  }
  await page.reload();await expect(page.locator('#messages article')).toHaveCount(8);
  await page.locator('#language').selectOption('en');await page.locator('#live-consent').check();
  for(const [text,error] of [['__interrupted__','No valid tutor reply'],['__unauthorized__','Anthropic credential']]){
    await page.locator('#question').fill(text);await page.locator('#send').click();
    await expect(page.locator('#live-status')).toContainText(error);
    await expect(page.locator('#messages article')).toHaveCount(8);
    await expect(page.locator('#question')).toHaveValue(text);
    await expect(page.locator('#question-form')).toHaveAttribute('aria-busy','false');
  }
  expect(posts).toBe(6);
  const state=await page.evaluate(async()=> (await fetch('/api/state')).json());
  expect(state.history).toHaveLength(8);expect(state.attempts).toEqual([]);
  expect(state.claude_enabled).toBe(true);
  const storage=await page.evaluate(()=>JSON.stringify({...localStorage,...sessionStorage}));
  expect(storage).not.toContain('Synthetic Claude reply');expect(storage).not.toContain('synthetic-fixture-not-a-key');
  expect(errors).toEqual([]);expect(external).toEqual([]);
});

test('a failed live adapter cannot produce demo fallback',async({page})=>{
  await page.route('**/live.js',route=>route.abort());await page.goto('/');
  await page.locator('#language').selectOption('en');
  await page.locator('#question').fill('Any normal question');await page.locator('#send').click();
  await expect(page.locator('#form-status')).toContainText('connection did not start');
  await expect(page.locator('#messages article')).toHaveCount(0);
});
