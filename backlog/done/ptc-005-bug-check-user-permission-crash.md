# ptc-005 — Bug: check_user_permission() crashes with AttributeError (#116599)

## Metadata
- **ID**: ptc-005
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116599 (High)

---

## Planning

### Description
`check_user_permission()` does `self.env['checklist.item'].browse(self.check_list_item_id).id` then dereferences `.checklist_id` on the resulting int, raising `AttributeError` on every state-change action. On the project side, the same crash occurs and the wrong model (`checklist.item` instead of `project.checklist.item`) is browsed.

### Goal
Make `check_user_permission()` actually run, on both task and project side.

### Objectives
- Remove the redundant/incorrect `browse()` call — `check_list_item_id` is already a Many2one field, so `self.check_list_item_id` already is the linked record

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` fixed

---

## Specification

### Complexity Score: EASY
### Complexity Rationale
2-line fix per file, no schema/behavior change beyond removing the crash.

### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | `checklist_item = self.check_list_item_id` (drop `.browse(...).id`) |
| `models/project_checklist.py` | modify | same; also fixes the wrong-model-browsed half of the bug since no model-string browse is used at all |

### Implementation Notes
This is a blocking prerequisite for #116596's write() guard to behave correctly end-to-end — without this fix, every state-change attempt (permitted or not) raises AttributeError instead of the intended allow/deny outcome. Discovered this dependency during live verification of #116596/#116598.

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_state_button_no_crash | Permitted user clicks any of the 4 state buttons | State changes, no AttributeError | pending |
| 2 | test_permission_denial_still_works | Non-permitted user attempts state change | UserError/AccessError (not AttributeError) | pending |

### Test Plan for QA Team
**Scope**: `check_user_permission()` functions correctly instead of crashing.
**QA Steps**: 1) Click Mark Done/In Progress/Cancel/Reset as a permitted user — verify no server error. 2) Attempt the same as a non-permitted user — verify a clean permission-denied message, not a stack trace.
**Expected Outcomes**: No AttributeError anywhere in this flow.

---

## Done

### Test Results
Verified live via `odoo-bin shell` against `ptc_audit_test`: with this fix applied, `#116596`'s write() guard correctly raises UserError for non-permitted users and succeeds for permitted members (previously both cases crashed with AttributeError).

### Summary
Replaced the redundant `browse(...).id` + dereference with a direct Many2one field access, on both task and project side. This also incidentally fixed the "wrong model browsed" half of the bug on the project side.

### Commit / PR
Committed as `#116599: check_user_permission() crashes with AttributeError — use direct Many2one field access instead of browse(...).id`
