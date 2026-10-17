---
name: nmi-curriculum-quality
description: Validate NMI curriculum provenance by country, grade and subject, stable topic and skill identifiers, and prerequisite relationships without inventing official requirements.
---

Own educational source integrity, not model-response scoring. Current get_curriculum(country, grade) reads text markers and has no subject dimension or structured prerequisite graph; curriculum.txt currently contains a heading only. Preserve its fallback and report missing coverage.

- Require explicit country/jurisdiction, grade system, subject, language, edition/year, issuing authority, title, source URL/document identifier, section/page locator and date checked for future curriculum records.
- Prefer the relevant education ministry, official curriculum authority or identifiable adopted syllabus. Separate verified official requirements, teacher-provided supplementary material and synthetic test content. Do not label a plausible model-generated outline official.
- Do not conflate grade labels between countries or silently substitute a different subject. Missing or conflicting sources require an unavailable/unverified status and clarification, not fabricated requirements.
- Define stable subject/topic/skill IDs separately from translated display labels. Check uniqueness, references, mappings and versioned migrations before renaming IDs already used in progress.
- For prerequisites, validate every referenced ID, reject self-links and cycles, and distinguish documented dependencies from a proposed pedagogical ordering. Explain the path when reporting a cycle.
- Test missing country/grade/subject, duplicate IDs, dangling edges, cycles, changed editions and absent sources with synthetic fixtures. Preserve existing curriculum and student files. Coordinate schema integration with nmi-backend-quality.

