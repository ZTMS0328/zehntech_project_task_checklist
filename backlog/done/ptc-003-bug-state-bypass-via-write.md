# ptc-003 — Bug: Checklist item state bypass via direct ORM write() (#116596)

## Metadata
- **ID**: ptc-003
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116596 (Blocker)

---

## Planning

### Description
`checklist.item.line.state` was `readonly=True` at the field level and gated only by button methods calling `check_user_permission()` before mutating `state`. A direct `write({'state': 'done'})` via sudo/JSON-RPC skipped every permission check, letting the stage-restriction logic (which trusts `item.state`) be bypassed.

### Goal
Enforce `check_user_permission()` server-side on every state write, not just through button methods.

### Objectives
- Add `write()` override on `checklist.item.line` and `project.checklist.item.line` that calls `check_user_permission()` whenever `'state'` is in `vals`

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` updated

---

## Specification

### Complexity Score: EASY
### Complexity Rationale
2 files, additive `write()` override, no new models.

### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | add `write()` to `CheckListItemLine` |
| `models/project_checklist.py` | modify | add `write()` to `ProjectCheckListItemLine` |

### Implementation Notes
Button methods (`approve_and_next`, `mark_completed`, `mark_canceled`, `reset_stage`) keep their existing explicit `check_user_permission()` calls as defense in depth — the new `write()` override is the authoritative server-side gate.

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_direct_write_blocked | Non-permitted user calls `line.write({'state': 'done'})` | AccessError/UserError | pass |
| 2 | test_direct_write_allowed_for_member | Permitted user calls same write | Succeeds, state updates | pass |

### Test Plan for QA Team
**Scope**: Server-side enforcement of checklist item state changes.
**QA Steps**: 1) As a non-permitted user, attempt a direct ORM write of `state` — verify it's blocked. 2) As a permitted user/admin, verify buttons and direct writes both still work.
**Expected Outcomes**: No ORM-level bypass of the category permission check.

---

## Done

### Test Results
Verified live via `odoo-bin shell` against `ptc_audit_test`: non-permitted direct write raises UserError; permitted member's direct write succeeds and updates state.

### Summary
Added `write()` guard calling `check_user_permission()` whenever `state` changes, on both task- and project-side item line models.

### Commit / PR
`8b87401` — `#116596: Checklist item state bypass via direct ORM write() — enforce check_user_permission() server-side on state changes`
