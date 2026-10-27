/* Every text the student sees on the kit page, in three languages: ar (simple Modern Standard Arabic), he (Hebrew)
   and en (English). The prompt itself stays in Arabic (the curriculum is Arabic) and is not here, except for the one
   line that tells the tutor which language the student speaks (kit/prompt.js).
   Pure data and small functions: no DOM, no network. Used by app.js in the page and by the node tests. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NMII18n = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const LANGS = ['ar', 'he', 'en'];
  const NAMES = { ar: 'عربي', he: 'עברית', en: 'English' };
  const DIR = { ar: 'rtl', he: 'rtl', en: 'ltr' };
  const STORAGE_KEY = 'nmi-lang-v1';

  const STRINGS = {
    "title": {
      "ar": "عدّة NMI",
      "he": "ערכת NMI",
      "en": "NMI Kit"
    },
    "description": {
      "ar": "جهّز نصًّا فيه منهاجك ونمط الامتحان وقواعد التدريس، وافتحه في تطبيق الذكاء الاصطناعي الذي تستخدمه.",
      "he": "הכינו פרומפט עם התוכנית שלכם, מבנה המבחנים וכללי ההוראה, ופתחו אותו באפליקציית הבינה המלאכותית שלכם.",
      "en": "Prepare a prompt with your curriculum, the shape of the exams and the teaching rules, and open it in the AI app you already use."
    },
    "brand": {
      "ar": "عدّة NMI",
      "he": "ערכת NMI",
      "en": "NMI Kit"
    },
    "back": {
      "ar": "→ رجوع",
      "he": "→ חזרה",
      "en": "← Back"
    },
    "loading": {
      "ar": "لحظة، نجهّز المنهاج...",
      "he": "רגע, מכינים את התוכנית...",
      "en": "One moment, getting the curriculum ready..."
    },
    "noscript": {
      "ar": "تحتاج الصفحة إلى JavaScript لتجهيز البرومبت.",
      "he": "הדף צריך JavaScript כדי להכין את הפרומפט.",
      "en": "This page needs JavaScript to prepare the prompt."
    },
    "logLink": {
      "ar": "سجلّي",
      "he": "היומן שלי",
      "en": "My log"
    },
    "langNav": {
      "ar": "اللغة",
      "he": "שפה",
      "en": "Language"
    },
    "stepOf": {
      "ar": "الخطوة {n} من {total}",
      "he": "שלב {n} מתוך {total}",
      "en": "Step {n} of {total}"
    },
    "intro": {
      "ar": "NMI يجهّز تعليمات لـ ChatGPT أو Claude أو Gemini، فيها منهاجك وشكل امتحاناتك، ليعلّمك بدل أن يحلّ عنك.",
      "he": "NMI מכין הוראות ל-ChatGPT, Claude או Gemini, עם התוכנית שלכם ומבנה המבחנים, כדי שילמד אתכם ולא יפתור במקומכם.",
      "en": "NMI prepares instructions for ChatGPT, Claude or Gemini with your curriculum and the shape of your exams, so it teaches you instead of solving for you."
    },
    "s1Title": {
      "ar": "ما مستواك؟",
      "he": "מה הרמה שלכם?",
      "en": "What is your level?"
    },
    "subject": {
      "ar": "المادة",
      "he": "מקצוע",
      "en": "Subject"
    },
    "grade": {
      "ar": "الصف",
      "he": "כיתה",
      "en": "Grade"
    },
    "units": {
      "ar": "الوحدات",
      "he": "יחידות לימוד (יח\"ל)",
      "en": "Units"
    },
    "unitsN": {
      "ar": "{n} وحدات",
      "he": "{n} יח\"ל",
      "en": "{n} units"
    },
    "targetTitle": {
      "ar": "مستوى هدف (اختياري)",
      "he": "רמת יעד (לא חובה)",
      "en": "Target level (optional)"
    },
    "targetHint": {
      "ar": "إذا أردت الانتقال إلى مستوى أعلى، فاختره وسنضيف مواضيعه.",
      "he": "רוצים לעלות לרמה גבוהה יותר? בחרו בה ונוסיף את הנושאים שלה.",
      "en": "Want to move up a level? Choose it and we will add its topics."
    },
    "noTarget": {
      "ar": "بلا هدف",
      "he": "ללא יעד",
      "en": "No target"
    },
    "next": {
      "ar": "التالي",
      "he": "הבא",
      "en": "Next"
    },
    "experimental": {
      "ar": "تجريبي",
      "he": "ניסיוני",
      "en": "Experimental"
    },
    "s2Title": {
      "ar": "ما الذي تريد مراجعته؟",
      "he": "מה תרצו לחזור עליו?",
      "en": "What do you want to review?"
    },
    "allTopics": {
      "ar": "كل المواضيع",
      "he": "כל הנושאים",
      "en": "All topics"
    },
    "customTitle": {
      "ar": "أضف موضوعًا غير موجود في القائمة",
      "he": "הוסיפו נושא שלא מופיע ברשימה",
      "en": "Add a topic that is not on the list"
    },
    "customPlaceholder": {
      "ar": "مثال: المعادلات التربيعية",
      "he": "לדוגמה: משוואות ריבועיות",
      "en": "For example: quadratic equations"
    },
    "customAdd": {
      "ar": "أضف",
      "he": "הוספה",
      "en": "Add"
    },
    "customDelete": {
      "ar": "حذف",
      "he": "מחיקה",
      "en": "Delete"
    },
    "customDeleteLabel": {
      "ar": "احذف: {text}",
      "he": "מחיקה: {text}",
      "en": "Delete: {text}"
    },
    "customLimit": {
      "ar": "وصلت إلى الحد الأقصى: {n} مواضيع.",
      "he": "הגעתם למגבלה: {n} נושאים.",
      "en": "You reached the limit: {n} topics."
    },
    "customEmpty": {
      "ar": "اكتب اسم الموضوع أولًا.",
      "he": "כתבו קודם את שם הנושא.",
      "en": "Write the topic name first."
    },
    "customDup": {
      "ar": "هذا الموضوع مضاف بالفعل.",
      "he": "הנושא הזה כבר נוסף.",
      "en": "This topic is already added."
    },
    "targetSummary": {
      "ar": "مواضيع مستوى الهدف ({n} وحدات)",
      "he": "נושאי רמת היעד ({n} יח\"ל)",
      "en": "Target level topics ({n} units)"
    },
    "s3Title": {
      "ar": "ماذا تريد أن تفعل؟",
      "he": "מה תרצו לעשות?",
      "en": "What do you want to do?"
    },
    "modesHint": {
      "ar": "اختر وضعًا واحدًا أو أكثر. نبدأ بأول وضع ثم ننتقل إلى الباقي.",
      "he": "בחרו מצב אחד או יותר. מתחילים במצב הראשון ועוברים אל הבאים.",
      "en": "Choose one or more modes. We start with the first and move on to the others."
    },
    "modeExplainLabel": {
      "ar": "افهم",
      "he": "להבין",
      "en": "Understand"
    },
    "modeExplainDesc": {
      "ar": "شرح موضوع خطوة بخطوة.",
      "he": "הסבר של נושא צעד אחר צעד.",
      "en": "A topic explained step by step."
    },
    "modePracticeLabel": {
      "ar": "تدرّب",
      "he": "לתרגל",
      "en": "Practice"
    },
    "modePracticeDesc": {
      "ar": "سؤال بنمط الامتحان، قسمًا قسمًا، مع تصحيح حلّك.",
      "he": "שאלה במבנה של מבחן, סעיף אחר סעיף, עם בדיקה של הפתרון שלכם.",
      "en": "An exam-style question, one part at a time, with your answer checked."
    },
    "modeMockLabel": {
      "ar": "امتحان تجريبي",
      "he": "סימולציה",
      "en": "Mock exam"
    },
    "modeMockDesc": {
      "ar": "امتحان كامل على المواضيع المختارة، وعلامة من 100 في النهاية.",
      "he": "מבחן מלא על הנושאים שבחרתם, וציון מ-100 בסוף.",
      "en": "A full exam on the chosen topics, with a mark out of 100 at the end."
    },
    "modePlanLabel": {
      "ar": "خطة",
      "he": "תוכנית",
      "en": "Plan"
    },
    "modePlanDesc": {
      "ar": "خطة مراجعة لامتحانك موزّعة على الأيام.",
      "he": "תוכנית חזרה למבחן שלכם, לפי ימים.",
      "en": "A revision plan for your exam, day by day."
    },
    "prepare": {
      "ar": "جهّز البرومبت",
      "he": "הכינו את הפרומפט",
      "en": "Prepare the prompt"
    },
    "teacherFile": {
      "ar": "لديّ امتحان قديم أو ورقة عمل من معلّمي",
      "he": "יש לי מבחן ישן או דף עבודה מהמורה שלי",
      "en": "I have an old exam or a worksheet from my teacher"
    },
    "teacherFileHint": {
      "ar": "يعمل مع «تدرّب» و«امتحان تجريبي» فقط.",
      "he": "עובד רק עם \"לתרגל\" ו\"סימולציה\".",
      "en": "Works only with \"Practice\" and \"Mock exam\"."
    },
    "remind": {
      "ar": "ذكّرني بأخطائي القديمة",
      "he": "להזכיר לי את הטעויות הקודמות שלי",
      "en": "Remind me of my old mistakes"
    },
    "remindHint": {
      "ar": "من {n} جلسة محفوظة في سجلّي لهذا المستوى.",
      "he": "מתוך {n} סיכומים שמורים ביומן שלי לרמה הזאת.",
      "en": "From {n} sessions saved in My log for this level."
    },
    "noteTitle": {
      "ar": "ملاحظة للمدرّس (اختياري)",
      "he": "הערה למורה (לא חובה)",
      "en": "A note to the tutor (optional)"
    },
    "noteExamples": {
      "ar": "مثلًا: أحب الفيزياء، اجعل الأمثلة منها · ركّز على أخطاء الإشارات · اشرح ببطء · امتحاني يوم الأحد",
      "he": "לדוגמה: אוהב/ת פיזיקה, דוגמאות משם · להתמקד בטעויות סימן · להסביר לאט · המבחן שלי ביום ראשון",
      "en": "For example: I like physics, use examples from it · focus on sign mistakes · explain slowly · my exam is on Sunday"
    },
    "topicOne": {
      "ar": "موضوع واحد",
      "he": "נושא אחד",
      "en": "1 topic"
    },
    "topicTwo": {
      "ar": "موضوعان",
      "he": "שני נושאים",
      "en": "2 topics"
    },
    "topicFew": {
      "ar": "{n} مواضيع",
      "he": "{n} נושאים",
      "en": "{n} topics"
    },
    "topicMany": {
      "ar": "{n} موضوعًا",
      "he": "{n} נושאים",
      "en": "{n} topics"
    },
    "fromTarget": {
      "ar": "من مستوى الهدف",
      "he": "מרמת היעד",
      "en": "from the target level"
    },
    "customCount": {
      "ar": "{n} من إضافتك",
      "he": "{n} שהוספתם בעצמכם",
      "en": "{n} added by you"
    },
    "ready": {
      "ar": "جاهز",
      "he": "הכול מוכן",
      "en": "Ready"
    },
    "levelLabel": {
      "ar": "{subject}، الصف {grade}، {units} وحدات",
      "he": "{subject}, {grade}, {units} יח\"ל",
      "en": "{subject}, {grade}, {units} units"
    },
    "targetInLabel": {
      "ar": "(هدف: {n} وحدات)",
      "he": "(יעד: {n} יח\"ל)",
      "en": "(target: {n} units)"
    },
    "lengthLine": {
      "ar": "طول البرومبت: {n} حرفًا",
      "he": "אורך הפרומפט: {n} תווים",
      "en": "Prompt length: {n} characters"
    },
    "tooLong": {
      "ar": "اخترت مواضيع كثيرة والبرومبت طويل ({n} حرفًا، والحد {max}). تتعامل التطبيقات بشكل أفضل مع برومبت أقصر: ارجع واختر مواضيع أقل.",
      "he": "בחרתם הרבה נושאים והפרומפט ארוך ({n} תווים, המגבלה {max}). האפליקציות עובדות טוב יותר עם פרומפט קצר: חזרו ובחרו פחות נושאים.",
      "en": "You chose many topics and the prompt is long ({n} characters, the limit is {max}). Apps work better with a shorter prompt: go back and choose fewer topics."
    },
    "experimentalWarn": {
      "ar": "هذا المستوى تجريبي: ليست له بعد أمثلة جاهزة على نمط الامتحان.",
      "he": "הרמה הזאת ניסיונית: עדיין אין לה דוגמאות מוכנות במבנה של מבחן.",
      "en": "This level is experimental: it has no ready exam-style examples yet."
    },
    "openApp": {
      "ar": "افتح في تطبيق الذكاء الاصطناعي",
      "he": "פתחו באפליקציית הבינה המלאכותית",
      "en": "Open in your AI app"
    },
    "openHint": {
      "ar": "الأفضل: يضع البرومبت داخل التطبيق مباشرة.",
      "he": "הכי טוב: הפרומפט נכנס ישר לתוך האפליקציה.",
      "en": "Best: it puts the prompt straight into the app."
    },
    "copy": {
      "ar": "انسخ",
      "he": "העתקה",
      "en": "Copy"
    },
    "copied": {
      "ar": "تم النسخ.",
      "he": "הועתק.",
      "en": "Copied."
    },
    "copyFailed": {
      "ar": "تعذّر النسخ تلقائيًا: حدّد النص من «اعرض البرومبت».",
      "he": "לא הצלחנו להעתיק אוטומטית: סמנו את הטקסט תחת \"הצגת הפרומפט\".",
      "en": "We could not copy automatically: select the text under \"Show the prompt\"."
    },
    "copyFailedCopy": {
      "ar": "تعذّر النسخ تلقائيًا: حدّد النص من «اعرض البرومبت» وانسخه.",
      "he": "לא הצלחנו להעתיק אוטומטית: סמנו את הטקסט תחת \"הצגת הפרומפט\" והעתיקו אותו.",
      "en": "We could not copy automatically: select the text under \"Show the prompt\" and copy it."
    },
    "copyFailedShare": {
      "ar": "تعذّر النسخ تلقائيًا: اضغط «انسخ» أو حدّد النص من «اعرض البرومبت».",
      "he": "לא הצלחנו להעתיק אוטומטית: לחצו על \"העתקה\" או סמנו את הטקסט תחת \"הצגת הפרומפט\".",
      "en": "We could not copy automatically: press \"Copy\" or select the text under \"Show the prompt\"."
    },
    "sharedOk": {
      "ar": "تمّت المشاركة. والبرومبت منسوخ في الحافظة أيضًا.",
      "he": "בוצע. הפרומפט הועתק גם ללוח.",
      "en": "Done. The prompt is also copied to the clipboard."
    },
    "sharedDone": {
      "ar": "تمّت المشاركة.",
      "he": "בוצע.",
      "en": "Done."
    },
    "pasteIt": {
      "ar": "نسخنا البرومبت. الصقه في التطبيق.",
      "he": "העתקנו את הפרומפט. הדביקו אותו באפליקציה.",
      "en": "We copied the prompt. Paste it into the app."
    },
    "copiedOpen": {
      "ar": "نسخنا البرومبت. افتح التطبيق والصقه.",
      "he": "העתקנו את הפרומפט. פתחו את האפליקציה והדביקו אותו.",
      "en": "We copied the prompt. Open the app and paste it."
    },
    "levelNotFound": {
      "ar": "لم نجد هذا المستوى. ارجع واختر من جديد.",
      "he": "לא מצאנו את הרמה הזאת. חזרו ובחרו שוב.",
      "en": "We could not find this level. Go back and choose again."
    },
    "appsTitle": {
      "ar": "أو افتح التطبيق بنفسك والصق",
      "he": "או פתחו את האפליקציה בעצמכם והדביקו",
      "en": "Or open the app yourself and paste"
    },
    "photoNote": {
      "ar": "صوّر حلّك على الورقة وأرسله في التطبيق.",
      "he": "צלמו את הפתרון שלכם על הדף ושלחו אותו באפליקציה.",
      "en": "Photograph your solution on paper and send it in the app."
    },
    "examNote": {
      "ar": "هل تريد التدرّب على امتحان كامل؟ نزّله وارفعه إلى الأداة.",
      "he": "רוצים לתרגל מבחן שלם? הורידו אותו והעלו אותו לכלי.",
      "en": "Want to practise a full exam? Download it and upload it to the tool."
    },
    "examsLink": {
      "ar": "امتحانات رسمية سابقة",
      "he": "מבחנים רשמיים קודמים",
      "en": "Past official exams"
    },
    "chatTipTitle": {
      "ar": "💡 لماذا نفتح محادثة جديدة لكل مادة أو موضوع جديد؟",
      "he": "💡 למה פותחים שיחה חדשה לכל מקצוע או נושא חדש?",
      "en": "💡 Why a new chat for every new subject or topic?"
    },
    "chatTip1": {
      "ar": "يقرأ الذكاء الاصطناعي البرومبت في بداية المحادثة. وكلما طالت المحادثة نسي قواعده: فيعطيك الحل مباشرة، أو يخلط بين المواد. المحادثة الجديدة تعني قواعد جديدة ومركّزة على موضوعك.",
      "he": "הבינה המלאכותית קוראת את הפרומפט בתחילת השיחה. ככל שהשיחה מתארכת היא שוכחת את הכללים: היא מתחילה לתת את הפתרון מיד או לבלבל בין מקצועות. שיחה חדשה פירושה כללים חדשים וממוקדים בנושא שלכם.",
      "en": "The AI reads the prompt at the start of the chat. The longer the chat, the more it forgets its rules: it starts giving the answer straight away, or mixing subjects. A new chat means new rules, focused on your topic."
    },
    "chatTip2": {
      "ar": "✅ في المحادثة نفسها: مواضيع مرتبطة ببعضها، أو امتحان تجريبي.",
      "he": "✅ באותה שיחה: נושאים הקשורים זה לזה, או סימולציה.",
      "en": "✅ Same chat: topics that belong together, or a mock exam."
    },
    "chatTip3": {
      "ar": "🆕 محادثة جديدة: مادة أخرى، أو موضوع جديد في يوم آخر، أو محادثة طالت كثيرًا.",
      "he": "🆕 שיחה חדשה: מקצוע אחר, נושא חדש ביום אחר, או שיחה שהתארכה מאוד.",
      "en": "🆕 New chat: another subject, a new topic on another day, or a chat that has become very long."
    },
    "attach": {
      "ar": "📎 الصق البرومبت، ثم اضغط + في التطبيق وأرفق الصور (من 2 إلى 4 صور، كل صفحة في صورة، مستقيمة وبإضاءة جيدة)، وأرسلها معًا في رسالة واحدة.",
      "he": "📎 הדביקו את הפרומפט, ואז לחצו על + באפליקציה וצרפו את התמונות (2 עד 4 תמונות, כל עמוד בתמונה, ישר ובתאורה טובה), ושלחו את כולן יחד בהודעה אחת.",
      "en": "📎 Paste the prompt, then tap + in the app and attach the photos (2 to 4 photos, one page per photo, straight and well lit), and send them together in one message."
    },
    "showPrompt": {
      "ar": "اعرض البرومبت",
      "he": "הצגת הפרומפט",
      "en": "Show the prompt"
    },
    "loadError": {
      "ar": "تعذّر تحميل المنهاج. افتح الصفحة من الرابط الرسمي ثم حدّثها.",
      "he": "לא הצלחנו לטעון את התוכנית. פתחו את הדף מהקישור הרשמי ורעננו.",
      "en": "We could not load the curriculum. Open the page from the official link and refresh."
    },
    "logTitle": {
      "ar": "سجلّي",
      "he": "היומן שלי",
      "en": "My log"
    },
    "logWhyTitle": {
      "ar": "لماذا سجلّي؟ (اختياري، لكنه مفضّل)",
      "he": "למה היומן שלי? (לא חובה, אבל מומלץ)",
      "en": "Why My log? (optional, but recommended)"
    },
    "logWhyBody": {
      "ar": "المحادثة الجديدة لا تتذكّر أخطاءك. سجلّي يحفظها، ويجعل المدرّس يفحصك عليها في المرة القادمة.",
      "he": "שיחה חדשה לא זוכרת את הטעויות שלכם. היומן שלי שומר אותן, ועוזר למורה לבדוק אתכם עליהן בפעם הבאה.",
      "en": "A new chat does not remember your mistakes. My log keeps them, and lets the tutor test you on them next time."
    },
    "logHow": {
      "ar": "كيف؟",
      "he": "איך?",
      "en": "How?"
    },
    "logStep1": {
      "ar": "في آخر الجلسة اكتب للمدرّس: خلصت",
      "he": "בסוף השיחה כתבו למורה: סיימתי",
      "en": "At the end of the session write to the tutor: I am done"
    },
    "logStep2": {
      "ar": "انسخ الملخّص الذي يبدأ بـ NMI-LOG",
      "he": "העתיקו את הסיכום שמתחיל ב-NMI-LOG",
      "en": "Copy the summary that starts with NMI-LOG"
    },
    "logStep3": {
      "ar": "الصقه هنا واضغط «احفظ»",
      "he": "הדביקו אותו כאן ולחצו על \"שמירה\"",
      "en": "Paste it here and press \"Save\""
    },
    "logStep4": {
      "ar": "في المرة القادمة علّم «ذكّرني بأخطائي القديمة»",
      "he": "בפעם הבאה סמנו \"להזכיר לי את הטעויות הקודמות שלי\"",
      "en": "Next time tick \"Remind me of my old mistakes\""
    },
    "logPrivacy": {
      "ar": "السجل محفوظ على هذا الجهاز فقط. لا يصلنا منه شيء.",
      "he": "היומן נשמר במכשיר הזה בלבד. שום דבר ממנו לא מגיע אלינו.",
      "en": "The log is saved on this device only. Nothing reaches us."
    },
    "logLevel": {
      "ar": "المستوى: {level}",
      "he": "רמה: {level}",
      "en": "Level: {level}"
    },
    "logNoLevel": {
      "ar": "لم تختر مستواك بعد: جهّز برومبت من الصفحة الرئيسية ثم عد.",
      "he": "עוד לא בחרתם רמה: הכינו פרומפט בדף הראשי ואז חזרו.",
      "en": "You have not chosen a level yet: prepare a prompt on the main page, then come back."
    },
    "logPaste": {
      "ar": "الصق ملخّص الجلسة",
      "he": "הדביקו את סיכום השיחה",
      "en": "Paste the session summary"
    },
    "logSave": {
      "ar": "احفظ",
      "he": "שמירה",
      "en": "Save"
    },
    "logSaved": {
      "ar": "تم الحفظ.",
      "he": "נשמר.",
      "en": "Saved."
    },
    "logSavedTitle": {
      "ar": "الجلسات المحفوظة",
      "he": "סיכומים שמורים",
      "en": "Saved sessions"
    },
    "logDeleteLabel": {
      "ar": "امسح هذا المدخل",
      "he": "מחיקת הסיכום",
      "en": "Delete this entry"
    },
    "logDelete": {
      "ar": "امسح",
      "he": "מחיקה",
      "en": "Delete"
    },
    "logConfirmDelete": {
      "ar": "متأكد؟ اضغط مرة أخرى للمسح",
      "he": "בטוחים? לחצו שוב למחיקה",
      "en": "Sure? Tap again to delete"
    },
    "logClearAll": {
      "ar": "امسح الكل",
      "he": "מחיקת הכול",
      "en": "Delete all"
    },
    "logClose": {
      "ar": "رجوع إلى العدّة",
      "he": "חזרה לערכה",
      "en": "Back to the kit"
    },
    "logNoStorage": {
      "ar": "هذا المتصفح لا يستطيع الحفظ. لن يُحفظ السجل.",
      "he": "הדפדפן הזה לא יכול לשמור. היומן לא יישמר.",
      "en": "This browser cannot save. The log will not be saved."
    },
    "logNotSummary": {
      "ar": "هذا ليس ملخّصًا من المدرّس. انسخ الملخّص الذي يبدأ بـ NMI-LOG.",
      "he": "זה לא סיכום מהמורה. העתיקו את הסיכום שמתחיל ב-NMI-LOG.",
      "en": "This is not a summary from the tutor. Copy the summary that starts with NMI-LOG."
    },
    "logNeedLevel": {
      "ar": "اختر مستواك أولًا: جهّز برومبت من الصفحة الرئيسية ثم عد.",
      "he": "בחרו קודם רמה: הכינו פרומפט בדף הראשי ואז חזרו.",
      "en": "Choose your level first: prepare a prompt on the main page, then come back."
    },
    "subjectMath": {
      "ar": "رياضيات",
      "he": "מתמטיקה",
      "en": "Math"
    },
    "grade10": {
      "ar": "العاشر",
      "he": "כיתה י׳",
      "en": "Grade 10"
    },
    "grade11": {
      "ar": "الحادي عشر",
      "he": "כיתה י״א",
      "en": "Grade 11"
    },
    "grade12": {
      "ar": "الثاني عشر",
      "he": "כיתה י״ב",
      "en": "Grade 12"
    }
  };

  /* the text of a key in a language; {name} is replaced by params.name; a missing key or language falls back to Arabic */
  function t(lang, key, params) {
    const entry = STRINGS[key];
    if (!entry) return key;
    let text = entry[lang] != null ? entry[lang] : entry.ar;
    Object.keys(params || {}).forEach(function (name) {
      text = text.split('{' + name + '}').join(String(params[name]));
    });
    return text;
  }

  /* the language of the browser: Hebrew or English, otherwise Arabic */
  function detect(browserLanguage) {
    const primary = String(browserLanguage || '').toLowerCase().split('-')[0];
    if (primary === 'he' || primary === 'iw') return 'he';
    if (primary === 'en') return 'en';
    return 'ar';
  }

  /* the choice of the student is kept in localStorage; every access is inside try/catch */
  function loadLang(storage) {
    try {
      const value = storage && storage.getItem(STORAGE_KEY);
      return LANGS.indexOf(value) !== -1 ? value : null;
    } catch (error) {
      return null;
    }
  }

  function saveLang(storage, lang) {
    try {
      if (storage && LANGS.indexOf(lang) !== -1) storage.setItem(STORAGE_KEY, lang);
    } catch (error) { /* a browser that cannot store: the choice only lasts until the page is closed */ }
  }

  const HEBREW_IN_PARENS = /\(([^()]*[\u0590-\u05ff][^()]*)\)/;

  /* The Hebrew term of a title like "الاحتمال (הסתברות)", or null when the title has none. */
  function hebrewTerm(full) {
    const match = HEBREW_IN_PARENS.exec(String(full || ''));
    return match ? match[1].trim() : null;
  }

  /* "English name (Hebrew name)": the English reader can read the first, and the exams use the second. */
  function withEnglish(english, hebrew, arabic) {
    if (english && hebrew) return english + ' (' + hebrew + ')';
    return english || hebrew || arabic;
  }

  /* The name of a topic: Arabic in Arabic; in Hebrew the Hebrew term when there is one (the curriculum is Arabic, and the
     terms of the exams are Hebrew), otherwise the Arabic title; in English "English name (Hebrew name)". */
  function topicName(topic, lang) {
    if (lang === 'ar') return topic.title;
    if (lang === 'en') return withEnglish(topic.title_en, hebrewTerm(topic.title_full), topic.title);
    return hebrewTerm(topic.title_full) || topic.title;
  }

  function groupName(topic, lang) {
    if (!topic.group) return topic.group;
    if (lang === 'ar') return topic.group;
    if (lang === 'en') return withEnglish(topic.group_en, hebrewTerm(topic.group_full), topic.group);
    return hebrewTerm(topic.group_full) || topic.group;
  }

  function count(lang, n) {
    if (n === 1) return t(lang, 'topicOne');
    if (n === 2) return t(lang, 'topicTwo');
    return t(lang, lang === 'ar' && n > 10 ? 'topicMany' : 'topicFew', { n: n });
  }

  function gradeName(lang, id) {
    return t(lang, 'grade' + id);
  }

  /* "رياضيات، الصف العاشر، 3 وحدات" / "מתמטיקה, כיתה י׳, 3 יח"ל" / "Math, Grade 10, 3 units" */
  function levelLabel(lang, level) {
    return t(lang, 'levelLabel', { subject: t(lang, 'subject' + level.subject.charAt(0).toUpperCase() + level.subject.slice(1)), grade: gradeName(lang, level.grade), units: level.units });
  }

  return {
    LANGS: LANGS, NAMES: NAMES, DIR: DIR, STORAGE_KEY: STORAGE_KEY, STRINGS: STRINGS,
    t: t, detect: detect, loadLang: loadLang, saveLang: saveLang, hebrewTerm: hebrewTerm, topicName: topicName,
    groupName: groupName, count: count, gradeName: gradeName, levelLabel: levelLabel
  };
});
