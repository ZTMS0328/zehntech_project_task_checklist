# ptc-015 — Task: No LICENSE file (#116607)

## Metadata
- **ID**: ptc-015
- **Type**: task
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116607 (High)

---

## Planning
### Description
No `LICENSE` file existed at the module root, required for OPL-1 paid modules.

### Deliverables
- `LICENSE` at module root, standard OPL-1 text (copied verbatim from the same text used across the Zehntech portfolio, e.g. `zehntech_scrum_meeting_management/LICENSE`)

---

## Specification
### Complexity Score: EASY
| File | Action | Description |
|------|--------|--------------|
| `LICENSE` | create | full OPL-1 license text |

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | File present | Browse module root | `LICENSE` file exists with OPL-1 text | pass |

---

## Done
### Summary
Created `LICENSE` with the standard OPL-1 text matching the rest of the Zehntech portfolio.

### Commit / PR
Committed as `#116607: No LICENSE file — add OPL-1 license text to module root`
