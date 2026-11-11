# ptc-008 — Bug: write() validates current checklist, not incoming vals (#116598)

## Metadata
- **ID**: ptc-008
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116598 (High)

---

## Planning

### Description
`ChecklistProgress.write()` (and its project-side mirror) only checked `task.checklist_id.checklist_category` — the record's CURRENT value — before calling `super().write(vals)`. The incoming `vals['checklist_id']` was never inspected, letting a non-permitted user swap in a restricted checklist silently via write().

### Goal
Validate the incoming checklist_id command the same way create() does.

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` updated

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | when `'checklist_id' in vals`, call `_check_checklist_category_permission()` on the incoming ids |
| `models/project_checklist.py` | modify | mirror |

### Implementation Notes
Reuses the `_extract_checklist_ids()` / `_check_checklist_category_permission()` helpers added for ptc-004 (#116597) — no new logic, just a second call site. The existing current-value check is left in place (it covers writes that don't touch `checklist_id` at all).

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_write_incoming_blocked | Non-permitted user writes a restricted checklist onto an existing task | AccessError | pass |
| 2 | test_write_incoming_allowed_for_member | Permitted member does the same write | Succeeds | pass |

### Test Plan for QA Team
**Scope**: `write()` permission validation on the incoming `checklist_id` command.
**QA Steps**: 1) As a non-permitted user, try to write a restricted checklist onto an existing task/project — verify AccessError. 2) As a permitted member, verify the same write succeeds.
**Expected Outcomes**: No silent swap-in of a restricted checklist via write().

---

## Done

### Test Results
Verified live via `odoo-bin shell` against `ptc_audit_test` (after ptc-005/#116599 and ptc-007/create()-batch-fix were also in place, since all three are needed for the flow to run end-to-end): both checks pass.

### Summary
`write()` now validates every incoming checklist id via the shared helper, in addition to the existing current-value check.

### Commit / PR
Committed as `#116598: write() validates current checklist, not incoming vals — validate the incoming checklist_id command too`
