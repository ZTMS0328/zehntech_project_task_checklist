# ptc-009 — Bug: project.checklist.project_id links to project.task instead of project.project (#116600)

## Metadata
- **ID**: ptc-009
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116600 (High)

---

## Planning

### Description
`project_checklist.py`'s `project_id` Many2one comodel was `'project.task'` (copy-paste from `task_ids` on the same model), so the "Project" field on a Project Checklist record actually showed a task selector instead of a project selector.

### Goal
Point `project_id` at the correct model.

### Deliverables
- `models/project_checklist.py` updated

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/project_checklist.py` | modify | `project_id` comodel `'project.task'` → `'project.project'` |

### Implementation Notes
Confirmed safe before changing: no view or demo-data record (`data/checklist_demo_data.xml`) sets this field, so there's no existing data pointing at task IDs that would need migration.

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Field points at projects | Open a Project Checklist record, inspect the Project field | Shows a project selector, not a task selector | pass |

---

## Done

### Test Results
Verified live: module installs/updates cleanly with the corrected comodel; no existing data referenced the old (wrong) model.

### Summary
Fixed the copy-paste bug — `project_id` now correctly links to `project.project`.

### Commit / PR
Committed as `#116600: project.checklist.project_id Many2one links to project.task instead of project.project`
