"use strict";

const COPY = {
  "en": {
    "title": "NMI — Your learning companion",
    "skip": "Skip to conversation",
    "sidebar": "Sidebar",
    "navigation": "Main navigation",
    "newChat": "New chat",
    "search": "Search chats",
    "history": "Conversations",
    "historyCaption": "Examples and saved demo chats",
    "progress": "Progress",
    "curriculum": "Curriculum",
    "library": "Library",
    "settings": "Settings",
    "yourSpace": "Your learning space",
    "preview": "Design preview",
    "companion": "Your learning companion",
    "collapse": "Collapse sidebar",
    "expand": "Expand sidebar",
    "dark": "Dark theme",
    "light": "Light theme",
    "demo": "Demo",
    "welcome": "What would you like to learn today?",
    "welcomeBody": "A small question, a difficult idea, or a fresh start. Let’s think together.",
    "conversation": "Conversation",
    "questionLabel": "Your message to NMI",
    "placeholder": "Ask about anything you want to understand…",
    "learnTogether": "Think it through",
    "keyboardHint": "Enter to send",
    "send": "Send message",
    "stop": "Stop demo reply",
    "suggestExplain": "Explain a concept",
    "suggestMath": "Work through a problem",
    "suggestCode": "Help me code",
    "suggestWriting": "Improve my writing",
    "demoNotice": "Mock replies, saved in this browser. Use sample questions only.",
    "learningSpace": "Your learning space",
    "progressIntro": "Academic progress, grounded in assessed evidence.",
    "progressEmpty": "Your learning journey starts here",
    "progressBody": "No learning attempts have been recorded. Demo conversations do not award grades or change mastery.",
    "startConversation": "Start a conversation",
    "curriculumIntro": "Mathematics, Physics and Chemistry, aligned only when verified sources are available.",
    "curriculumEmpty": "No verified curriculum added yet",
    "curriculumBody": "We won’t invent official requirements. You can still start a conversation about any subject, without selecting a curriculum first.",
    "askAnything": "Ask about any subject",
    "inspiration": "A starting point",
    "libraryIntro": "Explore an academic idea or start a conversation about something else.",
    "libraryNote": "Illustrative examples, not official curricula.",
    "settingsIntro": "A comfortable space, your way.",
    "languageLabel": "Interface language",
    "languageHelp": "Arabic or English, with the right reading direction.",
    "appearance": "Appearance",
    "appearanceHelp": "Choose what feels comfortable to read.",
    "privacy": "Preview privacy",
    "privacyBody": "Demo profile and conversations are saved in this browser. Use sample details only; anyone using this browser profile can see them. No account or cloud sync.",
    "close": "Close",
    "searchQuery": "A word from a title or message",
    "searchPlaceholder": "Search demo conversations…",
    "noResults": "No matching conversations. Try another word.",
    "searchHelp": "Search the examples and saved demo messages.",
    "empty": "Write a message before sending.",
    "tooLong": "Keep your message within 4,000 characters.",
    "thinking": "Preparing a demo reply…",
    "stopped": "Demo reply stopped.",
    "sent": "Demo reply ready.",
    "copied": "Copied",
    "copyCode": "Copy code",
    "copyFailed": "Copy is unavailable. Select the code to copy it.",
    "you": "You",
    "assistant": "NMI",
    "hint": "Give me a hint",
    "check": "Check my understanding",
    "notes": "Learning notes",
    "demoPath": "Illustrative learning path",
    "pathLabel": "Demo: one of three steps explored",
    "pathBody": "Idea explored → guided practice → explain it yourself.",
    "notAssessment": "This is a display example, not a mastery score or saved assessment.",
    "mathTitle": "Making sense of fractions",
    "codeTitle": "My first Python function",
    "writingTitle": "Finding the right words",
    "mathDescription": "Make a tricky idea click with a simple example.",
    "codeDescription": "Read a short function, one line at a time.",
    "writingDescription": "Express an idea more clearly and confidently.",
    "explainPrompt": "Can you help me understand a new concept?",
    "mathPrompt": "How do I add one half and one quarter?",
    "codePrompt": "Can you show me how a Python function works?",
    "writingPrompt": "How can I make my writing clearer?",
    "mathHeading": "Different pieces. The same whole.",
    "mathIntro": "Think of a fraction as part of something. Before we add two fractions, we need to describe those parts using the same-sized pieces.",
    "mathStep1": "One half is the same amount as two quarters.",
    "mathStep2": "Now add the quarters: two pieces plus one piece makes three.",
    "mathStep3": "Keep the denominator at four because the size of each piece has not changed.",
    "mathFollowup": "Would you like a hint to try a similar question yourself?",
    "formulaSpoken": "One half plus one quarter equals two quarters plus one quarter, which equals three quarters.",
    "codeHeading": "A function is a reusable little instruction.",
    "codeIntro": "Give it an input, let it do one job, and use the result. Here is a small example:",
    "codeAfter": "The name is the input. The return statement sends a greeting back. Calling the function runs those instructions.",
    "codeFollowup": "What do you think would change if we passed a different name?",
    "writingHeading": "Start with the idea you want to communicate.",
    "writingIntro": "Clear writing gives each sentence one job. Put the main idea first, choose concrete words, and remove anything that doesn’t help the reader.",
    "writingBefore": "Before: “Due to the fact that I was tired, I made the decision to rest.”",
    "writingAfter": "After: “I was tired, so I rested.”",
    "writingFollowup": "Share a short sentence you would like to improve, without personal details.",
    "generalHeading": "Let’s find a good place to start.",
    "generalIntro": "Tell me the topic and the part you want to understand. We can build an explanation around a simple example, work through a question, or explore an idea together.",
    "generalFollowup": "Would you prefer a quick explanation or a step-by-step example?",
    "generalNote": "This is a predefined preview reply. A live tutor is not connected.",
    "hintHeading": "One small nudge.",
    "mathHint": "Imagine cutting the half into two equal pieces. How many quarters do you have now?",
    "codeHint": "Follow the value of name from the function call into the return statement.",
    "writingHint": "Look for a long phrase that could become one familiar word.",
    "generalHint": "Start with what you already know. Which part feels unclear?",
    "checkHeading": "A quick check, if you’d like.",
    "mathCheck": "Which is larger: one half or one quarter? Explain your choice in a sentence.",
    "codeCheck": "What is the input to greet, and what does the function return?",
    "writingCheck": "Can you rewrite “at this point in time” in one word?",
    "generalCheck": "How would you explain the idea to a friend in one sentence?",
    "checkNote": "Practice prompt only. This preview does not grade your answer.",
    "draftPrompt": "A starting point is ready. Edit it or send it.",
    "newLabel": "New conversation",
    "profile": "Profile",
    "demoProfile": "Demonstration profile",
    "editProfile": "Edit demo profile",
    "profileIntro": "A space to understand how you learn. At your own pace.",
    "subjects": "Academic subjects",
    "subjectNote": "Choose a focus for future academic tracking. You can still chat about any topic.",
    "strengths": "Strengths",
    "weaknesses": "Foundations to revisit",
    "noEvidence": "No assessed learning evidence yet.",
    "skillProgress": "Progress by skill",
    "viewProgress": "View progress",
    "learningHistory": "Learning history",
    "demoHistoryNote": "These are demo conversations, not assessed learning attempts.",
    "continueLearning": "Continue learning",
    "onboardingTitle": "Make room for your next idea.",
    "onboardingNote": "Use a nickname and sample details only. This demo is saved in this browser, without an account.",
    "demoName": "Demo nickname",
    "country": "Country of study",
    "grade": "Grade",
    "chooseGrade": "Choose your grade",
    "grade9": "Grade 9",
    "grade10": "Grade 10",
    "grade11": "Grade 11",
    "grade12": "Grade 12",
    "avatarOption": "Show an illustrated avatar",
    "cancel": "Cancel",
    "startLearning": "Start exploring",
    "saveProfile": "Save demo profile",
    "invalidName": "Enter a demo nickname, up to 40 characters.",
    "invalidCountry": "Choose one of the ten supported countries.",
    "invalidGrade": "Choose Grade 9, 10, 11 or 12.",
    "storageUnavailable": "This browser could not save the demo. You can keep exploring in this tab.",
    "storageInvalid": "Saved demo data could not be read safely. It has not been changed. Use Settings to reset demo data.",
    "storageConflict": "The saved demo changed in another tab. Reload to use that version; this tab will not overwrite it.",
    "clearDemo": "Reset saved demo",
    "clearConfirm": "Reset this browser's NMI demo profile and conversations? This does not touch real student files.",
    "resetHelp": "Clears this preview's profile, chats and preferences only.",
    "demoLimit": "The demo has reached its storage limit. Reset demo data in Settings to start again.",
    "mathSubject": "Mathematics",
    "scienceSubject": "Science",
    "codeSubject": "Programming",
    "writingSubject": "Writing",
    "sampleProgress": "Show a fictional progress example",
    "hideSample": "Hide fictional example",
    "sampleLabel": "Fictional example — not your progress",
    "sampleNote": "These fixed values show the design only. Chatting does not change them.",
    "fractionsSkill": "Equivalent fractions",
    "equationsSkill": "One-step equations",
    "unitsSkill": "Interpreting units",
    "sampleStrength": "Explains equivalent parts using a visual example.",
    "sampleWeakness": "Needs another check when changing denominators.",
    "foundationTitle": "A small step back. Then forward.",
    "foundationBody": "An earlier foundation can help with a current goal. Your enrolled grade stays the same.",
    "recoveryStep1": "Original goal: rearrange an equation.",
    "recoveryStep2": "Foundation: understand equivalent fractions.",
    "recoveryStep3": "Short check: why are one half and two quarters equal?",
    "recoveryStep4": "Return: use equal values in the original equation.",
    "recoveryNote": "Illustrative teaching sequence only. No answer is graded or weakness recorded in this preview.",
    "languages": "Languages",
    "academicFocus": "Academic focus in V1",
    "academicScope": "Curriculum alignment, skill assessment and academic progress are limited to Mathematics, Physics and Chemistry in V1.",
    "openChatScope": "Ask about any topic. Other conversations are saved without academic scores.",
    "conversationOnly": "Conversation only · No academic mastery score",
    "retainedInterests": "Earlier interests preserved for conversation only:",
    "physicsSubject": "Physics",
    "chemistrySubject": "Chemistry",
    "atomsSkill": "Atoms and molecules",
    "noAcademicEvidence": "No assessed attempts",
    "sourceUnavailable": "Verified curriculum not loaded",
    "moreSubjects": "More academic subjects will be added gradually.",
    "physicsTitle": "Making sense of motion",
    "chemistryTitle": "Exploring atoms and molecules",
    "physicsPrompt": "Can you explain velocity with one simple example?",
    "chemistryPrompt": "What is the difference between an atom and a molecule?",
    "physicsHeading": "Velocity describes motion in a direction.",
    "physicsIntro": "A cyclist travelling east at 5 metres per second has both a speed and a direction. Together, those describe velocity. Changing direction changes velocity, even if speed stays the same.",
    "physicsFollowup": "If the cyclist turns west at the same speed, what changed?",
    "physicsHint": "Compare the direction before and after the turn.",
    "physicsCheck": "Two cyclists move at the same speed in opposite directions. Is their velocity the same?",
    "chemistryHeading": "A molecule contains atoms bonded together.",
    "chemistryIntro": "Think of an atom as one building block of an element. A water molecule contains two hydrogen atoms bonded to one oxygen atom. We can focus on that distinction before looking at chemical reactions.",
    "chemistryFollowup": "Would you like to compare one atom with a water molecule?",
    "chemistryHint": "Count the atoms that make up one molecule of water.",
    "chemistryCheck": "How many atoms are in one water molecule?",
    "academicStarters": "Explore the V1 academic subjects",
    "openStarters": "More ways to start a conversation",
    "untrackedLibrary": "Conversation example · No academic tracking",
    "chooseCountry": "Choose your country",
    "legacyCountry": "Your previous country is still saved. Choose a supported country to update this demo profile."
  },
  "ar": {
    "title": "NMI — رفيق تعلّمك",
    "skip": "انتقل إلى المحادثة",
    "sidebar": "الشريط الجانبي",
    "navigation": "التنقل الرئيسي",
    "newChat": "محادثة جديدة",
    "search": "البحث في المحادثات",
    "history": "المحادثات",
    "historyCaption": "أمثلة ومحادثات تجريبية محفوظة",
    "progress": "تقدّمي",
    "curriculum": "المنهج الدراسي",
    "library": "المكتبة",
    "settings": "الإعدادات",
    "yourSpace": "مساحتك للتعلّم",
    "preview": "معاينة تجريبية",
    "companion": "رفيق تعلّمك",
    "collapse": "طي الشريط الجانبي",
    "expand": "إظهار الشريط الجانبي",
    "dark": "الوضع الداكن",
    "light": "الوضع الفاتح",
    "demo": "تجريبي",
    "welcome": "ماذا تريد أن تتعلّم اليوم؟",
    "welcomeBody": "سؤال صغير، فكرة صعبة، أو بداية جديدة. لنفكّر معًا.",
    "conversation": "المحادثة",
    "questionLabel": "رسالتك إلى NMI",
    "placeholder": "اسأل عن أي شيء تريد فهمه…",
    "learnTogether": "لنفهم معًا",
    "keyboardHint": "Enter للإرسال",
    "send": "إرسال الرسالة",
    "stop": "إيقاف الرد التجريبي",
    "suggestExplain": "بسّط لي فكرة",
    "suggestMath": "فكّر معي في مسألة",
    "suggestCode": "ساعدني في البرمجة",
    "suggestWriting": "طوّر كتابتي",
    "demoNotice": "ردود تجريبية تُحفظ في هذا المتصفح. استخدم أسئلة افتراضية فقط.",
    "learningSpace": "مساحة التعلّم",
    "progressIntro": "تقدّم أكاديمي يستند إلى أدلة تعلّم مُقيّمة.",
    "progressEmpty": "ستبدأ رحلة تقدّمك هنا",
    "progressBody": "لا توجد محاولات تعلّم مسجّلة. المحادثات التجريبية لا تمنح درجات ولا تغيّر مستوى الإتقان.",
    "startConversation": "ابدأ محادثة",
    "curriculumIntro": "الرياضيات والفيزياء والكيمياء، مع مواءمة المناهج عند توافر مصادر موثّقة فقط.",
    "curriculumEmpty": "لم يُضَف منهج موثّق بعد",
    "curriculumBody": "لن نخترع متطلبات رسمية. يمكنك بدء محادثة عن أي موضوع، دون اختيار منهج مسبقًا.",
    "askAnything": "اسأل عن أي موضوع",
    "inspiration": "بداية لفكرة",
    "libraryIntro": "استكشف فكرة أكاديمية أو ابدأ محادثة عن موضوع آخر.",
    "libraryNote": "أمثلة توضيحية، وليست مناهج رسمية.",
    "settingsIntro": "مساحة مريحة، على طريقتك.",
    "languageLabel": "لغة الواجهة",
    "languageHelp": "العربية أو الإنجليزية، مع اتجاه مناسب للنص.",
    "appearance": "المظهر",
    "appearanceHelp": "اختر ما يناسبك أثناء القراءة.",
    "privacy": "خصوصية المعاينة",
    "privacyBody": "يُحفظ الملف والمحادثات التجريبية في هذا المتصفح. استخدم بيانات افتراضية فقط؛ يمكن لمن يستخدم ملف المتصفح نفسه رؤيتها. لا يوجد حساب أو مزامنة سحابية.",
    "close": "إغلاق",
    "searchQuery": "كلمة من عنوان أو رسالة",
    "searchPlaceholder": "ابحث في المحادثات التجريبية…",
    "noResults": "لا توجد محادثات مطابقة. جرّب كلمة أخرى.",
    "searchHelp": "ابحث في الأمثلة والرسائل التجريبية المحفوظة.",
    "empty": "اكتب رسالة قبل الإرسال.",
    "tooLong": "اجعل رسالتك ضمن ٤٠٠٠ حرف.",
    "thinking": "جارٍ إعداد رد تجريبي…",
    "stopped": "أُوقف الرد التجريبي.",
    "sent": "الرد التجريبي جاهز.",
    "copied": "نُسخ",
    "copyCode": "نسخ الكود",
    "copyFailed": "النسخ غير متاح. حدّد الكود لنسخه.",
    "you": "أنت",
    "assistant": "NMI",
    "hint": "أريد تلميحًا",
    "check": "تحقّق من فهمي",
    "notes": "ملاحظات التعلّم",
    "demoPath": "مسار تعلّم توضيحي",
    "pathLabel": "مثال: استكشاف خطوة من ثلاث",
    "pathBody": "استكشاف الفكرة، ثم تدريب موجّه، ثم شرحها بكلماتك.",
    "notAssessment": "هذا مثال للعرض، وليس درجة إتقان أو تقييمًا محفوظًا.",
    "mathTitle": "فهم الكسور ببساطة",
    "codeTitle": "أول دالة في بايثون",
    "writingTitle": "اختيار الكلمات المناسبة",
    "mathDescription": "فكرة صعبة تصبح أوضح بمثال بسيط.",
    "codeDescription": "اقرأ دالة قصيرة، سطرًا بعد سطر.",
    "writingDescription": "عبّر عن فكرتك بوضوح وثقة.",
    "explainPrompt": "هل يمكنك مساعدتي في فهم فكرة جديدة؟",
    "mathPrompt": "كيف أجمع النصف والربع؟",
    "codePrompt": "هل يمكنك أن تشرح لي كيف تعمل دالة في بايثون؟",
    "writingPrompt": "كيف أجعل كتابتي أكثر وضوحًا؟",
    "mathHeading": "أجزاء مختلفة، من الكلّ نفسه.",
    "mathIntro": "تخيّل الكسر جزءًا من شيء كامل. قبل جمع كسرين، نحتاج إلى التعبير عنهما بقطع متساوية الحجم.",
    "mathStep1": "النصف يساوي المقدار نفسه الذي يساويه ربعان.",
    "mathStep2": "نجمع الأرباع الآن: قطعتان مع قطعة واحدة تصبح ثلاث قطع.",
    "mathStep3": "يبقى المقام أربعة، لأن حجم كل قطعة لم يتغيّر.",
    "mathFollowup": "هل تريد تلميحًا لتجرّب سؤالًا مشابهًا بنفسك؟",
    "formulaSpoken": "نصف زائد ربع يساوي ربعين زائد ربع، أي ثلاثة أرباع.",
    "codeHeading": "الدالة مجموعة تعليمات يمكنك إعادة استخدامها.",
    "codeIntro": "أعطها مدخلًا، ودعها تؤدّي مهمة واحدة، ثم استخدم النتيجة. إليك مثالًا قصيرًا:",
    "codeAfter": "الاسم هو المدخل. تعيد عبارة الإرجاع رسالة ترحيب. عند استدعاء الدالة تُنفَّذ هذه التعليمات.",
    "codeFollowup": "ما الذي سيتغيّر برأيك إذا مرّرنا اسمًا مختلفًا؟",
    "writingHeading": "ابدأ بالفكرة التي تريد إيصالها.",
    "writingIntro": "في الكتابة الواضحة، لكل جملة دور. قدّم الفكرة الرئيسية أولًا، واختر كلمات محدّدة، واحذف ما لا يساعد القارئ.",
    "writingBefore": "قبل: «نظرًا إلى حقيقة أنني كنت متعبًا، اتخذت قرارًا بالراحة».",
    "writingAfter": "بعد: «كنت متعبًا، فاسترحت».",
    "writingFollowup": "شارك جملة قصيرة تريد تحسينها، دون تفاصيل شخصية.",
    "generalHeading": "لنجد نقطة بداية مناسبة.",
    "generalIntro": "أخبرني بالموضوع والجزء الذي تريد فهمه. يمكننا بناء شرح حول مثال بسيط، أو التفكير في سؤال، أو استكشاف فكرة معًا.",
    "generalFollowup": "هل تفضّل شرحًا سريعًا أم مثالًا خطوة بخطوة؟",
    "generalNote": "هذا رد تجريبي مكتوب مسبقًا. المعلّم الذكي غير متصل في هذه المعاينة.",
    "hintHeading": "تلميح صغير.",
    "mathHint": "تخيّل تقسيم النصف إلى قطعتين متساويتين. كم ربعًا أصبح لديك؟",
    "codeHint": "تتبّع قيمة الاسم من استدعاء الدالة إلى عبارة الإرجاع.",
    "writingHint": "ابحث عن عبارة طويلة يمكن استبدالها بكلمة مألوفة.",
    "generalHint": "ابدأ بما تعرفه بالفعل. أي جزء يبدو غير واضح؟",
    "checkHeading": "سؤال قصير، إن أحببت.",
    "mathCheck": "أيهما أكبر: النصف أم الربع؟ اشرح اختيارك في جملة.",
    "codeCheck": "ما المدخل الذي تستقبله الدالة، وما النتيجة التي تعيدها؟",
    "writingCheck": "هل يمكنك اختصار «في هذه اللحظة الزمنية» بكلمة واحدة؟",
    "generalCheck": "كيف تشرح الفكرة لصديق في جملة واحدة؟",
    "checkNote": "سؤال تدريبي فقط. هذه المعاينة لا تقيّم إجابتك.",
    "draftPrompt": "بداية مقترحة جاهزة. عدّلها أو أرسلها.",
    "newLabel": "محادثة جديدة",
    "profile": "ملفي",
    "demoProfile": "ملف تجريبي",
    "editProfile": "تعديل الملف التجريبي",
    "profileIntro": "مساحة لفهم طريقة تعلّمك، بالوتيرة التي تناسبك.",
    "subjects": "المواد الأكاديمية",
    "subjectNote": "اختر مجالًا للتتبّع الأكاديمي مستقبلًا. يمكنك الاستمرار في المحادثة عن أي موضوع.",
    "strengths": "نقاط القوة",
    "weaknesses": "أساسيات تحتاج إلى دعم",
    "noEvidence": "لا توجد أدلة تعلّم مُقيّمة بعد.",
    "skillProgress": "التقدّم حسب المهارة",
    "viewProgress": "عرض التقدّم",
    "learningHistory": "سجل التعلّم",
    "demoHistoryNote": "هذه محادثات تجريبية، وليست محاولات تعلّم مُقيّمة.",
    "continueLearning": "متابعة التعلّم",
    "onboardingTitle": "لنجهّز مساحة لفكرتك القادمة.",
    "onboardingNote": "استخدم اسمًا مستعارًا وبيانات تجريبية فقط. تُحفظ هذه المعاينة في هذا المتصفح، دون حساب.",
    "demoName": "الاسم المستعار التجريبي",
    "country": "بلد الدراسة",
    "grade": "الصف الدراسي",
    "chooseGrade": "اختر صفّك",
    "grade9": "الصف التاسع",
    "grade10": "الصف العاشر",
    "grade11": "الصف الحادي عشر",
    "grade12": "الصف الثاني عشر",
    "avatarOption": "إظهار صورة شخصية مرسومة",
    "cancel": "إلغاء",
    "startLearning": "ابدأ الاستكشاف",
    "saveProfile": "حفظ الملف التجريبي",
    "invalidName": "أدخل اسمًا مستعارًا تجريبيًا لا يتجاوز ٤٠ حرفًا.",
    "invalidCountry": "اختر بلدًا من البلدان العشرة المدعومة.",
    "invalidGrade": "اختر الصف التاسع أو العاشر أو الحادي عشر أو الثاني عشر.",
    "storageUnavailable": "تعذّر حفظ المعاينة في هذا المتصفح. يمكنك متابعة الاستكشاف في علامة التبويب هذه.",
    "storageInvalid": "تعذّرت قراءة البيانات التجريبية المحفوظة بأمان. لم نغيّرها. يمكنك إعادة ضبط بيانات المعاينة من الإعدادات.",
    "storageConflict": "تغيّرت المعاينة المحفوظة في علامة تبويب أخرى. أعد التحميل لاستخدامها؛ لن نستبدلها من هنا.",
    "clearDemo": "إعادة ضبط المعاينة",
    "clearConfirm": "هل تريد إعادة ضبط الملف والمحادثات التجريبية في هذا المتصفح؟ لن تتأثر ملفات الطلاب الحقيقية.",
    "resetHelp": "يمسح ملف هذه المعاينة ومحادثاتها وتفضيلاتها فقط.",
    "demoLimit": "وصلت المعاينة إلى حدّ التخزين. أعد ضبط بياناتها من الإعدادات للبدء من جديد.",
    "mathSubject": "الرياضيات",
    "scienceSubject": "العلوم",
    "codeSubject": "البرمجة",
    "writingSubject": "الكتابة",
    "sampleProgress": "عرض مثال تقدّم افتراضي",
    "hideSample": "إخفاء المثال الافتراضي",
    "sampleLabel": "مثال افتراضي — ليس تقدّمك الفعلي",
    "sampleNote": "قيم ثابتة لتوضيح التصميم فقط. لا تتغيّر عند المحادثة.",
    "fractionsSkill": "الكسور المتكافئة",
    "equationsSkill": "معادلات من خطوة واحدة",
    "unitsSkill": "فهم الوحدات",
    "sampleStrength": "يشرح الأجزاء المتكافئة باستخدام مثال بصري.",
    "sampleWeakness": "يحتاج إلى تحقّق إضافي عند تغيير المقامات.",
    "foundationTitle": "خطوة إلى الأساس، ثم نكمل.",
    "foundationBody": "قد تساعدك مهارة سابقة في هدفك الحالي. يبقى صفّك الدراسي كما هو.",
    "recoveryStep1": "الهدف الأصلي: إعادة ترتيب معادلة.",
    "recoveryStep2": "الأساس المطلوب: فهم الكسور المتكافئة.",
    "recoveryStep3": "تحقّق قصير: لماذا يساوي النصف ربعين؟",
    "recoveryStep4": "العودة: استخدم القيم المتساوية في المعادلة الأصلية.",
    "recoveryNote": "تسلسل تعليمي توضيحي فقط. لا تُقيَّم إجابات ولا تُسجَّل نقاط ضعف في هذه المعاينة.",
    "languages": "اللغات",
    "academicFocus": "المواد الأكاديمية في الإصدار الأول",
    "academicScope": "تقتصر مواءمة المناهج وتقييم المهارات والتقدّم الأكاديمي في الإصدار الأول على الرياضيات والفيزياء والكيمياء.",
    "openChatScope": "اسأل عن أي موضوع. تُحفظ المحادثات الأخرى دون درجات إتقان أكاديمية.",
    "conversationOnly": "محادثة فقط · دون درجة إتقان أكاديمية",
    "retainedInterests": "اهتمامات سابقة محفوظة للمحادثة فقط:",
    "physicsSubject": "الفيزياء",
    "chemistrySubject": "الكيمياء",
    "atomsSkill": "الذرات والجزيئات",
    "noAcademicEvidence": "لا توجد محاولات مُقيّمة",
    "sourceUnavailable": "لم يُضَف منهج موثّق",
    "moreSubjects": "ستُضاف مواد أكاديمية أخرى تدريجيًا.",
    "physicsTitle": "فهم الحركة",
    "chemistryTitle": "استكشاف الذرات والجزيئات",
    "physicsPrompt": "هل يمكنك شرح السرعة المتجهة بمثال بسيط؟",
    "chemistryPrompt": "ما الفرق بين الذرة والجزيء؟",
    "physicsHeading": "السرعة المتجهة تصف الحركة في اتجاه معيّن.",
    "physicsIntro": "يتحرّك درّاج شرقًا بسرعة خمسة أمتار في الثانية. يصف مقدار السرعة والاتجاه معًا سرعته المتجهة. تتغيّر السرعة المتجهة عند تغيير الاتجاه، حتى لو بقي مقدار السرعة ثابتًا.",
    "physicsFollowup": "إذا اتجه الدرّاج غربًا بالمقدار نفسه من السرعة، فما الذي تغيّر؟",
    "physicsHint": "قارن الاتجاه قبل الاستدارة وبعدها.",
    "physicsCheck": "يتحرّك درّاجان بالمقدار نفسه من السرعة في اتجاهين متعاكسين. هل سرعتهما المتجهة متساوية؟",
    "chemistryHeading": "يتكوّن الجزيء من ذرات مترابطة.",
    "chemistryIntro": "تخيّل الذرة وحدة بناء لعنصر. يحتوي جزيء الماء على ذرتَي هيدروجين مرتبطتين بذرة أكسجين واحدة. يمكننا فهم هذا الفرق قبل الانتقال إلى التفاعلات الكيميائية.",
    "chemistryFollowup": "هل تريد مقارنة ذرة واحدة بجزيء ماء؟",
    "chemistryHint": "عدّ الذرات التي تكوّن جزيئًا واحدًا من الماء.",
    "chemistryCheck": "كم ذرة يحتوي جزيء ماء واحد؟",
    "academicStarters": "استكشف المواد الأكاديمية للإصدار الأول",
    "openStarters": "طرق أخرى لبدء محادثة",
    "untrackedLibrary": "مثال محادثة · دون تتبّع أكاديمي",
    "chooseCountry": "اختر بلد الدراسة",
    "legacyCountry": "ما زال بلدك السابق محفوظًا. اختر بلدًا مدعومًا لتحديث هذا الملف التجريبي."
  }
};

