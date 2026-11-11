# ptc-010 — Bug: write() overrides decorated with @api.model (#116601)

## Metadata
- **ID**: ptc-010
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116601 (High)

---

## Planning

### Description
`ChecklistProgress.write()` and `ProjectChecklistProgress.write()` were decorated `@api.model`, which is the correct decorator for `create()` (model-level, no meaningful recordset) but wrong for `write()` (always operates on a real recordset). `@api.model` marks the method `_api_model = True`, semantically incorrect for a recordset method per Odoo's own API contract.

### Goal
Remove the incorrect decorator.

### Deliverables
- `models/task_checklist.py`, `models/project_checklist.py` updated

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/task_checklist.py` | modify | remove `@api.model` above `write()` |
| `models/project_checklist.py` | modify | mirror |

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Bulk write on multiple records | `tasks.write({'stage_id': ...})` on a 2-record recordset | Both records updated correctly in one call | pass |

---

## Done

### Test Results
Verified live via `odoo-bin shell`: `(task1 + task2).write({'stage_id': stage.id})` applies to both records correctly.

### Summary
Removed the incorrect `@api.model` decorator from both `write()` overrides.

### Commit / PR
Committed as `#116601: write() overrides decorated with @api.model — remove the incorrect decorator`
