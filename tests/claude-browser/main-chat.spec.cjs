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
  // The only country is written in the form, not chosen from a list; grade and units start empty.
  await expect(page.locator('#live-country')).toHaveCount(0);
  await expect(page.locator('#live-country-text')).toHaveValue('Israel');
  await expect(page.locator('#live-country-text')).toHaveJSProperty('readOnly',true);
  await expect(page.locator('#live-grade')).toHaveValue('');
  await expect(page.locator('#live-units')).toHaveValue('');
  await expect(page.locator('#live-target-field')).toBeHidden();
  await expect(page.locator('#live-profile-save')).toBeDisabled();
  await expect(page.locator('#send')).toBeDisabled();
  await expect(page.locator('#live-edit-profile')).toBeVisible();
  // Options come from the server's curriculum folders: math, grades 10-12, units 3/4/5.
  await expect(page.locator('#live-subject-field')).toBeVisible();
  expect(await values('#live-subject')).toEqual(['','math']);
  await expect(page.locator('#live-subject')).toHaveValue('math');  // the only subject is selected for the student
  expect(await values('#live-grade')).toEqual(['','10','11','12']);
  await page.locator('#live-grade').selectOption('10');
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
  await expect(page.locator('#live-country-text')).toHaveValue('Israel');
  for(const [id,value] of [['subject','math'],['grade','10'],['units','3'],['target-units','5']])await expect(page.locator('#live-'+id)).toHaveValue(value);
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
    // Tutor replies are rendered as Markdown blocks; the student's own messages stay plain text.
    await expect(page.locator('#messages article[data-role="assistant"]').last().locator('.live-message-content.md')).toHaveCount(1);
    await expect(page.locator('#messages article[data-role="user"] .md')).toHaveCount(0);
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

test('tutor replies render as safe Markdown: structure, RTL text with LTR equations, no raw HTML or script links', async ({page}) => {
  await page.goto('/');
  const sample = [
    '## الفكرة ببساطة', 'الميل **معدل التغيّر** و `y = mx + b` وكمان *إيه*', '',
    '## المصطلحات', '- **المتغير**: رقم بيتغيّر', '- الثابت: رقم ما بيتغيّر', '',
    '1. أول خطوة', '2. تاني خطوة', '',
    '$$ y = 2x + 3 $$', 'x^2 + 3x = 5', 'المعادلة x + 1 = 3 هي مثال', '',
    '| الأسبوع | الموضوع |', '|---|---|', '| 1 | m10-3-12 **النموذج الخطي** |', '',
    '<script>window.hacked=1</script> <img src=x onerror="window.hacked=2"> <b>غامق خام</b>',
    '[رابط](https://example.com/a) و [سيئ](javascript:window.hacked=3) و [بيانات](data:text/html,x)',
    '---', 'سعر 5$ فقط'].join('\n');
  const facts = await page.evaluate(markdown => {
    const root = window.nmiRenderMarkdown(markdown);
    document.body.append(root);
    const direction = element => getComputedStyle(element).direction;
    const result = {
      headings: [...root.querySelectorAll('h3,h4,h5,h6')].map(h => [h.tagName, h.textContent, h.dir]),
      strong: [...root.querySelectorAll('strong')].map(n => n.textContent),
      code: [...root.querySelectorAll('code')].map(n => [n.textContent, n.dir]),
      em: [...root.querySelectorAll('em')].map(n => n.textContent),
      ul: [...root.querySelectorAll('ul > li')].map(n => n.textContent),
      ol: [...root.querySelectorAll('ol > li')].map(n => n.textContent),
      math: [...root.querySelectorAll('.md-math')].map(n => [n.textContent, n.dir, direction(n)]),
      th: [...root.querySelectorAll('th')].map(n => n.textContent),
      td: [...root.querySelectorAll('td')].map(n => n.textContent),
      tdStrong: root.querySelectorAll('td strong').length,
      dangerous: root.querySelectorAll('script,img,b,iframe,style,form,input').length,
      anchors: [...root.querySelectorAll('a')].map(a => [a.textContent, a.href, a.rel, a.target]),
      hr: root.querySelectorAll('hr').length,
      paragraphs: [...root.querySelectorAll('p')].map(n => [n.textContent, n.dir]),
      text: root.textContent,
      hacked: window.hacked,
      onerror: [...root.querySelectorAll('*')].some(n => n.getAttributeNames().some(name => name.startsWith('on'))),
    };
    root.remove();
    return result;
  }, sample);
  expect(facts.headings).toEqual([['H4', 'الفكرة ببساطة', 'auto'], ['H4', 'المصطلحات', 'auto']]);
  expect(facts.strong).toEqual(['معدل التغيّر', 'المتغير', 'النموذج الخطي']);
  expect(facts.code).toEqual([['y = mx + b', 'ltr']]);
  expect(facts.em).toEqual(['إيه']);
  expect(facts.ul).toEqual(['المتغير: رقم بيتغيّر', 'الثابت: رقم ما بيتغيّر']);
  expect(facts.ol).toEqual(['أول خطوة', 'تاني خطوة']);
  // Equations get their own line, left to right, even inside right-to-left text.
  expect(facts.math).toEqual([['y = 2x + 3', 'ltr', 'ltr'], ['x^2 + 3x = 5', 'ltr', 'ltr']]);
  expect(facts.paragraphs.map(p => p[0])).toContain('المعادلة x + 1 = 3 هي مثال');  // Arabic words: not an equation line
  expect(facts.paragraphs.every(p => p[1] === 'auto')).toBe(true);
  expect(facts.th).toEqual(['الأسبوع', 'الموضوع']);
  expect(facts.td).toEqual(['1', 'm10-3-12 النموذج الخطي']);
  expect(facts.tdStrong).toBe(1);
  expect(facts.hr).toBe(1);
  // Nothing from the reply becomes an element, an event handler or a script link.
  expect(facts.dangerous).toBe(0);
  expect(facts.onerror).toBe(false);
  expect(facts.hacked).toBeUndefined();
  expect(facts.text).toContain('<script>window.hacked=1</script>');
  expect(facts.text).toContain('<img src=x onerror="window.hacked=2">');
  expect(facts.text).toContain('<b>غامق خام</b>');
  expect(facts.anchors).toHaveLength(1);
  expect(facts.anchors[0][0]).toBe('رابط');
  expect(facts.anchors[0][1]).toBe('https://example.com/a');
  expect(facts.anchors[0][2]).toContain('noopener');
  expect(facts.text).toContain('سيئ (javascript:window.hacked=3)');
  expect(facts.text).toContain('بيانات (data:text/html,x)');
  expect(facts.text).toContain('سعر 5$ فقط');
  // Plain text, an empty reply and a very long line do not break the renderer.
  const edge = await page.evaluate(() => [window.nmiRenderMarkdown('').childElementCount, window.nmiRenderMarkdown('نص عادي').textContent,
    window.nmiRenderMarkdown('x'.repeat(20000)).textContent.length, window.nmiRenderMarkdown('|a|b|\n|--|--|').querySelectorAll('th').length]);
  expect(edge).toEqual([0, 'نص عادي', 20000, 2]);
});
