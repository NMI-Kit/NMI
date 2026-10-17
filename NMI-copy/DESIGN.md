# NMI design system

Product authority: [NMI_PRODUCT_SPEC.md](NMI_PRODUCT_SPEC.md). Status: locally verified desktop design preview with mock replies, ready for design review. Current results are in [docs/FRONTEND_REFINEMENTS.md](docs/FRONTEND_REFINEMENTS.md). No real tutor or student-data integration.

Local integration update, 13 October: [docs/LOCAL_AI.md](docs/LOCAL_AI.md) describes the new opt-in Flask AI pane. It reuses these tokens, logos, sidebar, languages and themes. The static demo is unchanged. The local pane has its own profile, history and attempt counts; demo pages do not masquerade as live progress. Replies are rendered as safe plain text for this first integration, with no executable HTML or model-supplied tools. Paid calls have not been made.

## Direction: a calm AI conversation workspace

**15 October phase-1 update:** Flask uses the main NMI composer and transcript. Connection/profile setup lives in Settings; there is no separate live chat pane. Static demo storage is not loaded on Flask. Existing tokens, themes and asset files are preserved. The latest master brief in docs/MASTER_BRIEF_STATUS.md supersedes the old sparkle and country requirements below; later design changes are pending the first real AI milestone. See docs/PHASE1_VERIFICATION.md for current evidence.

The conversation is the center. A quiet sidebar supports history and secondary learning tools; the welcome screen offers one clear question and a generous composer. No predefined lesson, subject dashboard, decorative hero or compulsory course choice stands between onboarding and chat.

Use the approved ribbon N and four-point sparkle, deep teal actions, open whitespace and comfortable prose. The memorable element is the focused composer and centered icon-only NMI identity. Student text has a soft bubble; assistant content sits in open space with a small NMI mark. Steps, math, code and contextual hints share one reading rhythm. Progress stays off the default conversation surface.

Layout:

    Sidebar 248px | Minimal topbar: NMI, locale, appearance
    New / Search | Welcome or scrolling conversation
    Learning     | Reading measure 760px
    History      | Contextual hints and checks
    Settings     | Bottom composer and honest demo notice

In Arabic the sidebar and inline alignment follow RTL. Math, code and the logo do not mirror. At 1280px the sidebar contracts to 228px and reading measure to 720px. V1 targets 1280px and wider; no mobile navigation. Browser zoom and overflow remain available below the supported layout width.

## Authority and shared assets

- preview/tokens.css owns all semantic color, spacing, typography, radius and motion tokens. Reuse these in future Flask static assets; do not create competing themes.
- preview/styles.css owns components, preview/index.html semantic structure, preview/preview.js translated copy, mock interactions and bounded demo storage.
- preview/assets/nmi-mark-light.svg and nmi-mark-dark.svg adapt the user-supplied concept #6 identity board as transparent, icon-only vectors. nmi-mark-white.svg and nmi-mark-black.svg are monochrome variants; nmi-mark.svg aliases the light color geometry. The board and provenance are in docs/references and docs/BRAND_ASSETS.md. Inline symbols share one outline icon system. The optional profile portrait is original SVG, not a match to an unsupplied avatar reference.
- Onboarding, profile, progress, library, settings and chat use these same controls and tokens.

## Palette and typography

| Role | Light | Dark |
|---|---|---|
| Canvas | #fcfdfd | #172126 |
| Sidebar | #f2f6f5 | #111c20 |
| Surface | #ffffff | #1e2c31 |
| Quiet surface | #edf2f1 | #26363a |
| Primary text | #1e3337 | #ecf3f1 |
| Secondary text | #627376 | #a7b9b7 |
| Action | #086b63 | #8edac6 |
| On action | #ffffff | #15342c |
| Border | #d7e1df | #34484b |
| Control border | #94aaa5 | #77908e |
| Focus | #0759bf | #99c5ff |
| Error | #a82132 | #ffabb6 |

System typography: Segoe UI with system fallbacks for English; Segoe UI/Tahoma for Arabic. No external font requests. Headings 31-34px, assistant prose 15px English/16px Arabic with 1.8/2 line height, short secondary labels 12-14px. Keep lines below about 80 characters. Spacing uses the 4px base with 8/12/16/24/32/48/64px roles. Controls use 8-10px radii, composer 22px, specimen panels 16px. Shadows are restrained and limited to composer/dialog elevation.

## Onboarding and profile

Updated 13 October: use a labeled Languages dropdown and exactly ten country options with translated labels (US, GB, CA, DE, CH, SG, AU, NL, QA, AE). New demo profiles save a countryCode and canonical name; legacy free-text values remain intact until the user explicitly updates them. Profile academic selections and progress/curriculum summaries use only Mathematics, Physics and Chemistry. Earlier coding/writing/science interests remain visible as conversation-only interests, without being mapped to supported academic subjects.

