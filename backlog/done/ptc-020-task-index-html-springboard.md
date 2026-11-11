# ptc-020 — Task: index.html requires Springboard template rewrite (#116610)

## Metadata
- **ID**: ptc-020
- **Type**: task
- **Status**: done
- **Complexity**: MEDIUM
- **Created**: 2026-07-09
- **Redmine**: #116610 (High)

---

## Planning

### Description
The 537-line `static/description/index.html` was a developer-authored, feature-listing store page. Per the Zehntech Springboard workflow (already applied to `zehntech_scrum_meeting_management/static/description/index.html`), store listings must use outcome-led copy — what customers achieve, not a feature dump.

### Goal
Rewrite the page using the same Springboard structure, reusing this module's own existing screenshots.

### Deliverables
- Rewritten `static/description/index.html`: hero, overview (with the existing Kopyst user guide link), 3-card benefits, key features + image, 6-tab screenshot gallery, About Zehntech, achievement stats, FAQ accordion, Our Odoo Services grid, Contact Us

---

## Specification

### Complexity Score: MEDIUM
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `static/description/index.html` | modify | full rewrite to the Springboard structure with outcome-led copy |

### Implementation Notes
- Reused all 6 existing screenshots (`checklist_management.png`, `multi_select_checklist.png`, `status_management.png`, `progress.png`, `category_checklist.png`, `security.png`) and the hero GIF — no new image assets needed, this module already had real UI screenshots (unlike the scrum module's audit, which had zero).
- Fixed the stale `apps.odoo.com/.../18.0/...` download link to `19.0`, matching the manifest version.
- Verified every referenced image filename exists on disk, and the resulting HTML parses cleanly via `lxml.html`.
- Final CEO sign-off on the Store Listing scorecard dimension is outside what can be verified locally (per the sibling module's own audit notes) — out of scope here.

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Valid HTML | Parse the file with lxml.html | No parse error | pass |
| 2 | All images resolve | Check every referenced image filename against the images/ folder | All 30 exist | pass |
| 3 | Module still installs | `odoo-bin -u zehntech_project_task_checklist` | 0 errors (index.html isn't manifest-loaded, but confirms nothing else broke) | pass |

---

## Done

### Test Results
HTML parses cleanly; all referenced images exist; module install unaffected.

### Summary
Rewrote `index.html` to the Springboard template with outcome-led copy across every section, reusing existing screenshots and fixing the stale version-18 download link.

### Commit / PR
Committed as `#116610: index.html requires Springboard template rewrite — outcome-led copy using existing screenshots`
