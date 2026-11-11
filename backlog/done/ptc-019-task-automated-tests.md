# ptc-019 — Task: Zero automated tests (#116609)

## Metadata
- **ID**: ptc-019
- **Type**: task
- **Status**: done
- **Complexity**: MEDIUM
- **Created**: 2026-07-09
- **Redmine**: #116609 (High)

---

## Planning

### Description
No `tests/` directory existed. Needed coverage of: install/basic creation, checklist+items creation, full state transition cycle, progress bar computation, stage restriction, and category group-permission enforcement.

### Deliverables
- `tests/__init__.py`, `tests/test_task_checklist.py`, `tests/test_project_checklist.py`
- Root `__init__.py` updated with `from . import tests`

---

## Specification

### Complexity Score: MEDIUM
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `tests/__init__.py` | create | test package init |
| `tests/test_task_checklist.py` | create | 15 test methods covering task-side checklist creation, state cycle, direct-write permission bypass, progress bar, stage restriction, category permission on create()/write() |
| `tests/test_project_checklist.py` | create | 7 test methods mirroring the project-side model + comodel-fix regression test |
| `__init__.py` | modify | add `from . import tests` |

### Implementation Notes
Discovered mid-implementation: creating a `project.project` record requires `project.group_project_manager` in stock Odoo ACLs (regular `group_project_user` can only work within existing projects) — adjusted the project-side test users to hold the manager group, since the checklist category's own `group_permission` (not the base project ACL) is the axis actually under test.

---

## Test Cases

### Unit Tests (all implemented as real test methods, not just planned)
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|--------------------|-------------------|--------|
| 1 | test_checklist_creation_with_items | both files | items attached correctly | pass |
| 2 | test_checklist_requires_at_least_one_item | both files | ValidationError | pass |
| 3 | test_duplicate_checklist_name_in_category_blocked | task side | ValidationError | pass |
| 4 | test_project_id_field_points_at_project_project | project side | regression test for #116600 | pass |
| 5 | test_state_transition_cycle | task side | todo→in_progress→done→cancel→todo | pass |
| 6 | test_direct_write_state_blocked_for_non_permitted_user | task side | UserError | pass |
| 7 | test_direct_write_state_allowed_for_permitted_member | task side | succeeds | pass |
| 8 | test_progress_bar_computation | both files | 0.0 → 50.0 without manual refresh | pass |
| 9 | test_progress_bar_zero_items_no_division_error | task side | 0.0, no crash | pass |
| 10 | test_stage_restriction_blocks_incomplete_checklist | task side | ValidationError | pass |
| 11 | test_stage_restriction_allows_completed_checklist | task side | succeeds | pass |
| 12 | test_create_blocks_restricted_checklist_listed_second | both files | AccessError | pass |
| 13 | test_create_allows_unrestricted_checklist | both files | succeeds | pass |
| 14 | test_write_blocks_swapping_in_restricted_checklist | both files | AccessError | pass |
| 15 | test_write_allows_permitted_member_to_set_restricted_checklist | both files | succeeds | pass |

### Test Plan for QA Team
**Scope**: Automated regression coverage for the module's core checklist workflow and the security fixes in this audit cycle.
**QA Steps**: `odoo-bin -d <db> -u zehntech_project_task_checklist --test-enable --test-tags=//zehntech_project_task_checklist --stop-after-init --without-demo=all`
**Expected Outcomes**: 22/22 tests pass, 0 errors.

---

## Done

### Test Results
Ran live against a fresh Odoo 19 database: **22 tests, 0 failed, 0 errors** (1744 queries, 1.58s).

### Summary
Added full automated test coverage across both task- and project-side checklist models, covering every scenario the ticket asked for plus regression tests for several of the other bugs fixed in this audit cycle (#116596, #116597, #116598, #116600, #116603).

### Commit / PR
Committed as `#116609: Zero automated tests — add tests/ package with 22 test methods covering the full checklist workflow`
