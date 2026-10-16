---
name: nmi-frontend-quality
description: Run NMI desktop frontend acceptance tests for navigation, forms, Arabic and English, themes, keyboard access, console errors, and visual consistency.
---

Own test coverage and acceptance, not design choices. Use playwright-cli for browser mechanics and web-design-guidelines for static UI review.

- From NMI run `node tools/run_frontend_tests.cjs`; this uses the pinned local Playwright package, a fresh browser profile and localhost-only requests. Do not attach to personal browser sessions or save authentication state.
- Test the matrix in DESIGN.md. Check visible labels, keyboard focus and skip link, form validation, language/theme persistence, draft preservation, reduced motion, no clipping and no console errors.
- Assert user-observable behavior with role/label locators. A screenshot existing is not a visual pass: inspect it. Automated accessibility checks supplement manual screen-reader and zoom checks.
- Mock backend calls for future integration. Use fabricated learners; never collect student screenshots or real conversations.
- Do not weaken assertions to make failures pass. Fix only authorized frontend changes; report unrelated backend defects.
- Keep artifacts under NMI/.cache. No global installation, external uploads, paid testing or mobile work. Invoke the existing local CLI as `node node_modules/playwright/cli.js`; avoid npx that can download implicitly.

