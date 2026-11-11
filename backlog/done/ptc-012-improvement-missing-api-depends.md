# ptc-012 — Improvement: 8 compute methods missing @api.depends (#116603)

## Metadata
- **ID**: ptc-012
- **Type**: improvement
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116603 (High)

---

## Planning

### Description
Ticket claimed 4 compute methods per file (8 total) were missing `@api.depends`. Verified against current code before changing anything: `_compute_has_checklist`, `_compute_category_domain`, and `_compute_checklist_domain` already had correct `@api.depends` decorators in both files (likely fixed in an earlier pass). Only `_compute_checklist_progress` was genuinely missing it in both files — matching the ticket's own repro steps ("mark an item done, progress bar does not update until manual refresh").

### Goal
Make the progress bar recompute automatically.

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` — added `@api.depends('checklists', 'checklists.state')` to `_compute_checklist_progress`

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | add `@api.depends` to `_compute_checklist_progress` |
| `models/project_checklist.py` | modify | mirror |

### Implementation Notes
No changes made to the other 3 compute methods per file since they were already correctly decorated — avoided touching already-correct code.

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Progress recomputes without refresh | Mark one of two items done, re-read `checklist_progress` without manual invalidation | Value updates from 0.0 to 50.0 | pass |

---

## Done

### Test Results
Verified live via `odoo-bin shell`: before marking an item done, `checklist_progress` = 0.0; after marking one of two items done, re-reading the field (no manual cache invalidation) returns 50.0.

### Summary
Added the missing `@api.depends` to `_compute_checklist_progress` on both task and project side.

### Commit / PR
Committed as `#116603: 8 compute methods missing @api.depends — add the one that's actually missing (_compute_checklist_progress)`
