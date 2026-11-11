# ptc-007 — Bug: create() overrides crash on every call under Odoo 19's batch-create contract (#116679)

## Metadata
- **ID**: ptc-007
- **Type**: bug
- **Status**: done
- **Complexity**: MEDIUM
- **Created**: 2026-07-09
- **Redmine**: #116679 (Blocker) — newly filed, discovered during pre-commit verification of #116597/#116598

---

## Planning

### Description
Not one of the original 18 audit tickets — discovered while live-testing #116597/#116598 against a local Odoo 19 instance. Odoo 19's `api.model` decorator (`odoo/orm/decorators.py`) special-cases any method literally named `create`: it auto-wraps it with `model_create_multi`, whose wrapper *always* normalizes its argument to a list before calling the wrapped function, even for a single-dict call. `ChecklistProgress.create(self, vals)` and `ProjectChecklistProgress.create(self, vals)` were written for the old single-dict contract and called `vals.get(...)` directly — under Odoo 19 this always raises `AttributeError: 'list' object has no attribute 'get'`, on every task/project creation, for every user. This is separate from #116601 (PTC-QA-07), which only flagged the same decorator issue on `write()`.

### Goal
Make `create()` work under Odoo 19's real batch-create API.

### Objectives
- Rewrite both `create()` overrides to accept `vals_list` (a list of dicts) per `@api.model_create_multi`, looping over each dict for validation, and pass the full list to `super().create(vals_list)`

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` updated
- Redmine ticket #116679 filed and closed per the security/critical-issue process

---

## Specification

### Complexity Score: MEDIUM
### Complexity Rationale
Requires understanding the Odoo 19 ORM decorator internals, not just a text-pattern fix; touches the same methods as #116597/#116598 so had to be sequenced carefully to keep commits atomic per ticket.

### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | `@api.model_create_multi def create(self, vals_list):` — loop over `vals_list`, delegate to `super().create(vals_list)` |
| `models/project_checklist.py` | modify | mirror |

### Implementation Notes
`is_admin` is computed once per call (not per vals dict) since it's a user-level check, not vals-specific — preserves the original per-record semantics exactly while fixing the signature.

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_create_single_dict_no_crash | `env['project.task'].create({...})` | Task created, no AttributeError | pass |
| 2 | test_create_still_enforces_permission | Non-permitted user creates with restricted checklist | AccessError (not AttributeError) | pass |

### Test Plan for QA Team
**Scope**: `create()` works correctly under Odoo 19's batch API while preserving all existing validation.
**QA Steps**: 1) Create a task via the UI — verify no server error. 2) Create via `odoo-bin shell` with a single dict — verify no AttributeError. 3) Re-run the #116597/#116598 permission checks — verify they still pass.
**Expected Outcomes**: `create()` behaves identically to before from a business-logic standpoint, just Odoo-19-compatible.

---

## Done

### Test Results
Verified live against `ptc_audit_test`: module installs/updates with 0 errors; `env['project.task'].create({...})` (single dict) succeeds; the #116597/#116598 permission checks (previously blocked by this crash) now pass end-to-end.

### Summary
Rewrote both `create()` overrides to the Odoo 19 `@api.model_create_multi` batch contract. Filed as Redmine #116679 per the security/critical-issue process since it's a severity-Blocker bug the static audit missed (it requires understanding decorator runtime behavior, not a pattern match).

### Commit / PR
Committed as `#116679: create() overrides crash on every call — @api.model on create() always receives a list in Odoo 19`
