/* Flask-only controller. Main NMI chat, server persistence, no demo fallback. */
(() => {
  'use strict';
  const COPY = {
    en: {
      connection:'Tutor connection', plan:'ChatGPT plan', api:'OpenAI API · separate billing', provider:'AI connection',
      claude:'Claude · Anthropic API', claudeDisabled:'Anthropic paid requests are disabled by the owner.',
      claudeModel:'The owner must configure a Claude model on the server.',
      claudeReady:'Claude is configured for approved requests. Availability is checked when you send.',
      claudeConsent:'I approve sending this message and recent learning context to Anthropic using paid Claude API credits. No automatic retry or provider fallback.',
      tokens:'Last reported Claude usage', inputTokens:'input', outputTokens:'output', cacheRead:'cache read', cacheWrite:'cache write', partialUsage:'Partial report; final usage may be higher.',
      signin:'Continue with ChatGPT', signout:'Sign out of ChatGPT', check:'Check tutor connection', usage:'Manage ChatGPT usage',
      access:'Open the private local link printed in the server terminal.', unlocking:'Unlocking this local session…',
      malformed:'The private link is incomplete. Copy the whole link from the current server terminal.',
      unlockFailed:'This link is from another launch or this server belongs to another browser session. Restart the server and use its new complete private link in one Chrome profile.',
      cookies:'Cookies could not be verified. Allow cookies for 127.0.0.1 and reopen the current private link. No new session was claimed.',
      cookieLost:'The link was accepted, but the browser session could not be verified. Allow cookies, restart the server and use its new link in the same Chrome profile.',
      signedOut:'Not connected. Continue with ChatGPT to authorize this local tutor.', connecting:'Connecting…', connected:'Connected to ChatGPT. The project owner configures the model in the terminal.',
      ready:'Connected. Ready for your approved tutoring request.', disabled:'Local session unlocked. Tutoring requests are disabled until the owner enables them.',
      unavailable:'ChatGPT sign-in is disabled for this launch.', limit:'The local request limit has been reached. No additional request will be sent.',
      generating:'Generating an answer…', completed:'Completed. Conversation saved locally.',
      failure:'Connection failed or timed out. Your draft remains here. Check the request status before sending again.',
      savedRefresh:'The reply was saved and is displayed below, but the latest connection status could not be refreshed.',
      uncertain:'The request outcome is not confirmed. Do not send another request. Check its saved status again or ask the owner to inspect it.',
      reconcile:'Check saved request status', refresh:'Refresh connection status', setup:'Local test profile',
      privacy:'Use fictional test information only. This local prototype has one owner and one saved conversation.',
      country:'Country of study', grade:'Grade', save:'Save local test profile', profileSaved:'Local test profile saved.',
      consent:'I approve sending this question and recent learning context to OpenAI using my ChatGPT plan allowance. No paid API fallback.',
      apiConsent:'I approve this separately billed OpenAI API request and sending this question and recent learning context to OpenAI.',
      validate:'Use a message of 1–4,000 characters.', user:'You', conversation:'Saved conversation',
      oneChat:'One local conversation. New conversations and pinning are not connected to the backend yet.',
      safety:'AI can make mistakes. No verified official curriculum is loaded. Local records are visible to people with access to this computer.',
      noScore:'No mastery scores are inferred from questions. Recorded learning attempts:',
      noHistory:'No saved conversation yet.', noSearch:'No matching saved conversation.',
      profileName:'Local learner', ask:'Question', answer:'Answer to an exercise', hint:'Request a hint', confusion:'I am confused', intent:'Message type',
      blocked:'Scripted replies are disabled here. Use the main composer after connecting the tutor.', local:'Local tutor',
      storage:'This conversation is saved on the local Flask server, separate from the static demo. No real replies are saved in browser demo storage.',
      readonly:'The existing profile is preserved. Profile editing and multiple conversations are pending.',
      missing:'No saved receipt was found yet. This does not prove that the request cannot still finish. Do not resend.',
      signoutDone:'Signed out locally. Check ChatGPT settings if remote revocation was not confirmed.'
    },
    ar: {
      connection:'اتصال المعلّم', plan:'خطة ChatGPT', api:'OpenAI API · فوترة منفصلة', provider:'اتصال الذكاء الاصطناعي',
      claude:'Claude · واجهة Anthropic', claudeDisabled:'عطّل صاحب المشروع طلبات Anthropic المدفوعة.',
      claudeModel:'يجب على صاحب المشروع إعداد نموذج Claude في الخادم.',
      claudeReady:'تم إعداد Claude للطلبات الموافق عليها. يُتحقّق من توفره عند الإرسال.',
      claudeConsent:'أوافق على إرسال هذه الرسالة وسياق التعلّم الأخير إلى Anthropic باستخدام رصيد Claude API المدفوع. لن تحدث إعادة محاولة تلقائية أو تحويل إلى خدمة بديلة.',
      tokens:'آخر استخدام مُبلّغ عنه من Claude', inputTokens:'إدخال', outputTokens:'إخراج', cacheRead:'قراءة التخزين المؤقت', cacheWrite:'كتابة التخزين المؤقت', partialUsage:'تقرير جزئي؛ قد يكون الاستخدام النهائي أعلى.',
      signin:'المتابعة باستخدام ChatGPT', signout:'تسجيل الخروج من ChatGPT', check:'التحقّق من اتصال المعلّم', usage:'إدارة استخدام ChatGPT',
      access:'افتح الرابط المحلي الخاص الظاهر في نافذة الخادم.', unlocking:'جارٍ فتح الجلسة المحلية…',
      malformed:'الرابط الخاص ناقص. انسخ الرابط كاملًا من نافذة الخادم الحالية.',
      unlockFailed:'الرابط يخص تشغيلًا آخر أو أن الخادم مرتبط بجلسة متصفح أخرى. أعد تشغيل الخادم وافتح رابطه الجديد كاملًا في ملف Chrome واحد.',
      cookies:'تعذّر التحقّق من ملفات الارتباط. اسمح بها للموقع 127.0.0.1 وأعد فتح الرابط الخاص الحالي. لم تُحجز جلسة جديدة.',
      cookieLost:'قُبل الرابط، لكن تعذّر التحقّق من جلسة المتصفح. اسمح بملفات الارتباط وأعد تشغيل الخادم وافتح رابطه الجديد في ملف Chrome نفسه.',
      signedOut:'غير متصل. تابع باستخدام ChatGPT للسماح لهذا المعلّم المحلي بالوصول.', connecting:'جارٍ الاتصال…', connected:'متصل بـ ChatGPT. يُعدّ صاحب المشروع النموذج من نافذة الخادم.',
      ready:'متصل. جاهز لطلب التعليم الذي وافقت عليه.', disabled:'الجلسة المحلية مفتوحة. طلبات التعليم معطّلة إلى أن يفعّلها صاحب المشروع.',
      unavailable:'تسجيل الدخول إلى ChatGPT معطّل في هذا التشغيل.', limit:'وصلت إلى حدّ الطلبات المحلية. لن يُرسَل طلب إضافي.',
      generating:'جارٍ إعداد الإجابة…', completed:'اكتمل الرد وحُفظت المحادثة محليًا.',
      failure:'تعذّر الاتصال أو انتهت مهلته. بقيت مسودتك هنا. تحقّق من حالة الطلب قبل الإرسال مجددًا.',
      savedRefresh:'حُفظ الرد ويظهر أدناه، لكن تعذّر تحديث حالة الاتصال الأخيرة.',
      uncertain:'لم تُؤكّد نتيجة الطلب. لا تُرسِل طلبًا آخر. تحقّق من حالته المحفوظة مجددًا أو اطلب من صاحب المشروع فحصها.',
      reconcile:'التحقّق من حالة الطلب المحفوظ', refresh:'تحديث حالة الاتصال', setup:'ملف اختبار محلي',
      privacy:'استخدم معلومات اختبار افتراضية فقط. يدعم هذا النموذج المحلي مستخدمًا واحدًا ومحادثة محفوظة واحدة.',
      country:'بلد الدراسة', grade:'الصف الدراسي', save:'حفظ ملف الاختبار المحلي', profileSaved:'حُفظ ملف الاختبار المحلي.',
      consent:'أوافق على إرسال هذا السؤال وسياق التعلّم الأخير إلى OpenAI باستخدام خطتي في ChatGPT. لن يحدث تحويل إلى API مدفوع.',
      apiConsent:'أوافق على هذا الطلب المدفوع منفصلًا عبر OpenAI API وعلى إرسال السؤال وسياق التعلّم الأخير إلى OpenAI.',
      validate:'استخدم رسالة من حرف واحد إلى 4000 حرف.', user:'أنت', conversation:'المحادثة المحفوظة',
      oneChat:'محادثة محلية واحدة. إنشاء محادثات إضافية وتثبيتها غير متصل بالخادم بعد.',
      safety:'قد يخطئ الذكاء الاصطناعي. لم يُحمّل منهج رسمي موثّق. يمكن لمن يصل إلى هذا الحاسوب الاطّلاع على السجلات المحلية.',
      noScore:'لا تُستنتج درجات إتقان من الأسئلة. محاولات التعلّم المسجّلة:',
      noHistory:'لا توجد محادثة محفوظة بعد.', noSearch:'لا توجد محادثة محفوظة مطابقة.',
      profileName:'المتعلّم المحلي', ask:'سؤال', answer:'إجابة عن تمرين', hint:'طلب تلميح', confusion:'لم أفهم', intent:'نوع الرسالة',
      blocked:'الردود التجريبية معطّلة هنا. استخدم مربع المحادثة الرئيسي بعد توصيل المعلّم.', local:'المعلّم المحلي',
      storage:'تُحفظ هذه المحادثة في خادم Flask المحلي منفصلةً عن المعاينة التجريبية. لا تُحفظ الردود الحقيقية في تخزين المعاينة بالمتصفح.',
      readonly:'الملف الحالي محفوظ. تعديل الملف وإضافة محادثات متعددة غير متاحين بعد.',
      missing:'لم يُعثر على سجل محفوظ للطلب بعد. قد يكون الطلب ما زال قيد التنفيذ. لا تُعِد الإرسال.',
      signoutDone:'تم تسجيل الخروج محليًا. راجع إعدادات ChatGPT إن لم يُؤكّد إلغاء الصلاحية عن بُعد.'
    }
  };
  const $ = s => document.querySelector(s);
  const lang = () => document.documentElement.lang === 'ar' ? 'ar' : 'en';
  const tr = key => COPY[lang()][key];
  const node = (tag, text, cls) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const signinLaunch = $('meta[name="nmi-chatgpt-signin"]')?.content === '1';
  const launchProvider = $('meta[name="nmi-provider"]')?.content;
  let state=null, csrf='', busy=false, pendingRequest=null, revision=0, unlocking=false;
  let statusKey='', statusText='', statusError=false, renderedSignature='';
  const question=$('#question'), form=$('#question-form');
  document.documentElement.dataset.nmiLive='true';
  $('#main').tabIndex=0;
  $('#onboarding').close();
  const connectionButton=node('button',undefined,'live-mode-button');connectionButton.id='open-live';connectionButton.type='button';$('.preferences').prepend(connectionButton);
  const banner=node('div',undefined,'live-banner');
  banner.innerHTML='<p id="live-gate"></p><p id="live-status" role="status"></p><button id="live-refresh" type="button" class="context-button"></button><button id="live-retry" type="button" class="context-button" hidden></button>';
  $('#main').before(banner);
  const usageNote=node('p',undefined,'page-note');usageNote.id='live-usage';usageNote.hidden=true;banner.append(usageNote);
  const connection=node('section',undefined,'live-connection');connection.id='live-connection';
  connection.innerHTML=`<h2 data-live="connection"></h2><div id="live-provider-field"><label for="live-provider" data-live="provider"></label><select id="live-provider"><option value="chatgpt" data-live="plan"></option><option value="api" data-live="api"></option></select></div>
    <div id="live-chatgpt"><p id="live-auth-status"></p><div class="live-auth-actions"><button id="live-signin" type="button" class="context-button" data-live="signin"></button><button id="live-models" type="button" class="context-button" data-live="check"></button><button id="live-signout" type="button" class="context-button" data-live="signout"></button></div><a href="https://chatgpt.com/settings/usage" target="_blank" rel="noopener noreferrer" data-live="usage"></a></div>
    <form id="live-profile" class="live-profile"><h3 data-live="setup"></h3><p data-live="privacy"></p><div class="field"><label for="live-country" data-live="country"></label><select id="live-country" required></select></div><div class="field"><label for="live-grade" data-live="grade"></label><select id="live-grade" required></select></div><button type="submit" class="primary-button" data-live="save"></button></form><p id="live-profile-note"></p>`;
  $('#settings').append(connection);
  const claudeOption=node('option');claudeOption.value='claude';claudeOption.dataset.live='claude';$('#live-provider').append(claudeOption);
  const consent=node('label',undefined,'live-consent');
  consent.innerHTML='<input id="live-consent" type="checkbox"><span id="live-consent-text"></span>';
  $('#question-form').before(consent);
  const intent=node('label',undefined,'live-intent');
  intent.innerHTML='<span class="sr-only" data-live="intent"></span><select id="live-intent"><option value="question" data-live="ask"></option><option value="answer" data-live="answer"></option><option value="hint" data-live="hint"></option><option value="confusion" data-live="confusion"></option></select>';
  $('.composer-mode').replaceWith(intent);
  const progress=node('p',undefined,'page-note');progress.id='live-attempts';$('#progress .empty-state').prepend(progress);

  function status(key='', error=false, text='') {statusKey=key;statusText=text;statusError=error;renderStatus();}
  function renderStatus() {const text=statusText || (statusKey?tr(statusKey):'');$('#live-status').textContent=text;$('#live-status').classList.toggle('error',statusError);$('#form-status').textContent=text;$('#form-status').classList.toggle('error',statusError);}
  // A browser deadline ends waiting, not the provider request. Never auto-resend.
  async function api(path, body, timeout=15000) {
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),timeout);
    try {
      const response=await fetch(path,{method:body===undefined?'GET':'POST',credentials:'same-origin',signal:controller.signal,
        headers:{'Content-Type':'application/json','X-NMI-CSRF':csrf,'X-NMI-Language':lang()},...(body===undefined?{}:{body:JSON.stringify(body)})});
      const data=await response.json();
      if(!response.ok){const e=new Error(data.message);e.code=data.error;throw e;}
      return data;
    } catch(error) {
      // DOMException.code is numeric (20 for abort), not a server error receipt.
      // Keep uncertain chat identity/draft instead of treating it as a rejection.
      if(error.name==='AbortError')throw new Error('Local request deadline exceeded');
      throw error;
    } finally {clearTimeout(timer);}
  }
  async function refresh() {
    const current=++revision;
    try {const value=await api('/api/state');if(current!==revision)return false;if(state&&state.provider!==value.provider)$('#live-consent').checked=false;state=value;csrf=value.csrf;return true;}
    catch(error){if(current!==revision)return false;if(error.code==='access'){state=null;csrf='';}throw error;}
    finally {if(current===revision)render();}
  }
  function chatVisible(){return !['#settings','#profile','#progress','#curriculum','#library'].includes(location.hash);}
  function openSettings(){location.hash='settings';connection.scrollIntoView({block:'nearest'});}
  function renderHistory() {
    const messages=state?.history || [], list=$('#history-list');list.replaceChildren();
    if(messages.length){const a=node('a',messages.find(m=>m.role==='user')?.content.slice(0,70)||tr('conversation'),'history-link');a.href='#chat/local';a.dir='auto';list.append(a);}
    else list.append(node('p',tr('noHistory'),'page-note'));
    $('#history-count').textContent=messages.length?'1':'0';$('.history-caption').textContent=tr('oneChat');
    const signature=JSON.stringify([messages,lang(),document.documentElement.dataset.theme]);
    if(signature!==renderedSignature){
      const target=$('#messages');target.replaceChildren();
      for(const message of messages){
        const article=node('article',undefined,'live-message');article.dataset.role=message.role;
        const heading=node('div',undefined,'assistant-heading');
        if(message.role==='assistant'){const mark=node('img');mark.src=`assets/nmi-mark-${document.documentElement.dataset.theme}.svg`;mark.width=25;mark.height=25;mark.alt='';heading.append(mark);}
        heading.append(node('strong',message.role==='assistant'?'NMI':tr('user')));article.append(heading);
        const content=node('div',message.content,'live-message-content');content.dir='auto';article.append(content);target.append(article);
      }
      renderedSignature=signature;
    }
    if(chatVisible()){
      $('#welcome').hidden=messages.length>0;$('#chat-view').hidden=!messages.length;
      $('#workspace').dataset.mode=messages.length?'chat':'welcome';$('#composer-dock').hidden=false;
    }
    $('#profile-history').textContent=messages.length?tr('conversation'):tr('noHistory');
  }
  function renderSearch(){
    const messages=state?.history||[], query=$('#chat-search').value.trim().toLocaleLowerCase(lang()), results=$('#search-results');results.replaceChildren();
    if(messages.length && messages.some(m=>m.content.toLocaleLowerCase(lang()).includes(query))){const a=node('a',tr('conversation'),'search-result');a.href='#chat/local';a.addEventListener('click',()=>$('#search-dialog').close());results.append(a);}
    $('#search-status').textContent=results.childElementCount?'':tr('noSearch');
  }
  function render(){
    const provider=state?.provider || launchProvider || (signinLaunch?'chatgpt':'api'), plan=provider==='chatgpt', claude=provider==='claude', auth=state?.chatgpt;
    document.querySelectorAll('[data-live]').forEach(n=>n.textContent=tr(n.dataset.live));
    connectionButton.textContent=tr('connection');$('#live-refresh').textContent=tr('refresh');$('#live-retry').textContent=tr('reconcile');
    $('#live-provider').value=provider;$('#live-provider-field').hidden=!state?.api_enabled||!!state?.provider_locked;
    claudeOption.hidden=!claude;claudeOption.disabled=!claude;
    $('#live-provider').disabled=busy||!!pendingRequest||!state;$('#live-provider option[value="api"]').disabled=!state?.api_enabled;
    $('#live-chatgpt').hidden=!plan;
    $('#live-auth-status').textContent=state?.chatgpt_message || tr(!state?'access':!state.signin_enabled?'unavailable':auth?.sharing?'connected':'signedOut');
    $('#live-signin').disabled=busy||!!pendingRequest||!state?.signin_enabled;
    $('#live-signout').disabled=busy||!!pendingRequest||!auth?.connected;
    $('#live-models').disabled=busy||!!pendingRequest||!auth?.sharing;
    $('#live-refresh').disabled=busy||unlocking;$('#live-retry').hidden=!pendingRequest||busy;
    $('#live-gate').textContent=tr(!state?'access':!state.enabled?'disabled':!state.remaining?'limit':plan&&!auth?.sharing?'signedOut':plan&&!auth?.ready?'connected':'ready');
    if(claude&&state)$('#live-gate').textContent=tr(!state.enabled?'disabled':!state.claude_enabled?'claudeDisabled':!state.claude_configured?'claudeModel':!state.remaining?'limit':'claudeReady');
    $('#live-profile').hidden=!state||!!state.profile;
    $('#live-profile-note').textContent=state?.profile?tr('readonly'):'';
    const selected=$('#live-country').value, grade=$('#live-grade').value;
    $('#live-country').replaceChildren(...COUNTRIES.map(c=>{const n=node('option',c[lang()]);n.value=c.code;return n;}));$('#live-country').value=selected||'US';
    $('#live-grade').replaceChildren(...SUPPORTED_GRADES.map(g=>{const n=node('option',String(g));n.value=String(g);return n;}));$('#live-grade').value=grade||'9';
    $('#live-consent-text').textContent=tr(claude?'claudeConsent':plan?'consent':'apiConsent');
    $('#live-consent').disabled=busy||!!pendingRequest;$('#live-intent').disabled=busy||!!pendingRequest;
    $('#send').hidden=false;$('#stop').hidden=true;
    $('#send').disabled=busy||!!pendingRequest||!state?.profile||!state?.enabled||!state.remaining||!$('#live-consent').checked||(plan&&(!auth?.ready||!auth?.sharing))||(claude&&(!state?.claude_enabled||!state?.claude_configured));
    question.disabled=busy||!!pendingRequest;form.setAttribute('aria-busy',String(busy));
    $('#composer-help').textContent=tr('safety');$('#suggestions').hidden=true;
    $('.demo-badge [data-i18n="demo"]').textContent=tr(claude?'claude':plan?'plan':'api');$('.workspace-label small').textContent=tr('local');
    usageNote.hidden=!claude||!state?.last_usage;
    if(!usageNote.hidden){const u=state.last_usage,n=v=>Number.isSafeInteger(v)?new Intl.NumberFormat(lang()).format(v):'—';usageNote.textContent=`${tr('tokens')}: ${tr('inputTokens')} ${n(u.input_tokens)} · ${tr('outputTokens')} ${n(u.output_tokens)} · ${tr('cacheRead')} ${n(u.cache_read_input_tokens)} · ${tr('cacheWrite')} ${n(u.cache_creation_input_tokens)}${u.complete?'':` · ${tr('partialUsage')}`}`;}
    $('#profile-name').textContent=tr('profileName');$('#profile-avatar').hidden=true;$('#edit-profile').textContent=tr('connection');
    $('#profile-meta').textContent=state?.profile?`${tr('grade')} ${state.profile.grade} · ${COUNTRIES.find(c=>c.code===state.profile.country)?.[lang()]||''}`:tr('setup');
    $('#profile [data-i18n="demoProfile"]').textContent=tr('setup');
    $('#profile [data-i18n="demoHistoryNote"]').textContent=tr('oneChat');
    $('#profile [data-i18n="progressBody"]').textContent=tr('noScore');
    $('#settings [data-i18n="privacy"]').textContent=tr('local');$('#settings [data-i18n="privacyBody"]').textContent=tr('storage');
    $('#progress [data-i18n="progressBody"]').textContent=tr('safety');
    progress.textContent=`${tr('noScore')} ${new Intl.NumberFormat(lang()).format(state?.attempts?.length||0)}`;
    $('#library-list').textContent=tr('blocked');
    renderHistory();renderSearch();renderStatus();
  }
  async function connectionAction(path,body){
    if(busy||pendingRequest)return null;busy=true;status('connecting');render();
    try{const result=await api(path,body,60000);await refresh();status();return result;}
    catch(error){status(error.code?'':'failure',true,error.code?error.message:'');return null;}
    finally{busy=false;render();}
  }
  function acceptReply(payload, reply){
    if(typeof reply!=='string'||!reply.trim())throw new Error('Invalid local reply');
    const history=state?.history||[];
    if(history.at(-1)?.role!=='assistant'||history.at(-1)?.content!==reply||history.at(-2)?.content!==payload.message){
      if(state)state.history=[...history,{role:'user',content:payload.message},{role:'assistant',content:reply}];
    }
    pendingRequest=null;question.value='';status('completed');render();$('#main').scrollTop=$('#main').scrollHeight;
  }
  async function send(payload){
    busy=true;status('generating');render();
    try{
      const result=await api('/api/chat',payload,150000);if(result.usage&&state)state.last_usage=result.usage;acceptReply(payload,result.reply);
      try{await refresh();}catch{status('savedRefresh',true);}
    }catch(error){
      if(error.code && !['busy','uncertain'].includes(error.code))pendingRequest=null;
      status(error.code?'':'failure',true,error.code?error.message:'');
      if(error.code){try{await refresh();}catch{}}
    }finally{busy=false;render();}
  }
  async function reconcile(){
    if(!pendingRequest||busy)return;busy=true;render();
    try{
      const result=await api('/api/requests/'+pendingRequest.request_id);
      if(result.status==='done'){if(result.usage&&state)state.last_usage=result.usage;acceptReply(pendingRequest,result.reply);try{await refresh();}catch{status('savedRefresh',true);}}
      else if(result.status==='failed'){pendingRequest=null;status('',true,result.message);try{await refresh();}catch{}}
      else status(result.status==='missing'?'missing':'uncertain',true);
    }catch(error){status(error.code?'':'failure',true,error.code?error.message:'');}
    finally{busy=false;render();}
  }
  form.addEventListener('submit',event=>{
    event.preventDefault();event.stopImmediatePropagation();if($('#send').disabled)return;
    const message=question.value.trim();if(!message||message.length>4000){status('validate',true);return;}
    pendingRequest={request_id:crypto.randomUUID(),message,language:lang(),intent:$('#live-intent').value,provider:state.provider};void send(pendingRequest);
  },true);
  connectionButton.addEventListener('click',openSettings);
  window.addEventListener('nmi-open-connection',openSettings);window.addEventListener('nmi-open-live',openSettings);
  window.addEventListener('nmi-demo-blocked',()=>status('blocked',true));
  window.addEventListener('nmi-render',render);window.addEventListener('nmi-search',renderSearch);
  $('#new-chat').addEventListener('click',()=>status('oneChat'));
  $('#live-consent').addEventListener('change',render);
  $('#live-refresh').addEventListener('click',async()=>{try{await refresh();status();}catch(e){status(e.code?'':'failure',true,e.code?e.message:'');}});
  $('#live-retry').addEventListener('click',()=>void reconcile());
  $('#live-profile').addEventListener('submit',event=>{event.preventDefault();void connectionAction('/api/profile',{country:$('#live-country').value,grade:Number($('#live-grade').value)}).then(result=>{if(result){status('profileSaved');location.hash='new';}});});
  $('#live-provider').addEventListener('change',()=>{$('#live-consent').checked=false;void connectionAction('/api/provider',{provider:$('#live-provider').value});});
  $('#live-signin').addEventListener('click',async()=>{
    const result=await connectionAction('/api/chatgpt/start',{});
    if(result?.url){const url=new URL(result.url);if(url.origin==='https://auth.openai.com'&&url.pathname==='/api/accounts/authorize')location.assign(url.href);}
  });
  $('#live-models').addEventListener('click',()=>void connectionAction('/api/chatgpt/models',{}));
  $('#live-signout').addEventListener('click',async()=>{$('#live-consent').checked=false;if(await connectionAction('/api/chatgpt/signout',{}))status('signoutDone');});
  window.addEventListener('beforeunload',event=>{if(busy||pendingRequest||question.value.trim()){event.preventDefault();event.returnValue='';}});
  async function unlock(){
    if(!location.hash.startsWith('#local-access')||unlocking)return;
    const match=location.hash.match(/^#local-access=([A-Za-z0-9_-]{20,100})$/);
    history.replaceState(null,'',location.pathname+location.search);revision++;state=null;csrf='';
    status(match?'unlocking':'malformed',!match);render();if(!match)return;
    unlocking=true;let claimed=false;
    try{
      await api('/api/session/preflight');
      if(!(await api('/api/session/preflight')).cookie_ready){status('cookies',true);return;}
      await api('/api/session',{token:match[1]});claimed=true;await refresh();status();
    }catch(error){status(error.code==='access'?(claimed?'cookieLost':'unlockFailed'):error.code==='cookies'?'cookies':'failure',true);}
    finally{unlocking=false;render();if(location.hash.startsWith('#local-access'))void unlock();}
  }
  window.addEventListener('hashchange',()=>void unlock());
  render();
  if(location.hash.startsWith('#local-access'))void unlock();
  else void refresh().catch(error=>status(error.code==='access'?'access':'failure',true));
})();
