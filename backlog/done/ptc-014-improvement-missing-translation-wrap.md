# ptc-014 — Improvement: Missing _() translation on 2 user-facing strings (#116606)

## Metadata
- **ID**: ptc-014
- **Type**: improvement
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116606 (High)

---

## Planning

### Description
Ticket claimed all 3 model files were missing the `_` import and 6 strings were unwrapped. Verified against current code: `task_checklist.py`, `project_checklist.py`, and `checklist_category.py` all already import `_` from `odoo`. Of the 6 cited strings, 4 were already correctly wrapped. Only 2 genuinely bare strings existed, both in `project_checklist.py`.

### Goal
Wrap the 2 real un-translated strings.

### Deliverables
- `models/project_checklist.py` — wrapped both strings in `_()`

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/project_checklist.py` | modify | wrap `_check_unique_checklist_name`'s ValidationError and `_onchange_checklist_id`'s UserError in `_()` |

### Implementation Notes
No changes made to the 4 already-correctly-wrapped strings or to the `_` imports (already present in all 3 files) — avoided touching already-correct code.

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Install clean | Update module | 0 errors | pass |
| 2 | Translation lookup | With a German .po entry for these strings, trigger both errors in German | Message appears in German | pending (manual language-switch check, not exercised in this pass) |

---

## Done

### Test Results
Verified live: module updates with 0 errors after the wrap.

### Summary
Wrapped the 2 genuinely bare user-facing strings in `project_checklist.py`; confirmed the other 4 cited strings and all 3 `_` imports were already correct.

### Commit / PR
Committed as `#116606: Missing _() translation on 2 user-facing strings in project_checklist.py`
