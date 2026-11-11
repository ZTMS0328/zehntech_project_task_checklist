# ptc-018 — Task: 4 model files missing copyright/license headers (#116611)

## Metadata
- **ID**: ptc-018
- **Type**: task
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116611 (High)

---

## Planning
### Description
`models/checklist_category.py`, `models/project_checklist.py`, `models/task_checklist.py`, and `models/task_stage_restriction.py` all began directly with `from odoo import ...`, no file header.

### Deliverables
- Standard 2-line Zehntech OPL-1 copyright header added to the top of all 4 files, matching the format used across the Zehntech portfolio (e.g. `zt_capacity_planning`)

---

## Specification
### Complexity Score: EASY
| File | Action | Description |
|------|--------|--------------|
| `models/checklist_category.py` | modify | add header |
| `models/project_checklist.py` | modify | add header |
| `models/task_checklist.py` | modify | add header |
| `models/task_stage_restriction.py` | modify | add header |

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Install clean | Update module | 0 errors | pass |

---

## Done
### Summary
Added the standard 2-line copyright/license header to all 4 model files.

### Commit / PR
Committed as `#116611: 4 of 5 model Python files missing standard copyright/license file headers`
