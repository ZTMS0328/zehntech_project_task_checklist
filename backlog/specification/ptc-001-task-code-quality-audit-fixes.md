# ptc-001 — Code Quality Audit Fixes (18 Tickets)

## Metadata
- **ID**: ptc-001
- **Type**: task
- **Status**: specification
- **Complexity**: HIGH
- **Created**: 2026-07-09

---

## Planning

### Description
A quality audit of `zehntech_project_task_checklist` filed 18 Redmine Flux tickets (#116595–#116612) in project `ztocla` (id=462, "0041 Checklist Odoo App"): 3 Blocker security bugs, 5 High bugs, 4 High-severity improvements (performance/i18n), and 6 compliance/documentation tasks. All fixes are being made on the `code_quality_improvements` branch, one commit per ticket, after which each ticket is moved to "In QA" in Redmine Flux.

### Goal
Fix all 18 audit findings without breaking existing checklist functionality (task/project checklist creation, state workflow, progress bar, stage restriction, category permissions), and keep the module Odoo 19 compatible.

### Objectives
- Fix 3 Blocker access-control bugs (no ACL group, ORM state-bypass, incomplete M2M permission check on create)
- Fix 5 additional High-severity bugs (incomplete write() validation, permission-check crash, wrong Many2one model, wrong decorator, demo data loading in production)
- Fix 4 High-severity improvements (missing @api.depends, N+1 queries, unbounded search, missing translations)
- Deliver 6 compliance/documentation tasks (LICENSE, CHANGELOG, tests, Springboard index.html, file headers, manifest category/currency)
- Move all 18 Redmine Flux tickets to "In QA" with fix notes

### Deliverables
- 18 commits on `code_quality_improvements`, one per ticket, ticket number first in the message
- New `security/checklist_security.xml` (ir.rule) + updated `security/ir.model.access.csv`
- New `tests/` directory with 2 test files
- Rewritten `static/description/index.html` (Springboard template)
- `LICENSE` and `CHANGELOG.md` at module root
- OPL-1 copyright headers on 4 model files
- Updated `RELEASE_NOTES.md`, `documents/security-rules.md`, `backlog/TODO.md`
- All 18 Redmine tickets updated to "In QA"

---

## Specification

### Complexity Score: HIGH

### Complexity Rationale
18 findings across security, correctness, performance, i18n, and compliance. Touches all 4 model files, security ACL + new ir.rule XML, manifest, static assets (index.html rewrite), and adds a new tests/ package. Security-sensitive (ACL + permission-check logic).

### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `security/ir.model.access.csv` | modify | #116595 — set `group_id:id` to `project.group_project_user` on all 7 rows |
| `security/checklist_security.xml` | create | #116595 — ir.rule scoping item-line records to task/project assignees, with manager bypass |
| `__manifest__.py` | modify | #116595 (register new security XML), #116602 (demo key), #116612 (category/currency) |
| `models/task_checklist.py` | modify | #116596, #116597, #116598, #116599, #116601, #116603, #116604/#116605, #116611 (header) |
| `models/project_checklist.py` | modify | #116596, #116597, #116598, #116599, #116600, #116601, #116603, #116604/#116605, #116606, #116611 (header) |
| `models/checklist_category.py` | modify | #116611 (header only — `_()` usage already correct) |
| `models/task_stage_restriction.py` | modify | #116611 (header only) |
| `data/checklist_demo_data.xml` | none | referenced only via manifest key move (#116602) |
| `LICENSE` | create | #116607 |
| `CHANGELOG.md` | create | #116608 |
| `tests/__init__.py` | create | #116609 |
| `tests/test_task_checklist.py` | create | #116609 |
| `tests/test_project_checklist.py` | create | #116609 |
| `__init__.py` (root) | modify | #116609 — add `from . import tests` |
| `static/description/index.html` | modify | #116610 — Springboard template rewrite |

### Implementation Notes
- Ticket claims were verified against current code before editing; where a cited defect no longer exists (3 of the 4 `@api.depends` methods per file, 4 of the 6 cited `_()` strings), no change was made to avoid touching already-correct code.
- `_extract_checklist_ids()` / `_check_checklist_category_permission()` helpers are added once per model (task + project side) and reused by both `create()` and `write()`, closing #116597 and #116598 together without duplicating validation logic.
- `check_user_permission()` fix (#116599) uses direct Many2one field access instead of a redundant `browse()` call — simpler and correct on both task and project side.
- ir.rule additions (#116595) include an explicit `project.group_project_manager` bypass rule so managers/admins are never locked out by the new assignee-scoping rule.
- Springboard index.html reuses this module's existing screenshots — no new image assets needed.

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_checklist_creation_with_items | Create task.checklist + checklist.item lines | Record created, constraint on empty items enforced | pending |
| 2 | test_state_transition_cycle | approve_and_next → mark_completed → mark_canceled → reset_stage | State updates correctly at each step | pending |
| 3 | test_progress_bar_computation | Mark N of M items done/cancelled | `checklist_progress` matches done/(total-cancelled) | pending |
| 4 | test_progress_recomputes_without_refresh | Change item state, re-read task without explicit invalidate | `checklist_progress` reflects new state (depends fix) | pending |
| 5 | test_stage_restriction_blocks_incomplete | Move task to `restrict_task_completion` stage with incomplete items | ValidationError raised | pending |
| 6 | test_stage_restriction_allows_complete | Move task to restricted stage with all items done/cancelled | Write succeeds | pending |
| 7 | test_category_permission_enforced_on_write | Non-group user calls `write({'state': 'done'})` directly on checklist.item.line | AccessError/UserError raised (ORM-level, not just UI) | pending |
| 8 | test_create_validates_all_checklist_ids | Create task with `checklist_id: [(6,0,[allowed.id, restricted.id])]` as non-permitted user | AccessError raised for the restricted id | pending |
| 9 | test_write_validates_incoming_checklist_id | Write a restricted checklist onto an existing task as non-permitted user | AccessError raised | pending |
| 10 | test_project_checklist_project_id_model | Create project.checklist and set `project_id` | Accepts a `project.project` record | pending |

### Functional Tests
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Fresh install, no demo | `odoo-bin -i zehntech_project_task_checklist --without-demo=all` | Install succeeds, no sample categories/checklists present | pending |
| 2 | Fresh install, with demo | `odoo-bin -i zehntech_project_task_checklist` (demo enabled) | Sample categories/checklists appear as before | pending |
| 3 | Non-project-group user access | Log in as internal user outside `project.group_project_user` | Checklist models return AccessError at ORM layer | pending |
| 4 | State-change buttons | Click Mark Done/In Progress/Cancel/Reset on a task checklist item | No AttributeError; state changes correctly | pending |

### Edge Cases
| # | Scenario | Expected Behaviour | Status |
|---|----------|----------------------|--------|
| 1 | Admin user (`base.group_system`) performs any checklist action | Always succeeds, bypasses category/group checks | pending |
| 2 | Task with zero checklist items | `checklist_progress` = 0.0, no division by zero | pending |
| 3 | 100+ checklist categories, task list view with 50+ tasks | Category domain computed with a bounded number of queries, not per-record `search([])` | pending |

### Test Plan for QA Team

**Scope**: Code quality/security/performance/compliance fixes across 18 audit tickets (#116595–#116612) on `zehntech_project_task_checklist`.

**Pre-conditions**:
- Module installed on a clean Odoo 19 instance
- Two test users: one in a checklist category's permitted group, one not
- At least one project task with a checklist attached and a stage with `restrict_task_completion` enabled

**QA Steps**:
1. Install with `--without-demo=all` — verify no sample checklist data appears
2. Install with demo enabled — verify sample checklist categories/checklists appear
3. As a non-project-group user, try to open Checklists — verify access is denied
4. As a permitted user, click each of the 4 state-change buttons on a checklist item — verify no server error and correct state change
5. As a non-permitted user, attempt `env['checklist.item.line'].write({'state': 'done'})` via a technical/dev tool — verify AccessError
6. Create a task and add two checklists (one unrestricted, one restricted) as a non-permitted user — verify AccessError on the restricted one
7. Mark a checklist item done — verify the progress bar updates immediately without a manual page refresh
8. Try to move a task with incomplete checklist items into a restricted stage — verify it's blocked
9. Open the rewritten `static/description/index.html` in a browser — verify it renders correctly with all 6 screenshots and updated download link

**Expected Outcomes**:
- No regressions to existing checklist creation, state workflow, progress bar, or stage restriction behavior
- All previously-open security bypasses are closed
- Module installs cleanly with 0 fatal errors, no demo data on production install

**Out of Scope**:
- #116585 (Competitor & Market Analysis) — business/research task, not a code fix
- Store Listing screenshot quality/CEO sign-off on the Springboard scorecard dimension
