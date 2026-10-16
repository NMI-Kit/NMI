---
name: nmi-bilingual-ui
description: Implement or review NMI Arabic RTL and English LTR interfaces, translations, mixed-direction learning content, and language switching.
---

Read NMI/DESIGN.md. Own locale behavior; delegate palette and component aesthetics to nmi-design-system.

1. Inventory visible strings and accessible names, including errors, empty/loading states, title, tooltips and controls. Keep exactly ar/en dictionaries with matching keys.
2. Switch lang and dir atomically. Use CSS logical properties. Preserve input drafts; language/theme preferences must not act as student identity.
3. Wrap equations, code, units and Latin identifiers in LTR islands; isolate arbitrary names with bdi. Do not reverse equations, logos or all icons indiscriminately.
4. Check Arabic glyph joining, punctuation and line-height. Never split Arabic into per-letter animation spans. Do not silently rewrite a student's original answer.
5. Test Arabic/English in both themes at desktop widths, long phrases, keyboard use, blocked localStorage, and switching while a draft exists. No mobile layout is required.

For tutoring semantics rather than UI text, use nmi-tutor-testing. Report untranslated keys, direction defects and evidence from the browser.

