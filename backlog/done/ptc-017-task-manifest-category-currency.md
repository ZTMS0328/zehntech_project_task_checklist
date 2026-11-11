# ptc-017 — Task: Manifest category/currency not compliant (#116612)

## Metadata
- **ID**: ptc-017
- **Type**: task
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116612 (High)

---

## Planning
### Description
`__manifest__.py` used a comma-separated multi-value `category` string (not allowed for paid modules) and `currency: "USD"` instead of the required `EUR`.

### Deliverables
- `__manifest__.py`: `category` → `"Project"`, `currency` → `"EUR"`

---

## Specification
### Complexity Score: EASY
| File | Action | Description |
|------|--------|--------------|
| `__manifest__.py` | modify | single-value category, EUR currency |

### Implementation Notes
`price` left at 15.00 — the ticket's expected-behavior block only shows a currency change, not a price conversion.

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Install clean | Update module | 0 errors | pass |

---

## Done
### Summary
Manifest now uses a single valid category and EUR currency.

### Commit / PR
Committed as `#116612: Manifest category not allowed for paid modules; currency set to USD instead of EUR`
