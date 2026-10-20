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
  const dialog=page.locator('#live-onboarding'), profile=async()=>(await (await page.request.get('/api/state')).json());
  const values=selector=>page.locator(selector).evaluate(select=>[...select.options].map(option=>option.value));
  // First visit, no profile: the profile dialog is the first thing, it cannot be dismissed, nothing is preselected,
  // and chatting is impossible until it is complete.
  await expect(dialog).toBeVisible();
  expect((await profile()).profile).toBeNull();
  expect((await profile()).profile_ready).toBe(false);
  await expect(page.locator('#live-profile-cancel')).toBeHidden();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeVisible();
  for(const id of ['country','grade'])await expect(page.locator('#live-'+id)).toHaveValue('');
  await expect(page.locator('#live-subject-field')).toBeHidden();
  await expect(page.locator('#live-units-field')).toBeHidden();
  await expect(page.locator('#live-target-field')).toBeHidden();
  await expect(page.locator('#live-profile-save')).toBeDisabled();
  await expect(page.locator('#send')).toBeDisabled();
  await expect(page.locator('#live-edit-profile')).toBeVisible();
  // A country without a curriculum cannot be saved; the student is told why.
  await page.locator('#live-country').selectOption('US');
  expect(await values('#live-grade')).toEqual(['','9','10','11','12']);
  await page.locator('#live-grade').selectOption('10');
  await expect(page.locator('#live-profile-error')).not.toHaveText('');
  await expect(page.locator('#live-profile-save')).toBeDisabled();
  await expect(page.locator('#live-units-field')).toBeHidden();
  // Israel: options come from the server's curriculum folders: math, grades 10-12, units 3/4/5. The grade is kept only if offered.
  await page.locator('#live-country').selectOption('IL');
  await expect(page.locator('#live-profile-error')).toHaveText('');
  await expect(page.locator('#live-subject-field')).toBeVisible();
  expect(await values('#live-subject')).toEqual(['','math']);
  await expect(page.locator('#live-subject')).toHaveValue('math');  // the only subject is selected for the student
  expect(await values('#live-grade')).toEqual(['','10','11','12']);
  await expect(page.locator('#live-grade')).toHaveValue('10');
  await expect(page.locator('#live-units-field')).toBeVisible();
  expect(await values('#live-units')).toEqual(['','3','4','5']);
  await expect(page.locator('#live-units')).toHaveValue('');
  await expect(page.locator('#live-target-field')).toBeHidden();
  await expect(page.locator('#live-profile-save')).toBeDisabled();  // units still missing
  await page.locator('#live-units').selectOption('3');
  await expect(page.locator('#live-target-field')).toBeVisible();
  expect(await values('#live-target-units')).toEqual(['','4','5']);  // only higher levels, empty = no move
  await page.locator('#live-target-units').selectOption('5');
  await expect(page.locator('#live-profile-save')).toBeEnabled();
  await page.locator('#live-profile-save').click();
  await expect(dialog).toBeHidden();
  expect((await profile()).profile).toEqual({country:'IL',grade:10,subject:'math',units:3,target_units:5});
  expect((await profile()).profile_ready).toBe(true);
  // The profile can be opened and edited at any time, with the saved values filled in.
  await page.locator('#live-edit-profile').click();
  await expect(dialog).toBeVisible();
  await expect(page.locator('#live-profile-cancel')).toBeVisible();
  for(const [id,value] of [['country','IL'],['subject','math'],['grade','10'],['units','3'],['target-units','5']])await expect(page.locator('#live-'+id)).toHaveValue(value);
  await page.locator('#live-profile-cancel').click();
  await expect(dialog).toBeHidden();
  await page.locator('#live-edit-profile').click();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();  // an edit can be dismissed
  expect((await profile()).profile.units).toBe(3);
  await page.locator('#live-edit-profile').click();
  await page.locator('#live-units').selectOption('4');
  expect(await values('#live-target-units')).toEqual(['','5']);
  await page.locator('#live-target-units').selectOption('');
  await page.locator('#live-profile-save').click();
  await expect(dialog).toBeHidden();
  expect((await profile()).profile).toEqual({country:'IL',grade:10,subject:'math',units:4});
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