Keep chat and the existing general Library examples open to any topic. Code/writing/general responses retain hints and comprehension prompts, but do not display academic learning-path bars. Physics and Chemistry have additional fixed mock examples. All curriculum summaries truthfully state that a verified curriculum has not been loaded. Fictional academic progress examples use only the three supported subjects and remain labeled.

The user supplied the approved identity board on 13 October 2026 in response to the concept #6 reference request. Preserve its flowing ribbon N, cyan-to-blue/lavender fold and four-point sparkle. The local SVGs are vector adaptations, not original source artwork or pixel-exact exports. Theme changes select the corresponding color asset; never mirror the logo in RTL. Gradients belong to the approved mark, not decorative page backgrounds. Logo assets contain no wordmark; contextual NMI text elsewhere identifies the product.

A single compact form requests language, demo nickname, country and a grade from the central [9,10,11,12] list. Explain synthetic data and browser persistence before saving. Do not ask for credentials. Restored valid onboarding skips the form. An illustrated portrait is optional and can be disabled. Inputs have explicit labels, validation and focus on the first invalid field.

The profile presents identity and subject interests first, then truthful evidence-free strength/weakness states and demo history. Progress starts empty. A separate opt-in fictional specimen shows subject/skill bars, strengths, foundation support and return to the original task. Its fixed values are explicitly not the student's progress. Earlier foundation support never changes enrollment grade.

## Language and content

Exactly ar/en dictionaries with identical keys. Change html.lang and html.dir together; preserve drafts and literal learner wording. Use logical CSS and bdi for names/countries. All chrome, labels, validation, storage failures and empty states are translated. Language names may appear in their own language to make switching identifiable. Programming syntax and brand names retain their original form.

Native MathML provides the fraction example, with a localized spoken label. Code is LTR with a copy control. Literal user input is textContent, never HTML. Demo replies are deterministic display samples, not intent classification or adaptive assessment.

## Persistence and privacy

Versioned demo state uses nmi-preview-demo-v1; preferences use nmi-preview-language and nmi-preview-theme. Validate profile enums, types, sizes, chat IDs and message kinds before rendering. Allowlist reconstructed fields. Cap 30 saved chats, 80 messages per chat and a 1,000,000-character serialized document. Invalid state is preserved until explicit reset. Guard stale writes from another tab. Storage failure is visible and the current tab remains usable. Only synthetic data belongs here; this is not secure multi-student storage.

No password, authentication token, external analytics, cloud sync or student-file access. The loopback preview server serves only allowlisted static assets. See the product specification for the future server-side session/isolation gate.

## Motion and accessibility

Only short opacity/transform feedback, 140-220ms. No continuous motion, typing simulation, parallax, moving scores or split Arabic letters. prefers-reduced-motion disables movement. Motion's guidance supports CSS for these simple effects; no Motion runtime/MCP or paid audit is installed or used.

Only newly displayed conversation objects receive the message-arrival transform; preference rerenders do not replay it. Native dialogs and utility-page entry use short transform-only feedback, preserving text contrast. The welcome mark has a single short entrance. No perpetual breathing, sparkle or loading ring is added merely because the reference board depicts animation ideas. Reduced-motion disables animations, transitions and active-button movement. Use browser checks for active animation names/durations, preference changes and reduced-motion behavior.

Use native controls/dialogs, visible focus, a skip link, polite status regions, explicit labels and current-navigation state. Error states never rely on color alone. Keep the composer outside the scrolling message pane. Preserve browser zoom. Automated axe checks supplement keyboard/zoom and visual review; they do not establish complete WCAG conformance.

## Research applied

- [ChatGPT](https://chatgpt.com/): new/search/history hierarchy and direct conversation entry, without copied branding or assets.
- [21st](https://21st.dev/): evaluated AI-chat/navigation/component patterns; React/Tailwind components were not imported into vanilla JS.
- [Supahero](https://supahero.io/): first-screen hierarchy and restrained framing; no marketing hero copied into the workspace.
- [Refero Styles](https://styles.refero.design/): explicit documentation of palette/type/spacing roles in DESIGN.md; no third-party theme copied wholesale.
- [Motion](https://motion.dev/): purposeful short feedback and reduced-motion handling with CSS.

## Verification

Arabic/English x light/dark at 1280x800, 1440x900 and 1920x1080. Exercise onboarding, profile, every route, search, long text, safe rendering, send/stop, drafts, code/math, keyboard, reduced motion, storage faults and a real browser-process restart. Inspect screenshots in both languages/themes. Record actual results and limitations in docs/PREVIEW_VERIFICATION.md. Historical lesson-preview results do not certify this redesign.
