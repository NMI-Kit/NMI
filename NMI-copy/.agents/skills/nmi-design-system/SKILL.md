---
name: nmi-design-system
description: Maintain NMI branding, design tokens, light and dark themes, and reusable desktop UI components when building or reviewing NMI visual interfaces.
---

Read [DESIGN.md](../../../DESIGN.md) and [AGENTS.md](../../../AGENTS.md). The design document owns visual decisions; frontend-design helps composition but cannot introduce an independent palette.

- Reuse preview/tokens.css and the original SVG mark. Extend semantic roles deliberately in both themes. Keep styles shared rather than duplicating each page.
- Inspect component default, hover, focus, selected, disabled, loading, empty and error states. Use real HTML controls with readable text and sufficient contrast.
- Desktop V1 is 1280px and wider. Do not add mobile navigation, React, Tailwind or an unrelated framework to fit a downloaded component.
- Evaluate 21st references for licensing, dependencies, accessibility and direction before translating a simple pattern to vanilla code. No authenticated publishing/generation is authorized.
- Send locale/direction issues to nmi-bilingual-ui and browser acceptance to nmi-frontend-quality. Motion owns animation implementation guidance.
- Deliver changed token/component names, screenshots in both themes, and any visual tradeoffs. Distinguish synthetic preview data from actual student results.

