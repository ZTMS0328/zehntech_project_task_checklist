# ptc-006 — Bug: checklist.category SQL constraint broken under Odoo 19 (not filed as a separate Redmine ticket, per instruction)

## Metadata
- **ID**: ptc-006
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09

---

## Planning

### Description
Discovered during pre-commit runtime verification (not one of the 18 audit tickets, and not filed as a separate Redmine ticket per explicit instruction — fixed directly as part of the Odoo 19 compatibility pass). `checklist_category.py` declared:
```
_sql_constraints = [('unique_category_name', 'unique(lower(name))', '...')]
```
Odoo 19 logs "Model attribute '_sql_constraints' is no longer supported" and does not apply it. Migrating it to the new `models.Constraint('unique(lower(name))', ...)` syntax still fails — PostgreSQL table constraints can't reference an expression like `lower(name)`; only a `CREATE UNIQUE INDEX` can. This means the SQL-level constraint never actually worked in any Odoo version, old or new — it silently failed at the DB layer in both cases.

### Goal
Stop logging a broken/deprecated declaration and rely on the enforcement mechanism that actually works.

### Deliverables
- `models/checklist_category.py` — removed the non-functional SQL constraint declaration, kept the existing `@api.constrains('name')` Python-level uniqueness check (the mechanism that was actually enforcing this rule all along)

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `models/checklist_category.py` | modify | remove dead `_sql_constraints` declaration, add a comment explaining why a table constraint can't express this, keep the Python constraint |

### Implementation Notes
A true race-safe fix would need a functional `UNIQUE INDEX` via a custom `_auto_init()` override — out of scope here since the Python-level check already covers all normal ORM usage paths (no raw SQL insert path exists in this module).

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Clean install log | Install/update module on Odoo 19 | No `_sql_constraints` warning, no `odoo.schema` syntax-error warning | pass |
| 2 | Duplicate category name still blocked | Create two categories with the same name (case-insensitive) via the ORM | ValidationError | pass |

---

## Done

### Test Results
Verified live against `ptc_audit_test`: install log is clean of both the deprecation warning and the schema syntax error; duplicate-name creation still raises ValidationError via the Python constraint.

### Summary
Removed a SQL constraint declaration that never actually worked (PostgreSQL doesn't support expression-based table constraints), in favor of the pre-existing, functioning Python-level uniqueness check.

### Commit / PR
Committed as "fix: remove non-functional checklist.category SQL constraint declaration — Odoo 19 compatibility"
