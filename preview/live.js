/* Flask-only controller. Main NMI chat, server persistence, no demo fallback. */
(() => {
  'use strict';
  // Israel is live-only: the curriculum files exist for it, and the demo list stays unchanged.
  const LIVE_COUNTRIES = [...COUNTRIES, {code:'IL', en:'Israel', ar:'إسرائيل'}];
  const COPY = {
    en: {
      connection:'Tutor connection',   
      claude:'Claude · Anthropic API', claudeDisabled:'Anthropic paid requests are disabled by the owner.',
      claudeModel:'The owner must configure a Claude model on the server.',
      claudeReady:'Claude is configured for approved requests. Availability is checked when you send.',
      claudeConsent:'I approve sending this message and recent learning context to Anthropic using paid Claude API credits. No automatic retry or provider fallback.',
      tokens:'Last reported Claude usage', inputTokens:'input', outputTokens:'output', cacheRead:'cache read', cacheWrite:'cache write', partialUsage:'Partial report; final usage may be higher.',
         
      access:'Open the private local link printed in the server terminal.', unlocking:'Unlocking this local session…',
      malformed:'The private link is incomplete. Copy the whole link from the current server terminal.',
      unlockFailed:'This link is from another launch or this server belongs to another browser session. Restart the server and use its new complete private link in one Chrome profile.',
      cookies:'Cookies could not be verified. Allow cookies for 127.0.0.1 and reopen the current private link. No new session was claimed.',
      cookieLost:'The link was accepted, but the browser session could not be verified. Allow cookies, restart the server and use its new link in the same Chrome profile.',
       connecting:'Connecting…', 
      ready:'Connected. Ready for your approved tutoring request.', disabled:'Local session unlocked. Tutoring requests are disabled until the owner enables them.',
       limit:'The local request limit has been reached. No additional request will be sent.',
      generating:'Generating an answer…', completed:'Completed. Conversation saved locally.',
      failure:'Connection failed or timed out. Your draft remains here. Check the request status before sending again.',
      savedRefresh:'The reply was saved and is displayed below, but the latest connection status could not be refreshed.',
      uncertain:'The request outcome is not confirmed. Do not send another request. Check its saved status again or ask the owner to inspect it.',
      reconcile:'Check saved request status', refresh:'Refresh connection status', setup:'Local test profile',
      privacy:'Use fictional test information only. This local prototype has one owner and one saved conversation.',
      country:'Country of study', grade:'Grade', subject:'Subject', subject_math:'Mathematics', saveProfile:'Save profile', profileTitle:'Student profile', profileIntro:'Choose your country, grade and units. NMI cannot chat before the profile is complete.', profileNeeds:'Your saved profile is incomplete. Complete it before you continue.', choose:'Choose…', targetUnits:'Do you want to move up to a higher level?', noTarget:'No', editProfile:'Edit profile', cancelProfile:'Cancel', units:'Study level (units)', unitsOption:'units', save:'Save local test profile', profileSaved:'Local test profile saved.',
      
      
      validate:'Use a message of 1–4,000 characters.', user:'You', conversation:'Saved conversation',
      oneChat:'One local conversation. New conversations and pinning are not connected to the backend yet.',
      safety:'AI can make mistakes. No verified official curriculum is loaded. Local records are visible to people with access to this computer.',
      noScore:'No mastery scores are inferred from questions. Recorded learning attempts:',
      noHistory:'No saved conversation yet.', noSearch:'No matching saved conversation.',
      profileName:'Local learner', ask:'Question', answer:'Answer to an exercise', hint:'Request a hint', confusion:'I am confused', intent:'Message type',
      blocked:'Scripted replies are disabled here. Use the main composer after connecting the tutor.', local:'Local tutor',
      storage:'This conversation is saved on the local Flask server, separate from the static demo. No real replies are saved in browser demo storage.',
      missing:'No saved receipt was found yet. This does not prove that the request cannot still finish. Do not resend.',
      
    },
    ar: {
      connection:'اتصال المعلّم',   
      claude:'Claude · واجهة Anthropic', claudeDisabled:'عطّل صاحب المشروع طلبات Anthropic المدفوعة.',
      claudeModel:'يجب على صاحب المشروع إعداد نموذج Claude في الخادم.',
      claudeReady:'تم إعداد Claude للطلبات الموافق عليها. يُتحقّق من توفره عند الإرسال.',
      claudeConsent:'أوافق على إرسال هذه الرسالة وسياق التعلّم الأخير إلى Anthropic باستخدام رصيد Claude API المدفوع. لن تحدث إعادة محاولة تلقائية أو تحويل إلى خدمة بديلة.',
      tokens:'آخر استخدام مُبلّغ عنه من Claude', inputTokens:'إدخال', outputTokens:'إخراج', cacheRead:'قراءة التخزين المؤقت', cacheWrite:'كتابة التخزين المؤقت', partialUsage:'تقرير جزئي؛ قد يكون الاستخدام النهائي أعلى.',
         
      access:'افتح الرابط المحلي الخاص الظاهر في نافذة الخادم.', unlocking:'جارٍ فتح الجلسة المحلية…',
      malformed:'الرابط الخاص ناقص. انسخ الرابط كاملًا من نافذة الخادم الحالية.',
      unlockFailed:'الرابط يخص تشغيلًا آخر أو أن الخادم مرتبط بجلسة متصفح أخرى. أعد تشغيل الخادم وافتح رابطه الجديد كاملًا في ملف Chrome واحد.',
      cookies:'تعذّر التحقّق من ملفات الارتباط. اسمح بها للموقع 127.0.0.1 وأعد فتح الرابط الخاص الحالي. لم تُحجز جلسة جديدة.',
      cookieLost:'قُبل الرابط، لكن تعذّر التحقّق من جلسة المتصفح. اسمح بملفات الارتباط وأعد تشغيل الخادم وافتح رابطه الجديد في ملف Chrome نفسه.',
       connecting:'جارٍ الاتصال…', 
      ready:'متصل. جاهز لطلب التعليم الذي وافقت عليه.', disabled:'الجلسة المحلية مفتوحة. طلبات التعليم معطّلة إلى أن يفعّلها صاحب المشروع.',
       limit:'وصلت إلى حدّ الطلبات المحلية. لن يُرسَل طلب إضافي.',
      generating:'جارٍ إعداد الإجابة…', completed:'اكتمل الرد وحُفظت المحادثة محليًا.',
      failure:'تعذّر الاتصال أو انتهت مهلته. بقيت مسودتك هنا. تحقّق من حالة الطلب قبل الإرسال مجددًا.',
      savedRefresh:'حُفظ الرد ويظهر أدناه، لكن تعذّر تحديث حالة الاتصال الأخيرة.',
      uncertain:'لم تُؤكّد نتيجة الطلب. لا تُرسِل طلبًا آخر. تحقّق من حالته المحفوظة مجددًا أو اطلب من صاحب المشروع فحصها.',
      reconcile:'التحقّق من حالة الطلب المحفوظ', refresh:'تحديث حالة الاتصال', setup:'ملف اختبار محلي',
      privacy:'استخدم معلومات اختبار افتراضية فقط. يدعم هذا النموذج المحلي مستخدمًا واحدًا ومحادثة محفوظة واحدة.',
      country:'بلد الدراسة', grade:'الصف الدراسي', subject:'المادة', subject_math:'الرياضيات', saveProfile:'حفظ البروفايل', profileTitle:'ملف الطالب', profileIntro:'اختر الدولة والصف والوحدات. لا تبدأ المحادثة قبل اكتمال الملف.', profileNeeds:'ملفك المحفوظ غير مكتمل. أكمله قبل أن تتابع.', choose:'اختر…', targetUnits:'بدك تنتقل لمستوى أعلى؟', noTarget:'لا', editProfile:'تعديل البروفايل', cancelProfile:'إلغاء', units:'مستوى الدراسة (وحدات)', unitsOption:'وحدات', save:'حفظ ملف الاختبار المحلي', profileSaved:'حُفظ ملف الاختبار المحلي.',
      
      
      validate:'استخدم رسالة من حرف واحد إلى 4000 حرف.', user:'أنت', conversation:'المحادثة المحفوظة',
      oneChat:'محادثة محلية واحدة. إنشاء محادثات إضافية وتثبيتها غير متصل بالخادم بعد.',
      safety:'قد يخطئ الذكاء الاصطناعي. لم يُحمّل منهج رسمي موثّق. يمكن لمن يصل إلى هذا الحاسوب الاطّلاع على السجلات المحلية.',
      noScore:'لا تُستنتج درجات إتقان من الأسئلة. محاولات التعلّم المسجّلة:',
      noHistory:'لا توجد محادثة محفوظة بعد.', noSearch:'لا توجد محادثة محفوظة مطابقة.',
      profileName:'المتعلّم المحلي', ask:'سؤال', answer:'إجابة عن تمرين', hint:'طلب تلميح', confusion:'لم أفهم', intent:'نوع الرسالة',
      blocked:'الردود التجريبية معطّلة هنا. استخدم مربع المحادثة الرئيسي بعد توصيل المعلّم.', local:'المعلّم المحلي',
      storage:'تُحفظ هذه المحادثة في خادم Flask المحلي منفصلةً عن المعاينة التجريبية. لا تُحفظ الردود الحقيقية في تخزين المعاينة بالمتصفح.',
      missing:'لم يُعثر على سجل محفوظ للطلب بعد. قد يكون الطلب ما زال قيد التنفيذ. لا تُعِد الإرسال.',
      
    }
  };
  const $ = s => document.querySelector(s);
  const lang = () => document.documentElement.lang === 'ar' ? 'ar' : 'en';
  const tr = key => COPY[lang()][key];
  const node = (tag, text, cls) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
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
  connection.innerHTML=`<h2 data-live="connection"></h2>`;
  $('#settings').append(connection);
  // Student profile: a dialog that opens first (nothing preselected) and can be reopened to edit.
  const profileDialog=node('dialog');profileDialog.id='live-onboarding';profileDialog.setAttribute('aria-labelledby','live-profile-title');
  profileDialog.innerHTML=`<div class="onboarding-brand"><img src="assets/nmi-mark-light.svg" width="38" height="38" alt="NMI"></div>
    <h2 id="live-profile-title" data-live="profileTitle"></h2><p id="live-profile-intro" class="page-note"></p>
    <form id="live-profile" novalidate><div class="onboarding-grid">
      <div class="field"><label for="live-country-text" data-live="country"></label><input id="live-country-text" type="text" readonly aria-readonly="true" dir="auto"></div>
      <div class="field" id="live-subject-field" hidden><label for="live-subject" data-live="subject"></label><select id="live-subject"></select></div>
      <div class="field"><label for="live-grade" data-live="grade"></label><select id="live-grade" required></select></div>
      <div class="field" id="live-units-field" hidden><label for="live-units" data-live="units"></label><select id="live-units"></select></div>
      <div class="field" id="live-target-field" hidden><label for="live-target-units" data-live="targetUnits"></label><select id="live-target-units"></select></div>
    </div><p id="live-profile-error" class="form-status error" role="status"></p>
    <div class="onboarding-actions"><button type="button" id="live-profile-cancel" class="context-button" data-live="cancelProfile" hidden></button><button type="submit" id="live-profile-save" class="primary-button" data-live="saveProfile"></button></div></form>`;
  document.body.append(profileDialog);
  const editProfileButton=node('button',undefined,'context-button');editProfileButton.id='live-edit-profile';editProfileButton.type='button';banner.append(editProfileButton);
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
    try {const value=await api('/api/state');if(current!==revision)return false;state=value;csrf=value.csrf;return true;}
    catch(error){if(current!==revision)return false;if(error.code==='access'){state=null;csrf='';}throw error;}
    finally {if(current===revision)render();}
  }
  // Subject, grade and units for the curriculum country come from the server's curriculum/ folders.
  // Every select starts empty ("Choose…"): the student picks, nothing is preselected.
  let profileMode=null; // 'forced' cannot be dismissed (no complete profile yet); 'edit' can
  function fillSelect(select,values,label,wanted,empty){
    const keep=wanted!==undefined?String(wanted):select.value, list=values.map(String);
    select.replaceChildren(...['',...list].map(v=>{const n=node('option',v===''?(empty||tr('choose')):label(v));n.value=v;return n;}));
    // The only subject is not a choice: it is selected for the student.
    select.value=list.includes(keep)?keep:(select.id==='live-subject'&&list.length===1?list[0]:'');
  }
  function fillForm(want){
    // Israel is the only country with a curriculum: it is written in the form and always selected.
    const w=want||{}, countryCode=state?.curriculum?.country||'';
    $('#live-country-text').value=LIVE_COUNTRIES.find(c=>c.code===countryCode)?.[lang()]||countryCode;
    const curriculum=!!countryCode, tree=curriculum?state.curriculum.options:{};
    $('#live-subject-field').hidden=!curriculum;$('#live-units-field').hidden=!curriculum;
    fillSelect($('#live-subject'),Object.keys(tree),s=>tr('subject_'+s)||s,w.subject);
    fillSelect($('#live-grade'),curriculum?Object.keys(tree[$('#live-subject').value]||{}):[],g=>String(g),w.grade);
    const units=curriculum?tree[$('#live-subject').value]?.[$('#live-grade').value]||[]:[];
    fillSelect($('#live-units'),units,u=>`${u} ${tr('unitsOption')}`,w.units);
    const higher=units.filter(u=>u>(Number($('#live-units').value)||Infinity));
    $('#live-target-field').hidden=!curriculum||!higher.length;
    fillSelect($('#live-target-units'),higher,u=>`${u} ${tr('unitsOption')}`,w.target_units,tr('noTarget'));
    $('#live-profile-save').disabled=busy||!formBody();
  }
  // The profile to send, or null while a required choice is missing (or the country has no curriculum).
  function formBody(){
    if($('#live-units-field').hidden)return null;
    const subject=$('#live-subject').value, grade=$('#live-grade').value, units=$('#live-units').value;
    if(!subject||!grade||!units)return null;
    const target=$('#live-target-field').hidden?'':$('#live-target-units').value;
    return {country:state.curriculum.country,grade:Number(grade),subject,units:Number(units),...(target?{target_units:Number(target)}:{})};
  }
  function openProfile(mode){
    if(!state)return;
    profileMode=mode;const p=state.profile;
    fillForm(p&&p.country===state?.curriculum?.country
      ?{subject:p.subject||'math',grade:p.grade,units:p.units??'',target_units:p.target_units??''}
      :{subject:'',grade:'',units:'',target_units:''});
    $('#live-profile-cancel').hidden=mode==='forced';
    $('#live-profile-intro').textContent=tr(mode==='forced'&&p?'profileNeeds':'profileIntro');
    if(!profileDialog.open)profileDialog.showModal();
    $('#live-grade').focus();
  }
  // No complete profile: the dialog opens first and stays until it is saved. A complete one closes it.
  function syncProfileDialog(){
    if(!state||unlocking)return;
    if(!state.profile_ready){if(profileMode!=='forced'||!profileDialog.open)openProfile('forced');}
    else if(profileMode==='forced'){profileMode=null;if(profileDialog.open)profileDialog.close();}
  }
  // ---- Markdown for the tutor's replies. It only builds DOM nodes with textContent (never innerHTML), so raw HTML
  // in a reply is shown as text. Links are kept only for http(s); every other scheme stays plain text.
  const MATH_WORDS=/\b(?:sin|cos|tan|cot|log|ln|sqrt|exp|abs|lim|max|min|mod)\b/gi;
  function isMathLine(line){
    // An equation alone on its line: only math characters, an "=" or inequality, and no ordinary words.
    if(line.length>140||!/[=<>≤≥≠]/.test(line)||!/[0-9xyz]/i.test(line))return false;
    if(!/^[0-9A-Za-z\s=+\-−*/^()√²³.,:<>≤≥≠|×÷·π°%'_[\]{}]+$/.test(line))return false;
    return !/[A-Za-z]{3,}/.test(line.replace(MATH_WORDS,''));
  }
  function mathBlock(text){const n=node('div',text.trim(),'md-math');n.dir='ltr';return n;}
  function inline(parent,text){
    const pattern=/\*\*([^*\n]+?)\*\*|`([^`\n]+?)`|\$\$([^\n]+?)\$\$|\$([^$\s][^$\n]*?)\$(?![0-9])|\[([^\]\n]+)\]\(([^)\s]+)\)|(?<![*\w])\*([^\s*][^*\n]*?)\*(?![*\w])/g;
    let last=0,match;
    while((match=pattern.exec(text))){
      if(match.index>last)parent.append(text.slice(last,match.index));
      if(match[1]!==undefined){const n=node('strong');inline(n,match[1]);parent.append(n);}
      else if(match[2]!==undefined){const n=node('code',match[2]);n.dir='ltr';parent.append(n);}
      else if(match[3]!==undefined||match[4]!==undefined){const n=node('span',(match[3]??match[4]).trim(),'md-math-inline');n.dir='ltr';parent.append(n);}
      else if(match[5]!==undefined){
        if(/^https?:\/\//i.test(match[6])){const a=node('a',match[5]);a.href=match[6];a.target='_blank';a.rel='noopener noreferrer';parent.append(a);}
        else parent.append(`${match[5]} (${match[6]})`);
      }
      else{const n=node('em');inline(n,match[7]);parent.append(n);}
      last=pattern.lastIndex;
    }
    if(last<text.length)parent.append(text.slice(last));
  }
  function withInline(tag,text){const n=node(tag);n.dir='auto';inline(n,text);return n;}
  function tableCells(line){return line.trim().replace(/^\|/,'').replace(/\|$/,'').split('|').map(cell=>cell.trim());}
  function renderMarkdown(source){
    const root=node('div',undefined,'md'), lines=String(source).replace(/\r\n?/g,'\n').split('\n');
    let i=0;
    const special=line=>/^\s*(#{1,4}\s|[-*•]\s|\d+[.)]\s|\$\$|\|.*\||---+\s*$)/.test(line)||isMathLine(line.trim());
    while(i<lines.length){
      const line=lines[i];
      if(!line.trim()){i++;continue;}
      let m;
      if((m=line.match(/^\s*\$\$(.+?)\$\$\s*$/))){root.append(mathBlock(m[1]));i++;continue;}
      if(/^\s*\$\$\s*$/.test(line)){const body=[];i++;while(i<lines.length&&!/^\s*\$\$\s*$/.test(lines[i]))body.push(lines[i++]);i++;root.append(mathBlock(body.join('\n')));continue;}
      if((m=line.match(/^\s*(#{1,4})\s+(.*)$/))){root.append(withInline('h'+(2+m[1].length),m[2].replace(/\s*#+\s*$/,'')));i++;continue;}
      if(/^\s*---+\s*$/.test(line)){root.append(node('hr'));i++;continue;}
      if(line.includes('|')&&i+1<lines.length&&/^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(lines[i+1])){
        const head=tableCells(line), table=node('table'), thead=node('thead'), tbody=node('tbody'), hr=node('tr');
        for(const cell of head){const th=withInline('th',cell);hr.append(th);}
        thead.append(hr);table.append(thead,tbody);i+=2;
        while(i<lines.length&&lines[i].includes('|')&&lines[i].trim()){const tr_=node('tr');for(const cell of tableCells(lines[i]))tr_.append(withInline('td',cell));tbody.append(tr_);i++;}
        const wrap=node('div',undefined,'md-table');wrap.append(table);root.append(wrap);continue;
      }
      if(/^\s*[-*•]\s+/.test(line)||/^\s*\d+[.)]\s+/.test(line)){
        const ordered=/^\s*\d+[.)]\s+/.test(line), list=node(ordered?'ol':'ul');
        if(ordered)list.start=Number(line.match(/^\s*(\d+)/)[1]);
        const marker=ordered?/^\s*\d+[.)]\s+(.*)$/:/^\s*[-*•]\s+(.*)$/;
        while(i<lines.length&&(m=lines[i].match(marker))){list.append(withInline('li',m[1]));i++;}
        root.append(list);continue;
      }
      // An equation on a line of its own is a block of its own, even right after a sentence.
      if(isMathLine(line.trim())){root.append(mathBlock(line));i++;continue;}
      const body=[];
      while(i<lines.length&&lines[i].trim()&&!(body.length&&special(lines[i])))body.push(lines[i++]);
      root.append(withInline('p',body.join('\n')));
    }
    return root;
  }
  window.nmiRenderMarkdown=renderMarkdown;
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
        const content=message.role==='assistant'?renderMarkdown(message.content):node('div',message.content);content.classList.add('live-message-content');content.dir='auto';article.append(content);target.append(article);
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
    document.querySelectorAll('[data-live]').forEach(n=>n.textContent=tr(n.dataset.live));
    connectionButton.textContent=tr('connection');$('#live-refresh').textContent=tr('refresh');$('#live-retry').textContent=tr('reconcile');
    $('#live-refresh').disabled=busy||unlocking;$('#live-retry').hidden=!pendingRequest||busy;
    $('#live-gate').textContent=tr(!state?'access':!state.enabled?'disabled':!state.claude_enabled?'claudeDisabled':!state.claude_configured?'claudeModel':!state.remaining?'limit':'claudeReady');
    editProfileButton.textContent=tr('editProfile');editProfileButton.hidden=!state;
    profileDialog.querySelector('img').src=`assets/nmi-mark-${document.documentElement.dataset.theme}.svg`;
    fillForm();
    $('#live-consent-text').textContent=tr('claudeConsent');
    $('#live-consent').disabled=busy||!!pendingRequest;$('#live-intent').disabled=busy||!!pendingRequest;
    $('#send').hidden=false;$('#stop').hidden=true;
    $('#send').disabled=busy||!!pendingRequest||!state?.profile_ready||!state?.enabled||!state.remaining||!$('#live-consent').checked||!state?.claude_enabled||!state?.claude_configured;
    question.disabled=busy||!!pendingRequest;form.setAttribute('aria-busy',String(busy));
    $('#composer-help').textContent=tr('safety');$('#suggestions').hidden=true;
    $('.demo-badge [data-i18n="demo"]').textContent=tr('claude');$('.workspace-label small').textContent=tr('local');
    usageNote.hidden=!state?.last_usage;
    if(!usageNote.hidden){const u=state.last_usage,n=v=>Number.isSafeInteger(v)?new Intl.NumberFormat(lang()).format(v):'—';usageNote.textContent=`${tr('tokens')}: ${tr('inputTokens')} ${n(u.input_tokens)} · ${tr('outputTokens')} ${n(u.output_tokens)} · ${tr('cacheRead')} ${n(u.cache_read_input_tokens)} · ${tr('cacheWrite')} ${n(u.cache_creation_input_tokens)}${u.complete?'':` · ${tr('partialUsage')}`}`;}
    $('#profile-name').textContent=tr('profileName');$('#profile-avatar').hidden=true;$('#edit-profile').textContent=tr('editProfile');
    $('#profile-meta').textContent=state?.profile?`${tr('grade')} ${state.profile.grade} · ${LIVE_COUNTRIES.find(c=>c.code===state.profile.country)?.[lang()]||''}${state.profile.units?` · ${state.profile.units} ${tr('unitsOption')}`:''}${state.profile.target_units?` → ${state.profile.target_units} ${tr('unitsOption')}`:''}`:tr('setup');
    $('#profile [data-i18n="demoProfile"]').textContent=tr('setup');
    $('#profile [data-i18n="demoHistoryNote"]').textContent=tr('oneChat');
    $('#profile [data-i18n="progressBody"]').textContent=tr('noScore');
    $('#settings [data-i18n="privacy"]').textContent=tr('local');$('#settings [data-i18n="privacyBody"]').textContent=tr('storage');
    $('#progress [data-i18n="progressBody"]').textContent=tr('safety');
    progress.textContent=`${tr('noScore')} ${new Intl.NumberFormat(lang()).format(state?.attempts?.length||0)}`;
    $('#library-list').textContent=tr('blocked');
    renderHistory();renderSearch();renderStatus();syncProfileDialog();
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
    pendingRequest={request_id:crypto.randomUUID(),message,language:lang(),intent:$('#live-intent').value};void send(pendingRequest);
  },true);
  connectionButton.addEventListener('click',openSettings);
  window.addEventListener('nmi-open-connection',()=>openProfile('edit'));window.addEventListener('nmi-open-live',openSettings);
  window.addEventListener('nmi-demo-blocked',()=>status('blocked',true));
  window.addEventListener('nmi-render',render);window.addEventListener('nmi-search',renderSearch);
  $('#new-chat').addEventListener('click',()=>status('oneChat'));
  $('#live-consent').addEventListener('change',render);
  for(const id of ['subject','grade','units','target-units'])$('#live-'+id).addEventListener('change',()=>fillForm());
  editProfileButton.addEventListener('click',()=>openProfile('edit'));
  $('#live-profile-cancel').addEventListener('click',()=>{profileMode=null;profileDialog.close();});
  profileDialog.addEventListener('cancel',event=>{if(profileMode==='forced')event.preventDefault();else profileMode=null;});
  $('#live-refresh').addEventListener('click',async()=>{try{await refresh();status();}catch(e){status(e.code?'':'failure',true,e.code?e.message:'');}});
  $('#live-retry').addEventListener('click',()=>void reconcile());
  $('#live-profile').addEventListener('submit',event=>{
    event.preventDefault();const body=formBody();if(!body||busy)return;
    void connectionAction('/api/profile',body).then(result=>{if(result){profileMode=null;if(profileDialog.open)profileDialog.close();status('profileSaved');location.hash='new';render();}});
  });
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
