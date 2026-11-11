# ptc-013 — Improvement: N+1 ORM queries + unbounded search in category domain compute (#116604, #116605)

## Metadata
- **ID**: ptc-013
- **Type**: improvement
- **Status**: done
- **Complexity**: MEDIUM
- **Created**: 2026-07-09
- **Redmine**: #116604 (High), #116605 (High) — combined, same root cause

---

## Planning

### Description
`_compute_category_domain` in both files ran up to 3 `search()` calls per record inside the `for record in self` loop, and the "no restriction" fallback used an unbounded `search([])`. Both tickets share the same fix point.

### Goal
Compute the category partitions once for the whole recordset; eliminate the per-record/unbounded searches.

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` — restructured `_compute_category_domain`

---

## Specification

### Complexity Score: MEDIUM
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | one `search([])` for the whole recordset, partitioned via `.filtered()`, filtered again per record in Python |
| `models/project_checklist.py` | modify | mirror |

### Implementation Notes
During verification, discovered a **pre-existing** quirk (present identically in the unmodified original code, confirmed by testing the literal original expression on a clean DB): for a task/project with no assigned users, the "no restriction" branch's resulting `category_domain` Many2many value does not include categories that have `group_permission` set, even though a plain `search([])` executed outside the compute method returns them correctly, and even though the same categories ARE correctly included via `.filtered()` for the assigned-user branch. This reproduces with the original code, my restructured code, and every variant tried (union of two searches, single search + filter, `.ids` vs recordset assignment) — it is specific to how this particular compute field materializes results for that one code path, not something this fix introduced or made worse. Not filed as a new ticket per instruction; flagging here for future investigation since it's a real (if minor, non-security) discrepancy in the "unassigned task shows all categories" UX case.

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Correctness for assigned users | Task assigned to a user in a group-restricted category's group | Category appears in `category_domain` | pass |
| 2 | Query count | Compute `category_domain` for 20 records at once | 1 query against `checklist_category` (was up to 60) | pass |

---

## Done

### Test Results
Verified live: assigned-user correctness passes; query count for 20 records dropped from up to 60 to exactly 1 (measured via cursor-level instrumentation, not just code inspection).

### Summary
Eliminated the N+1 pattern and the unbounded per-record `search([])` fallback in one restructure. Noted (not fixed, pre-existing and out of scope) a separate quirk in the unassigned-task branch.

### Commit / PR
Committed as `#116604 #116605: N+1 ORM queries + unbounded search in category domain compute — fetch once, filter in Python`
