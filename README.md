# NMI — Next Mastery Intelligence

**A free toolkit that turns ChatGPT, Claude or Gemini into a math tutor that knows the Israeli high-school curriculum and the shape of its exams.**

🔗 **Try it:** https://m0502223641-coder.github.io/NMI/ (works best on a phone)

---

## Why I built it

I built NMI because I had gaps in math. I needed to review grade 9 material on my own, really understand the topics I had skipped over, and reach a high level so I could move up to 5-unit math.

I used ChatGPT to study, but without the right instructions it scattered me. It did not know the Israeli curriculum, and it did not know the patterns of our exam questions:
- which topics are in **my** grade and level, and which are not;
- what our exam questions look like (a story, sections that build on each other, a "justify" section);
- that it should let me try first instead of solving for me.

So I decided to build NMI.

Building it was an amazing journey, and I was excited the whole time. But when I finished, I asked myself one question: **"Is a student ready to leave ChatGPT, Claude or Gemini and move to my website?"** The answer was no.

So I asked a better question: **why not bring NMI inside the AI tools students already use?**

## The solution

NMI brings the curriculum **into** the app the student already uses.

1. The student picks a subject, grade, level (3, 4 or 5 units) and an optional target level (for example 3 → 5).
2. The student ticks the topics to review, or adds a topic of their own.
3. The student picks a mode: **Understand**, **Practice**, **Mock exam** or **Plan**. Optional: "I have an old exam from my teacher" and a short note to the tutor.
4. NMI builds one prompt and opens the student's AI app with it (Android share sheet, or copy and paste).

The prompt contains only what that student needs: their topics from the official curriculum, the exam patterns for their level, one example question per topic, and the teaching rules (one question at a time, hints before answers, read photos of handwritten work).

Nothing is uploaded to NMI and nothing is stored about the student. There is no server and no cost.

## What is inside

| Part | What | How it was checked |
|---|---|---|
| Curriculum | 9 levels: grades 10, 11, 12 × 3, 4, 5 units, in Arabic | Topic lists compared line by line with the Ministry of Education teaching recommendations for 2026–2027 (תשפ"ז) and the new curriculum document |
| Exam patterns | 7 exam forms (35172, 35371, 35372, 35471, 35472, 35571, 35572): structure, typical sections, common traps | Built from official Ministry exams; no exam question is copied |
| Example bank | 101 exam-style questions, one per topic, with new stories and numbers | Every number checked with SymPy; stories checked for sense (no negative prices or lengths) |
| Teaching rules | Explain / practice / mock exam / plan, a hint ladder, photo reading | Tested first in a lab version (below) |

## How it was built

- **Lab version (first):** a local web app that called the Claude API directly, with 60+ evaluation cases scored by an AI judge and by code checks. It taught me which teaching rules work. It also taught me that students would not leave ChatGPT for it, so the product became the toolkit.
- **Toolkit (now):** a static page (`kit/`) built from the curriculum files by `tools/build_kit.py`. Adding a subject means adding curriculum files, not code.
- **Tests:** 183 offline tests, 77 local tests, 33 prompt tests, 64 browser tests on iPhone, Android and desktop sizes.
- **Tools:** I designed the product, made the decisions and tested it with real study sessions. I wrote the code with AI coding assistants (Claude Code), and checked the content against official sources.

## Honest limits

- The curriculum and exam patterns follow official documents, but **no math teacher has reviewed** the example bank yet.
- Common mistakes listed per topic come from general teaching experience, not from the Ministry.
- Some 4- and 3-unit patterns (35372, 35471) were built from the matching graduates' exams.
- Opening the installed app directly works on Android; on iPhone the student pastes the prompt.

## Next

- Physics and English (curriculum files only, same code).
- A grade 9 level for students who miss the basics.
- A review of the example bank by a math teacher.

## Repository map

```
kit/                 the toolkit page (index.html, app.js, prompt.js, data.json)
curriculum/math/     curriculum files, exam patterns, example bank
tools/build_kit.py   builds kit/data.json from curriculum/
tests/               offline, local, prompt and browser tests
docs/KIT.md          publishing and manual phone checks
(other files)        the lab version
```

---

## بالعربي باختصار

**NMI عدّة مجانية** بتخلّي ChatGPT أو Claude أو Gemini يصير مدرّس رياضيات بيعرف منهاجك الإسرائيلي بالضبط، وبيعطيك أسئلة بنمط امتحاناتنا، وبيخلّيك تحاول قبل ما يحل عنك. بتختار صفك ووحداتك ومواضيعك، والعدّة بتجهّز البرومبت وبتفتح التطبيق اللي عندك.