const SUPPORTED_GRADES = Object.freeze([9, 10, 11, 12]);
const COUNTRIES = Object.freeze([{"code":"US","en":"United States","ar":"الولايات المتحدة"},{"code":"GB","en":"United Kingdom","ar":"المملكة المتحدة"},{"code":"CA","en":"Canada","ar":"كندا"},{"code":"DE","en":"Germany","ar":"ألمانيا"},{"code":"CH","en":"Switzerland","ar":"سويسرا"},{"code":"SG","en":"Singapore","ar":"سنغافورة"},{"code":"AU","en":"Australia","ar":"أستراليا"},{"code":"NL","en":"Netherlands","ar":"هولندا"},{"code":"QA","en":"Qatar","ar":"قطر"},{"code":"AE","en":"United Arab Emirates","ar":"الإمارات العربية المتحدة"}]);
const countryByCode = code => COUNTRIES.find(country => country.code === code);
const countryCodeFor = p => p?.countryCode || COUNTRIES.find(country => country.en === p?.country || country.ar === p?.country)?.code || '';
const ACADEMIC_SUBJECTS = Object.freeze(['math', 'physics', 'chemistry']);
// Legacy interests remain readable; they never become academic capabilities.
const SUBJECTS = Object.freeze([...ACADEMIC_SUBJECTS, 'science', 'code', 'writing']);
function supportsAcademicSubject(subject) { return ACADEMIC_SUBJECTS.includes(subject); }
function academicPolicy(subject) {
  const eligible = supportsAcademicSubject(subject);
  return { chatAllowed: true, preserveConversation: true, curriculumEligible: eligible, assessmentEligible: eligible, masteryEligible: eligible, progressEligible: eligible };
}
const DEMO_KEY = 'nmi-preview-demo-v1';
const LIMITS = Object.freeze({ chats: 30, messages: 80, bytes: 1000000 });
function validProfile(p) {
  if (p?.countryCode !== undefined && (!countryByCode(p.countryCode) || p.country !== countryByCode(p.countryCode).en)) return false;
  return p && typeof p === 'object' && typeof p.name === 'string' && p.name.trim().length > 0 && p.name.length <= 40 && typeof p.country === 'string' && p.country.trim().length > 0 && p.country.length <= 60 && SUPPORTED_GRADES.includes(p.grade) && ['ar', 'en'].includes(p.language) && typeof p.avatar === 'boolean' && Array.isArray(p.subjects) && p.subjects.length <= SUBJECTS.length && new Set(p.subjects).size === p.subjects.length && p.subjects.every(s => SUBJECTS.includes(s));
}
function parseDemo(raw) {
  if (raw === null) return null;
  if (raw.length > LIMITS.bytes) throw new Error('Invalid demo size');
  const data = JSON.parse(raw);
  if (!data || data.version !== 1 || !validProfile(data.profile) || !Array.isArray(data.chats) || data.chats.length > LIMITS.chats) throw new Error('Invalid demo state');
  const kinds = [...ACADEMIC_SUBJECTS, 'code', 'writing', 'general'];
  const ids = new Set();
  const cleanChats = data.chats.map(c => {
    if (!c || !/^local-[1-9]\d{0,8}$/.test(c.id) || ids.has(c.id) || !kinds.includes(c.kind) || typeof c.title !== 'string' || !c.title.trim() || c.title.length > 70 || !Array.isArray(c.messages) || !c.messages.length || c.messages.length > LIMITS.messages) throw new Error('Invalid demo chat');
    ids.add(c.id);
    const messages = c.messages.map(m => {
      if (m?.role === 'user' && typeof m.text === 'string' && m.text.trim() && m.text.length <= 4000) return { role: 'user', text: m.text };
      if (m?.role === 'assistant' && kinds.includes(m.kind) && m.topic === undefined) return { role: 'assistant', kind: m.kind };
      if (m?.role === 'assistant' && ['hint','check'].includes(m.kind) && kinds.includes(m.topic)) return { role: 'assistant', kind: m.kind, topic: m.topic };
      if (m?.role === 'notice' && m.key === 'stopped') return { role: 'notice', key: 'stopped' };
      throw new Error('Invalid demo message');
    });
    return { id: c.id, title: c.title, kind: c.kind, messages };
  });
  const p = data.profile;
  return { version: 1, profile: { name: p.name, country: p.country, ...(p.countryCode === undefined ? {} : { countryCode: p.countryCode }), grade: p.grade, language: p.language, avatar: p.avatar, subjects: [...p.subjects] }, chats: cleanChats };
}
const $ = selector => document.querySelector(selector);
// The Flask origin owns its transcript and persistence. Static demo state never
// becomes a fallback for a failed real connection.
const LIVE_SERVER = !!document.querySelector('meta[name="nmi-live-server"]');
const root = document.documentElement;
function readPreference(key, fallback, allowed) { try { const value = localStorage.getItem(key); return allowed.includes(value) ? value : fallback; } catch { return fallback; } }
function savePreference(key, value) { try { localStorage.setItem(key, value); } catch { storageIssue = 'storageUnavailable'; renderStorageStatus(); } }
let language = readPreference('nmi-preview-language', 'ar', ['ar', 'en']);
let theme = readPreference('nmi-preview-theme', 'light', ['light', 'dark']);
let currentId = null, view = 'new', nextId = 1, pending = null, statusKey = '';
const drafts = new Map();
const chats = LIVE_SERVER ? [] : ['math', 'code', 'writing'].map(kind => ({ id: `example-${kind}`, kind, titleKey: `${kind}Title`, messages: [{ role: 'user', key: `${kind}Prompt` }, { role: 'assistant', kind }] }));
let profile = null, storageIssue = '', loadedRaw = null, writesBlocked = false, showSample = false, onboardingError = '';
try { if (!LIVE_SERVER) {
  loadedRaw = localStorage.getItem(DEMO_KEY);
  const restored = parseDemo(loadedRaw);
  if (restored) { profile = restored.profile; language = readPreference('nmi-preview-language', profile.language, ['ar', 'en']); chats.unshift(...restored.chats); nextId = Math.max(0, ...restored.chats.map(c => Number(c.id.slice(6)))) + 1; }
} } catch { storageIssue = loadedRaw === null ? 'storageUnavailable' : 'storageInvalid'; writesBlocked = true; }
const question = $('#question');
const seenMessages = new WeakSet();
function renderStorageStatus() { $('#storage-status').hidden = !storageIssue; $('#storage-status').textContent = storageIssue ? t(storageIssue) : ''; }
function saveDemo() {
  if (LIVE_SERVER) return;
  if (!profile || writesBlocked) { renderStorageStatus(); return; }
  try {
    if (localStorage.getItem(DEMO_KEY) !== loadedRaw) { writesBlocked = true; storageIssue = 'storageConflict'; renderStorageStatus(); return; }
    const raw = JSON.stringify({ version: 1, profile, chats: chats.filter(c => !c.titleKey) });
    parseDemo(raw);
    localStorage.setItem(DEMO_KEY, raw); loadedRaw = raw; storageIssue = '';
  } catch { storageIssue = 'storageUnavailable'; }
  renderStorageStatus();
}
function t(key) { if (!(key in COPY[language])) throw new Error(`Missing translation: ${key}`); return COPY[language][key]; }
function node(tag, text, className) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el; }
function icon(name) { const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.classList.add('icon'); svg.setAttribute('aria-hidden', 'true'); const use = document.createElementNS(svg.namespaceURI, 'use'); use.setAttribute('href', `#i-${name}`); svg.append(use); return svg; }
function chatTitle(chat) { return chat.titleKey ? t(chat.titleKey) : chat.title; }
function activeChat() { return chats.find(chat => chat.id === currentId); }
function rememberDraft() { drafts.set(currentId || 'new', question.value); }
function setStatus(key = '', error = false) { statusKey = key; $('#form-status').textContent = key ? t(key) : ''; $('#form-status').classList.toggle('error', error); question.setAttribute('aria-invalid', String(error)); }
function setBusy(busy) { $('#send').hidden = busy; $('#stop').hidden = !busy; $('#question-form').setAttribute('aria-busy', String(busy)); }
function resizeComposer() { question.style.height = '59px'; question.style.height = `${Math.min(156, Math.max(59, question.scrollHeight))}px`; }
function renderHistory() {
  if (LIVE_SERVER) return;
  const list = $('#history-list'); list.replaceChildren();
  for (const chat of chats) { const link = node('a', chatTitle(chat), 'history-link'); link.href = `#chat/${chat.id}`; link.title = chatTitle(chat); link.dir = 'auto'; if (chat.id === currentId && view === 'chat') link.setAttribute('aria-current', 'page'); list.append(link); }
  $('#history-count').textContent = new Intl.NumberFormat(language).format(chats.length);
}
function renderLibrary() {
  const list = $('#library-list'); list.replaceChildren();
  if (LIVE_SERVER) return;
  for (const [kind, glyph] of [['math', 'math'], ['code', 'code'], ['writing', 'book']]) { const link = node('a', undefined, 'library-row'); link.href = `#chat/example-${kind}`; const start = node('div', undefined, 'row-start'); start.append(icon(glyph)); const text = node('div'); text.append(node('h2', t(`${kind}Title`)), node('p', t(`${kind}Description`))); start.append(text); const arrow = icon('chevron'); arrow.classList.add('directional'); link.append(start, arrow); list.append(link); }
}
function renderSearch() {
  if (LIVE_SERVER) { window.dispatchEvent(new Event('nmi-search')); return; }
  const query = $('#chat-search').value.trim().toLocaleLowerCase(language);
  const matching = chats.filter(chat => [chatTitle(chat), ...chat.messages.filter(m => m.role === 'user').map(m => m.key ? t(m.key) : m.text)].join(' ').toLocaleLowerCase(language).includes(query));
  const results = $('#search-results'); results.replaceChildren();
  for (const chat of matching) { const link = node('a'); link.href = `#chat/${chat.id}`; link.append(icon('chat'), node('span', chatTitle(chat))); link.addEventListener('click', () => { $('#search-dialog').close(); if (currentId === chat.id) $('#main').focus(); }); results.append(link); }
  $('#search-status').textContent = matching.length ? t('searchHelp') : t('noResults');
}
function renderAcademicScope() {
  for (const destination of ['progress', 'curriculum']) {
    const list = $('#' + destination + '-subjects'); list.replaceChildren();
    for (const subject of ACADEMIC_SUBJECTS) {
      const item = node('section', undefined, 'academic-summary'); item.dataset.academicSubject = subject;
      item.append(node('h2', t(subject + 'Subject')), node('p', t(destination === 'progress' ? 'noAcademicEvidence' : 'sourceUnavailable'))); list.append(item);
    }
  }
  const prompts = $('#academic-prompts'); prompts.replaceChildren();
  for (const subject of ACADEMIC_SUBJECTS) {
    const button = node('button', t(subject + 'Subject'), 'context-button'); button.type = 'button'; button.dataset.academicSubject = subject;
    button.addEventListener('click', () => {
      history.pushState(null, '', '#new'); navigate(); const prompt = t(subject + 'Prompt'); question.value = question.value ? question.value + '\n' + prompt : prompt; rememberDraft(); resizeComposer(); setStatus('draftPrompt'); question.focus();
    }); prompts.append(button);
  }
  for (const link of document.querySelectorAll('#library-list a')) {
    if (!link.hash.endsWith('example-math')) link.querySelector('.row-start > div').append(node('p', t('untrackedLibrary'), 'library-scope'));
  }
}
function formula() {
  const ns = 'http://www.w3.org/1998/Math/MathML';
  const m = (tag, text) => { const el = document.createElementNS(ns, tag); if (text) el.textContent = text; return el; };
  const math = m('math'); math.setAttribute('dir', 'ltr'); math.setAttribute('display', 'block'); math.setAttribute('aria-label', t('formulaSpoken'));
  for (const term of [[1,2], '+', [1,4], '=', [2,4], '+', [1,4], '=', [3,4]]) { if (Array.isArray(term)) { const f = m('mfrac'); f.append(m('mn', String(term[0])), m('mn', String(term[1]))); math.append(f); } else math.append(m('mo', term)); }
  const wrapper = node('div', undefined, 'formula-block'); wrapper.dir = 'ltr'; wrapper.append(math); return wrapper;
}
const CODE = 'def greet(name):\n    return f"Hello, {name}!"\n\nprint(greet("NMI"))';
function codeBlock() {
  const block = node('div', undefined, 'code-block'); const header = node('div', undefined, 'code-header'); const label = node('span', 'Python'); label.lang = 'en'; label.translate = false;
  const copy = node('button', undefined, 'copy-code'); copy.type = 'button'; copy.append(icon('copy'), node('span', t('copyCode')));
  copy.addEventListener('click', async () => { try { await navigator.clipboard.writeText(CODE); copy.replaceChildren(icon('check'), node('span', t('copied'))); } catch { setStatus('copyFailed'); } });
  header.append(label, copy); const pre = node('pre'); pre.dir = 'ltr'; const code = node('code', CODE); code.lang = 'en'; code.translate = false; pre.append(code); block.append(header, pre); return block;
}
function learningNote() {
  const details = node('details', undefined, 'learning-note'); details.append(node('summary', t('notes'))); const content = node('div'); const label = node('p', t('pathLabel')); const bar = node('progress'); bar.value = 1; bar.max = 3; bar.setAttribute('aria-label', t('pathLabel')); content.append(node('strong', t('demoPath')), label, bar, node('p', t('pathBody')), node('p', t('notAssessment'))); details.append(content); return details;
}
function assistantMessage(message) {
  const article = node('article', undefined, 'message assistant-message'); article.setAttribute('aria-label', t('assistant'));
  const heading = node('div', undefined, 'assistant-heading'); const mark = node('img'); mark.dataset.nmiMark = ''; mark.src = `assets/nmi-mark-${theme}.svg`;  mark.width = 25; mark.height = 25; mark.alt = ''; heading.append(mark, node('span', 'NMI'));
  const body = node('div', undefined, 'assistant-body'); const kind = message.kind; const topic = message.topic || kind;
  if (kind === 'hint' || kind === 'check') { body.append(node('h2', t(`${kind}Heading`)), node('p', t(`${topic}${kind === 'hint' ? 'Hint' : 'Check'}`))); if (kind === 'check') body.append(node('p', t('checkNote'), 'inline-note')); }
  else { body.append(node('h2', t(`${kind}Heading`)), node('p', t(`${kind}Intro`)));
    if (kind === 'math') { const list = node('ol'); for (const key of ['mathStep1', 'mathStep2', 'mathStep3']) list.append(node('li', t(key))); body.append(list, formula()); }
    if (kind === 'code') body.append(codeBlock(), node('p', t('codeAfter')));
    if (kind === 'writing') body.append(node('p', t('writingBefore'), 'inline-note'), node('p', t('writingAfter')));
    body.append(node('p', t(`${kind}Followup`)));
    if (kind === 'general') body.append(node('p', t('generalNote'), 'inline-note'));
    const tools = node('div', undefined, 'message-tools');
    for (const [action, glyph] of [['hint', 'light'], ['check', 'check']]) { const button = node('button', undefined, 'context-button'); button.type = 'button'; button.append(icon(glyph), node('span', t(action))); button.addEventListener('click', () => requestReply(action, kind)); tools.append(button); }
    body.append(tools);
    if (supportsAcademicSubject(kind)) body.append(learningNote());
    else body.append(node('p', t('conversationOnly'), 'conversation-only page-note'));
  }
  article.append(heading, body); return article;
}
function renderMessages() {
  if (LIVE_SERVER) return;
  const container = $('#messages'); container.replaceChildren();
  for (const message of activeChat()?.messages || []) {
    if (message.role === 'assistant') container.append(assistantMessage(message));
    else if (message.role === 'notice') container.append(node('p', t(message.key), 'notice-message'));
    else { const article = node('article', undefined, 'message student-message'); article.setAttribute('aria-label', t('you')); const bubble = node('div', message.key ? t(message.key) : message.text, 'student-bubble'); bubble.dir = 'auto'; article.append(bubble); container.append(article); }
    if (!seenMessages.has(message)) { container.lastElementChild.classList.add('is-new'); seenMessages.add(message); }
  }
}
function renderCopy() {
  root.lang = language; root.dir = language === 'ar' ? 'rtl' : 'ltr'; root.dataset.theme = theme; document.title = t('title');
  document.querySelectorAll('[data-nmi-mark]').forEach(mark => { mark.src = `assets/nmi-mark-${theme}.svg`; });
  $('#nmi-favicon').href = `assets/nmi-mark-${theme}.svg`;
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-label]').forEach(el => { el.setAttribute('aria-label', t(el.dataset.label)); });
  document.querySelectorAll('[data-placeholder]').forEach(el => { el.setAttribute('placeholder', t(el.dataset.placeholder)); });
  $('#language').value = language;
  $('#theme').setAttribute('aria-label', t(theme === 'light' ? 'dark' : 'light')); $('#theme').setAttribute('aria-pressed', String(theme === 'dark')); $('#theme use').setAttribute('href', theme === 'light' ? '#i-moon' : '#i-sun');
  $('#toggle-sidebar').setAttribute('aria-label', t($('#app-shell').classList.contains('collapsed') ? 'expand' : 'collapse'));
  $('#settings-language').value = language; $('#settings-theme').value = theme;
  $('#form-status').textContent = statusKey ? t(statusKey) : '';
  $('#view-title').textContent = view === 'chat' ? chatTitle(activeChat()) : t(['progress','curriculum','library','settings','profile'].includes(view) ? view : 'companion');
  $('#onboarding-language').value = language;
  for (const option of $('#onboarding-country').options) option.textContent = option.value ? countryByCode(option.value)[language] : t('chooseCountry');
  $('#onboarding-error').textContent = onboardingError ? t(onboardingError) : '';
  renderHistory(); renderLibrary(); renderMessages(); renderSearch(); renderProfile(); renderSample(); renderAcademicScope(); renderStorageStatus(); resizeComposer();
  if (LIVE_SERVER) window.dispatchEvent(new Event('nmi-render'));
}
function changeLanguage(value) { if (!['ar', 'en'].includes(value)) return; language = value; savePreference('nmi-preview-language', value); if (profile) { profile.language = value; saveDemo(); } renderCopy(); }
function changeTheme(value) { if (!['light', 'dark'].includes(value)) return; theme = value; savePreference('nmi-preview-theme', value); renderCopy(); }
function stopReply() { if (!pending) return; clearTimeout(pending.timer); const chat = chats.find(c => c.id === pending.id); chat?.messages.push({ role: 'notice', key: 'stopped' }); pending = null; setBusy(false); setStatus('stopped'); saveDemo(); renderMessages(); }
function navigate(focus = false) {
  if (location.hash === '#main') return;
  rememberDraft(); stopReply(); const route = location.hash.slice(1); const match = /^chat\/(example-(math|code|writing)|local-\d+)$/.exec(route);
  if (match && chats.some(c => c.id === match[1])) { view = 'chat'; currentId = match[1]; }
  else { view = ['progress', 'curriculum', 'library', 'settings', 'profile'].includes(route) ? route : 'new'; currentId = null; }
  for (const id of ['welcome', 'chat-view', 'progress', 'curriculum', 'library', 'settings', 'profile']) { $('#' + id).hidden = id !== (view === 'new' ? 'welcome' : view === 'chat' ? 'chat-view' : view); }
  $('#workspace').dataset.mode = view === 'new' ? 'welcome' : view === 'chat' ? 'chat' : 'utility';
  $('#composer-dock').hidden = !['new', 'chat'].includes(view); $('#suggestions').hidden = view !== 'new';
  document.querySelectorAll('.primary-nav a, .sidebar-bottom a').forEach(link => { if (link.hash === '#' + view) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current'); });
  if (!LIVE_SERVER) { question.value = drafts.get(currentId || 'new') || ''; setStatus(); }
  renderCopy(); $('#main').scrollTop = 0;
  if (focus) { if (view === 'new') question.focus(); else $('#main').focus(); }
}
function requestReply(kind, topic) {
  if (LIVE_SERVER) { window.dispatchEvent(new Event('nmi-demo-blocked')); return; }
  if (pending) return;
  const chat = editableChat(); if (!chat) return;
  if (chat.messages.length >= LIMITS.messages) { setStatus('demoLimit', true); return; }
  setBusy(true); setStatus('thinking');
  pending = { id: chat.id, timer: setTimeout(() => {
    chat.messages.push({ role: 'assistant', kind, topic }); pending = null; setBusy(false); setStatus('sent'); saveDemo();
    if (currentId === chat.id) { renderMessages(); $('#main').scrollTop = $('#main').scrollHeight; }
  }, 450) };
}
function chooseReply(message) {
  // Picks static presentation examples only; never classifies or grades an attempt.
  if (/physics|velocity|acceleration|فيزياء|قيزياء|تسارع|سرعة/i.test(message)) return 'physics';
  if (/chemistry|atom|molecule|كيمياء|ذرة|جزيء/i.test(message)) return 'chemistry';
  if (/python|code|function|\u0628\u0631\u0645\u062c|\u0628\u0627\u064a\u062b\u0648\u0646|\u0643\u0648\u062f|\u062f\u0627\u0644\u0629/i.test(message)) return 'code';
  if (/fraction|math|quarter|half|\u0643\u0633\u0631|\u0643\u0633\u0648\u0631|\u0627\u0644\u0646\u0635\u0641|\u0627\u0644\u0631\u0628\u0639|\u0631\u064a\u0627\u0636\u064a\u0627\u062a/i.test(message)) return 'math';
  if (/writ|sentence|grammar|\u0643\u062a\u0627\u0628\u0629|\u0643\u062a\u0627\u0628\u062a\u064a|\u062c\u0645\u0644\u0629|\u0627\u0644\u0643\u0644\u0645\u0627\u062a/i.test(message)) return 'writing';
  return 'general';
}
$('#question-form').addEventListener('submit', event => {
  event.preventDefault(); if (pending) return;
  const text = question.value.trim(); if (!text || text.length > 4000) { setStatus(text ? 'tooLong' : 'empty', true); question.focus(); return; }
  if ((!activeChat() && chats.filter(c => !c.titleKey).length >= LIMITS.chats) || activeChat()?.messages.length > LIMITS.messages - 2) { setStatus('demoLimit', true); return; }
  // On Flask, demo generation is forbidden even if the live adapter fails to load.
  if(LIVE_SERVER) {
    setStatus();
    $('#form-status').textContent=language==='ar'?'تعذّر تشغيل اتصال المعلّم. أعد تحميل الصفحة وافحص حالة الخادم. لن يظهر رد تجريبي بدلًا من الرد الحقيقي.':'The tutor connection did not start. Reload the page and check the server. No scripted reply will replace a real answer.';
    window.dispatchEvent(new Event('nmi-open-live'));
    return;
  }
  const kind = chooseReply(text);
  if (activeChat()?.titleKey && !editableChat()) return;
  if (!activeChat()) { const chat = { id: `local-${nextId++}`, title: text.slice(0, 70), kind, messages: [] }; chats.unshift(chat); currentId = chat.id; view = 'chat'; drafts.delete('new'); history.replaceState(null, '', `#chat/${chat.id}`); $('#welcome').hidden = true; $('#chat-view').hidden = false; $('#workspace').dataset.mode = 'chat'; $('#suggestions').hidden = true; }
  activeChat().messages.push({ role: 'user', text }); saveDemo(); question.value = ''; drafts.set(currentId, ''); resizeComposer(); renderCopy(); question.focus(); $('#main').scrollTop = $('#main').scrollHeight; requestReply(kind);
});
question.addEventListener('input', () => { rememberDraft(); resizeComposer(); if ($('#form-status').classList.contains('error')) setStatus(); });
question.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); $('#question-form').requestSubmit(); } });
$('#new-chat').addEventListener('click', () => { if (location.hash === '#new' || !location.hash) { navigate(); question.focus(); } else location.hash = 'new'; });
$('#stop').addEventListener('click', () => { stopReply(); question.focus(); });
$('#language').addEventListener('change', event => changeLanguage(event.target.value));
$('#theme').addEventListener('click', () => changeTheme(theme === 'light' ? 'dark' : 'light'));
$('#settings-language').addEventListener('change', event => changeLanguage(event.target.value));
$('#settings-theme').addEventListener('change', event => changeTheme(event.target.value));
$('#toggle-sidebar').addEventListener('click', () => { const collapsed = $('#app-shell').classList.toggle('collapsed'); $('#toggle-sidebar').setAttribute('aria-expanded', String(!collapsed)); $('#toggle-sidebar').setAttribute('aria-label', t(collapsed ? 'expand' : 'collapse')); });
$('#search-chats').addEventListener('click', () => { $('#chat-search').value = ''; renderSearch(); $('#search-dialog').showModal(); $('#chat-search').focus(); });
$('#close-search').addEventListener('click', () => $('#search-dialog').close());
$('#chat-search').addEventListener('input', renderSearch);
$('#suggestions').addEventListener('click', event => { const button = event.target.closest('[data-prompt]'); if (!button) return; const prompt = t(button.dataset.prompt + 'Prompt'); question.value = question.value ? question.value + '\n' + prompt : prompt; rememberDraft(); resizeComposer(); setStatus('draftPrompt'); question.focus(); });
window.addEventListener('hashchange', () => navigate(true));
function editableChat() {
  if (LIVE_SERVER) return null;
  const chat = activeChat();
  if (!chat?.titleKey) return chat;
  if (chats.filter(c => !c.titleKey).length >= LIMITS.chats) { setStatus('demoLimit', true); return null; }
  const copy = { id: `local-${nextId++}`, title: chatTitle(chat), kind: chat.kind, messages: chat.messages.map(m => m.key ? { role: 'user', text: t(m.key) } : { ...m }) };
  chats.unshift(copy); currentId = copy.id; drafts.set(currentId, question.value); history.replaceState(null, '', `#chat/${copy.id}`); renderHistory(); return copy;
}
function renderProfile() {
  if (LIVE_SERVER) return;
  $('#profile-name').textContent = profile?.name || t('demoProfile');
  $('#profile-avatar').toggleAttribute('hidden', !profile?.avatar);
  const meta = $('#profile-meta'); meta.replaceChildren();
  if (profile) { const country = node('bdi', countryByCode(countryCodeFor(profile))?.[language] || profile.country); meta.append(country, document.createTextNode(' · ' + t('grade' + profile.grade) + ' · ' + (language === 'ar' ? 'العربية' : 'English'))); }
  const choices = $('#subject-choices'); choices.replaceChildren();
  for (const subject of ACADEMIC_SUBJECTS) {
    const label = node('label', undefined, 'subject-choice'); const input = node('input'); input.type = 'checkbox'; input.name = 'subject'; input.value = subject; input.checked = profile?.subjects.includes(subject) || false;
    input.addEventListener('change', () => { if (!profile) return; profile.subjects = input.checked ? [...profile.subjects, subject] : profile.subjects.filter(s => s !== subject); saveDemo(); });
    label.append(input, node('span', t(subject + 'Subject'))); choices.append(label);
  }
  const retained = profile?.subjects.filter(subject => !supportsAcademicSubject(subject)) || [];
  $('#legacy-interests').hidden = retained.length === 0;
  $('#legacy-interests').textContent = retained.length ? t('retainedInterests') + ' ' + retained.map(subject => t(subject + 'Subject')).join(language === 'ar' ? '، ' : ', ') : '';
  const historyList = $('#profile-history'); historyList.replaceChildren();
  for (const chat of chats.slice(0, 4)) { const link = node('a', chatTitle(chat), 'history-link'); link.href = `#chat/${chat.id}`; link.dir = 'auto'; historyList.append(link); }
  $('#continue-learning').href = chats.some(c => !c.titleKey) ? `#chat/${chats.find(c => !c.titleKey).id}` : '#new';
}
function renderSample() {
  if (LIVE_SERVER) return;
  $('#sample-toggle').textContent = t(showSample ? 'hideSample' : 'sampleProgress'); $('#sample-toggle').setAttribute('aria-expanded', String(showSample));
  const sample = $('#sample-progress'); sample.hidden = !showSample; sample.replaceChildren();
  if (!showSample) return;
  sample.append(node('h2', t('sampleLabel')), node('p', t('sampleNote'), 'page-note'));
  for (const [subject, skill, value] of [['math','fractionsSkill',60], ['math','equationsSkill',35], ['physics','unitsSkill',45], ['chemistry','atomsSkill',40]]) {
    if (!academicPolicy(subject).masteryEligible) continue;
    const row = node('div', undefined, 'skill-row'); row.dataset.academicSubject = subject; const description = node('div'); description.append(node('span', t(subject + 'Subject'), 'page-note'), node('h3', t(skill)));
    const bar = node('progress'); bar.max = 100; bar.value = value; bar.setAttribute('aria-label', t(skill)); const number = node('span', new Intl.NumberFormat(language, { style: 'percent' }).format(value / 100)); row.append(description, bar, number); sample.append(row);
  }
  const notes = node('div', undefined, 'insight-grid'); for (const [title, body] of [['strengths','sampleStrength'],['weaknesses','sampleWeakness']]) { const section = node('section'); section.append(node('h3', t(title)), node('p', t(body))); notes.append(section); } sample.append(notes);
  const recovery = node('section', undefined, 'recovery-path'); recovery.append(node('h3', t('foundationTitle')), node('p', t('foundationBody'))); const steps = node('ol'); for (let i = 1; i <= 4; i++) steps.append(node('li', t('recoveryStep' + i))); recovery.append(steps, node('p', t('recoveryNote'), 'page-note')); sample.append(recovery);
}
function openOnboarding() {
  if (LIVE_SERVER) { window.dispatchEvent(new Event('nmi-open-connection')); return; }
  $('#onboarding-name').value = profile?.name || ''; $('#onboarding-country').value = countryCodeFor(profile); $('#onboarding-grade').value = profile?.grade || ''; $('#onboarding-avatar').checked = profile?.avatar ?? true;
  $('#legacy-country-note').hidden = !profile || !!countryCodeFor(profile);
  onboardingError = ''; $('#onboarding-error').textContent = ''; $('#cancel-onboarding').hidden = !profile;
  $('#onboarding-form button[type="submit"]').dataset.i18n = profile ? 'saveProfile' : 'startLearning'; renderCopy(); $('#onboarding').showModal(); $('#onboarding-language').focus();
}
for (const grade of ['', ...SUPPORTED_GRADES]) { const option = node('option'); option.value = grade; option.dataset.i18n = grade ? 'grade' + grade : 'chooseGrade'; option.disabled = !grade; $('#onboarding-grade').append(option); }
$('#onboarding-grade').value = '';
for (const code of ['', ...COUNTRIES.map(country => country.code)]) { const option = node('option'); option.value = code; option.disabled = !code; $('#onboarding-country').append(option); }
$('#onboarding-country').value = '';
const toggle = node('button', undefined, 'context-button'); toggle.id = 'sample-toggle'; toggle.type = 'button'; toggle.setAttribute('aria-controls', 'sample-progress');
toggle.addEventListener('click', () => { showSample = !showSample; renderSample(); });
const sample = node('section', undefined, 'sample-progress'); sample.id = 'sample-progress'; sample.hidden = true; $('#progress').append(toggle, sample);
const resetRow = node('div', undefined, 'setting-row'); const resetText = node('p'); resetText.dataset.i18n = 'resetHelp'; const resetButton = node('button', undefined, 'context-button'); resetButton.id = 'reset-demo'; resetButton.type = 'button'; resetButton.dataset.i18n = 'clearDemo'; resetRow.append(resetText, resetButton); $('#settings .settings-list').append(resetRow);
resetButton.addEventListener('click', () => { if (!window.confirm(t('clearConfirm'))) return; try { for (const key of [DEMO_KEY, 'nmi-preview-language', 'nmi-preview-theme']) localStorage.removeItem(key); location.href = location.pathname; } catch { storageIssue = 'storageUnavailable'; renderStorageStatus(); } });
$('#edit-profile').addEventListener('click', openOnboarding);
$('#cancel-onboarding').addEventListener('click', () => $('#onboarding').close());
$('#onboarding').addEventListener('cancel', event => { if (!profile) event.preventDefault(); });
$('#onboarding-language').addEventListener('change', event => changeLanguage(event.target.value));
$('#onboarding-form').addEventListener('submit', event => {
  event.preventDefault();
  const name = $('#onboarding-name').value.trim(), countryCode = $('#onboarding-country').value, grade = Number($('#onboarding-grade').value);
  for (const field of ['name','country','grade']) $('#onboarding-' + field).removeAttribute('aria-invalid');
  const error = !name || name.length > 40 ? ['name','invalidName'] : !countryByCode(countryCode) ? ['country','invalidCountry'] : !SUPPORTED_GRADES.includes(grade) ? ['grade','invalidGrade'] : null;
  if (error) { onboardingError = error[1]; $('#onboarding-error').textContent = t(onboardingError); $('#onboarding-' + error[0]).setAttribute('aria-invalid', 'true'); $('#onboarding-' + error[0]).focus(); return; }
  onboardingError = '';
  profile = { name, country: countryByCode(countryCode).en, countryCode, grade, language, avatar: $('#onboarding-avatar').checked, subjects: profile?.subjects || [] }; saveDemo(); $('#onboarding').close(); renderCopy(); if (view === 'new') question.focus();
});
window.addEventListener('storage', event => { if (!LIVE_SERVER && (event.key === DEMO_KEY || event.key === null)) { writesBlocked = true; storageIssue = 'storageConflict'; renderStorageStatus(); } });
window.addEventListener('beforeunload', event => { if ([...drafts.values()].some(value => value.trim())) { event.preventDefault(); event.returnValue = ''; } });
navigate();
if (!profile && !LIVE_SERVER) openOnboarding();
