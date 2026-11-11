# ptc-004 — Bug: create() validates only first checklist ID (#116597)

## Metadata
- **ID**: ptc-004
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116597 (Blocker)

---

## Planning

### Description
`ChecklistProgress.create()` and `ProjectChecklistProgress.create()` validated only `checklist_ids[0]` against the category's group permission. Every remaining id in a `checklist_id: [(6,0,[...])]` command was persisted unchecked, letting a non-permitted user attach a restricted checklist as long as it wasn't listed first.

### Goal
Validate every id in the M2M command, not just the first.

### Objectives
- Factor id-extraction and permission-check logic into reusable helpers
- Loop over every checklist id during create()

### Deliverables
- `_extract_checklist_ids()` / `_check_checklist_category_permission()` helpers in both files
- `create()` updated to use them

---

## Specification

### Complexity Score: EASY
### Complexity Rationale
2 files, logic refactor within an existing method, no schema changes.

### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | add helpers, validate all ids in `create()` |
| `models/project_checklist.py` | modify | mirror |

### Implementation Notes
The helpers are reused again by #116598 (write() incoming-vals check) and are the fix point that had to be adapted to Odoo 19's batch `create()` signature (see ptc-007 / #116679, discovered during verification).

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_create_blocks_restricted_second_id | Non-permitted user creates task with `[open, restricted]` | AccessError | pass |
| 2 | test_create_allows_unrestricted | Non-permitted user creates task with `[open]` only | Succeeds | pass |

### Test Plan for QA Team
**Scope**: `create()` permission validation across the full checklist_id M2M command.
**QA Steps**: 1) Create a task/project with two checklists, one restricted listed second — verify AccessError. 2) Create with only unrestricted checklists — verify success.
**Expected Outcomes**: No id in the M2M command escapes validation.

---

## Done

### Test Results
Verified live via `odoo-bin shell` against `ptc_audit_test` (after the #116679 batch-API fix was also applied, since both were needed for `create()` to run at all): both checks pass.

### Summary
`create()` now validates every checklist id in the incoming command via shared helpers.

### Commit / PR
`73001d0` — `#116597: create() validates only first checklist ID — validate every ID in the M2M command`
