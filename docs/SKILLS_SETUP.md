# NMI Skills setup report

Historical setup report. The current chat-first product contract is ../NMI_PRODUCT_SPEC.md; current redesign evidence is PREVIEW_VERIFICATION.md. The lesson preview and original test counts below are superseded, while installed Skill provenance remains applicable.

Prepared 2026-10-12. Scope: local Skills, design foundation, synthetic desktop preview and offline testing support. Backend checkpoint verified before edits: `b26a71481f4bc52822818be05d7c0d3c19767e7f` (Save NMI backend fixes before website design).

## Installed official-source Skills

All are under `NMI/.agents/skills/<name>/SKILL.md`. Only reviewed text/reference files were copied from pinned official repositories. The bundled Codex Skill Installer was inspected and used with project-local staging and temporary paths; its GitHub credential variables were blanked in the installer child process. No downloaded executable installer was run.

| Skill | Owner/source | Revision | Purpose |
|---|---|---|---|
| frontend-design | [Anthropic](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design) | dbd4588f9e1033efb41dad4bef2f7947c8993d44 | Composition and visual direction |
| web-design-guidelines | [Vercel Labs](https://github.com/vercel-labs/agent-skills/tree/063bee94c3f4df8453406c830b0a7df0f2860278/skills/web-design-guidelines) | 063bee94c3f4df8453406c830b0a7df0f2860278 | Static interface and accessibility review |
| playwright-cli | [Microsoft](https://github.com/microsoft/playwright-cli/tree/b85c7a736bb473bf55b584e54a09ffa698d6d871/skills/playwright-cli) | b85c7a736bb473bf55b584e54a09ffa698d6d871 | Browser tooling and testing mechanics |
| motion | [Motion](https://github.com/motiondivision/ai-kit/tree/d1c5c26f424adfd47c112d894e9d424b57338c7e/plugins/motion/skills/motion) | d1c5c26f424adfd47c112d894e9d424b57338c7e | Offline animation guidance, including vanilla JS/CSS |

Local adaptations: every official entrypoint has an NMI scope note excluding global installation, personal browser attachment, credential access, external uploads, publishing, paid operations, mobile work and stack changes. Motion's top-level `argument-hint` was moved under `metadata` for compatibility with the bundled Codex validator. References remain available but their examples do not grant permission to execute out-of-scope commands. Exact original and installed file hashes are in `docs/skill-sources.json`.

Licensing: Anthropic's bundled Apache-2.0 LICENSE.txt is retained; Microsoft's Apache-2.0 repository LICENSE is included. Vercel's pinned README declares MIT although GitHub reports no detected license file. Motion's official installation documentation declares the skill MIT although GitHub likewise reports no detected license file. These are local development instructions, not website assets or a published redistribution. Recheck license notices before any redistribution.

The Motion skill is installed; the Motion JavaScript runtime, AI Kit installer and both remote MCP connections are NOT installed/configured. Its self-contained best-practices are usable offline. Current website and repository wording differ about some gated AI tools; none are enabled here, so there is no paid-feature dependency.

## Eight custom Skills

| Skill | Owns | Does not duplicate |
|---|---|---|
| nmi-design-system | Tokens, light/dark themes, branding, logo and reusable components | General visual brainstorming or locale behavior |
| nmi-bilingual-ui | Arabic/English copy, direction, mixed math, switching | Palette and component style decisions |
| nmi-frontend-quality | Desktop browser acceptance matrix | Playwright command reference or static design rules |
| nmi-tutor-testing | Intent, hints, misconceptions, Arabic typo cases and adaptation rubric | Storage-failure mechanics |
| nmi-backend-quality | Python contracts and future Flask/repository integration | Detailed security policy or fault tests |
| nmi-security-privacy | Credentials, ownership, authorization, safe inputs/logs and deployment review | Integration implementation and reliability fault execution |
| nmi-curriculum-quality | Country/grade/subject provenance, identifiers and prerequisite integrity | Assessment semantics and UI content translation |
| nmi-reliability-testing | Data faults, mocked API failures, retries and history/progress consistency | Teaching-quality rubric or security-policy ownership |

Security has a focused acceptance reference. Tutor testing links to 14 synthetic evaluation cases and a scoring guide. AGENTS.md routes work between these Skills so no two are competing authorities for the same decision.

## Compatibility and skipped integrations

- Python 3.14 and existing openai/pydantic requirements remain unchanged. No Flask/React/Tailwind package was added. The existing CLI and learning rules are untouched.
- Node 24.19.0 was already installed. Added local dev-only @playwright/test 1.64.0 and @axe-core/playwright 4.13.0, including their locked transitive packages. npm lifecycle scripts were disabled. npm used empty project-local configuration files, public registry and local cache. No npm audit submission or global upgrade was run.
- PyYAML 6.0.3 is isolated under ignored `.cache/python-tools` for the official skill validator; it is not in application requirements or installed into the application venv.
- Existing Microsoft Edge is used with a fresh temporary profile and Chromium sandbox enabled. No browser download or personal profile attachment was needed.
- [Refero's skill](https://github.com/referodesign/refero_skill) was reviewed but not installed: its broad primary-design authority overlaps this setup. Its live MCP research requires paid Pro access. [Refero Styles](https://styles.refero.design/) remains a manual reference.
- [21st's Codex plugin](https://github.com/21st-dev/codex-plugin) was reviewed but not installed: authentication and publishing/generation workflows are unnecessary for this setup, and its component code targets React/Tailwind. Free limited browsing does not make component code directly compatible with vanilla HTML.
- [Supahero](https://supahero.io/) remains an inspiration source; no official installable Skill was found in the reviewed resources.
- [Motion AI Kit](https://motion.dev/docs/ai-kit-install) installer and paid features were skipped. Only the verified instruction folder was installed. No MCP server or credential configuration was changed.

## Added design and preview files

- `AGENTS.md`: project boundaries, architecture facts, Skill routing and commands.
- `DESIGN.md`: original NMI visual direction, semantic palette, spacing/type/component rules and desktop acceptance.
- `NMI.code-workspace`: opens NMI as the workspace folder without touching parent workspace settings.
- `preview/index.html`, `tokens.css`, `styles.css`, `preview.js`, `assets/nmi-mark.svg`: desktop learning studio with original geometric logo, Arabic/English, light/dark, three navigable views, labeled form, mock replies, hint, reduced motion and keyboard support.
- The preview starts in Arabic/light unless a valid local preference exists. Only language/theme preferences persist. Conversations remain in memory and disappear on reload. No AI calls, student JSON reads/writes or official curriculum claims occur.
- `tools/serve_preview.py`: allowlisted static assets on 127.0.0.1:8765 only; backend/secret paths are denied. This is a local development server, not a deployment server.
- `package.json`, `package-lock.json`, `playwright.config.cjs`, `tools/run_frontend_tests.cjs`, `tests/frontend/preview.spec.cjs`: local browser tooling and acceptance tests.
- `tests/offline/test_backend_contracts.py`: mocked OpenAI installed before importing ai_test, network denial, per-test temporary persistence paths under NMI/.cache.
- `tests/evals/README.md`, `tests/evals/tutor_cases.json`: semantic evaluation specifications, not claims of measured real-model behavior.
- `tools/validate_setup.py`: official metadata validator, reference checks, eval-case integrity and unchanged-backend hash checks. It relaunches itself in UTF-8 mode to accommodate Arabic on Windows.
- `.gitignore`: excludes only new local tooling caches, node_modules and test artifacts. The root ignore file remains unchanged.

## Verification

Final test counts and observations are recorded in `docs/TEST_RESULTS.md`.

From the NMI directory:

```powershell
.\.venv\Scripts\python.exe -B tools/validate_setup.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/offline -v
node tools/run_frontend_tests.cjs
.\.venv\Scripts\python.exe -B tools/serve_preview.py
```

Open http://127.0.0.1:8765 while the preview server runs; stop with Ctrl+C. The browser test runner starts and stops its own server. Close a manually running server before the test suite, which intentionally refuses to reuse an unknown server.

Screenshots and machine-readable browser results are in `.cache/screenshots` and `.cache/frontend-results.json`. All use fictional content. Cache files and packages are not staged or committed.

The source pins and package lock support reproducibility. If tooling caches are removed in a future cleanup, reinstall only in NMI with reviewed pinned packages, lifecycle scripts disabled, local npm cache/configuration and no credentials. PyYAML can be restored with the existing venv's `python -B -m pip --isolated install --no-cache-dir --only-binary=:all: --target .cache/python-tools PyYAML==6.0.3` after authorizing the public download. Do not copy or upgrade application requirements for tool validation.

## Codex discovery and use

[Official discovery documentation](https://learn.chatgpt.com/docs/build-skills) states that Codex searches .agents/skills from its working directory upward to the repository root, not downward into child projects. Open NMI.code-workspace or start Codex with NMI as its working directory. All 12 directories have unique valid names and frontmatter descriptions; automatic selection remains enabled by default.

Installed Skills are available on the next turn. Use `/skills` or `$skill-name` in the CLI/IDE; restart/reopen NMI if the list is stale. A session still rooted at `studdy app` will not automatically discover the child Skills. No root/global files were changed to work around this boundary. Structural discovery and official schema validation passed; interactive selector appearance/automatic selection in a newly rooted session has not been observed. No extra model session was launched to simulate it.

Example future prompts:

- `$nmi-design-system Build the desktop tutor screen using DESIGN.md; preserve the Python core.`
- `$nmi-bilingual-ui Review the preview's Arabic/English direction and translations.`
- `$nmi-frontend-quality Run the local desktop preview acceptance tests.`
- `$nmi-tutor-testing Review the offline cases; distinguish semantic evidence from mocked plumbing.`
- `$nmi-security-privacy Review the planned student-record authorization boundary without reading credentials.`

For website building: frontend-design + nmi-design-system establish composition/tokens; nmi-bilingual-ui covers language; motion covers animation; web-design-guidelines and nmi-frontend-quality/playwright-cli validate. For backend work: nmi-backend-quality coordinates the three specialized security/curriculum/reliability skills and nmi-tutor-testing.

## Remaining implementation work

Skills guide engineering; they do not implement missing capabilities. Current backend uses global single-student JSON storage; Flask/authentication, isolated student repositories, transactional persistence and request-ID deduplication remain absent. Curriculum content and official provenance are not loaded. Actual Arabic understanding and adaptive teaching require later semantic evaluation. Manual screen-reader/zoom checks and browsers other than local Edge remain unverified. No production readiness claim is made.

No existing backend source, learning rules, curriculum content, requirements, parent duplicates or student data were changed. No commit, push, public deployment, purchase or OpenAI API call was performed.
