# Release Notes — Checklist for Projects and Tasks

## [Unreleased]

### Security
- **ptc-021**: `ir.model.access.csv` + `checklist_security.xml` (`ir.rule`) converted to Odoo 20 `security/ir.access.csv` — item-line access keeps the assignee/member domain for project users, unrestricted only for project managers

### Bug Fixes
- **ptc-021**: checklist row buttons rendered blank icons on Odoo 20 (FontAwesome removed) — now Material Symbols `schedule` / `check` / `close` / `refresh`, with titles
- **ptc-021**: task/project kanban progress bar now inherits Odoo 20's `project.view_task_card` / `project.view_project_card` (the old `view_task_kanban` anchor no longer exists)

### Internal
- **ptc-021**: ported to Odoo 20.0 (version 20.0.1.1.0); `_description` added to `task.checklist`, `project.checklist`, `checklist.category`; Odoo 19 → 20 references in manifest, README and index.html

---

## [19.0.1.1.0] — 2026-10-27

### Security
- **ptc-002 / #116595**: scoped all 7 checklist ACLs to `project.group_project_user`; added `ir.rule` for item-line assignee scoping with a manager bypass
- **ptc-003 / #116596**: closed a direct-ORM state bypass — `write()` on `checklist.item.line` / `project.checklist.item.line` now enforces `check_user_permission()` server-side
- **ptc-004 / #116597**: `create()` now validates every checklist id in the M2M command, not just the first
- **ptc-008 / #116598**: `write()` now validates the incoming `checklist_id` command, not just the record's current value

### Performance
- **ptc-013 / #116604, #116605**: eliminated an N+1 query pattern and an unbounded `search([])` fallback in `_compute_category_domain`

### Bug Fixes
- **ptc-005 / #116599**: `check_user_permission()` no longer crashes with `AttributeError`
- **ptc-006**: removed a non-functional `checklist.category` SQL constraint declaration (Odoo 19 compatibility — not a Flux ticket)
- **ptc-007**: `create()` overrides rewritten for Odoo 19's batch-create contract, fixing a crash on every task/project creation (not a Flux ticket)
- **ptc-009 / #116600**: `project.checklist.project_id` now correctly links to `project.project`
- **ptc-010 / #116601**: removed the incorrect `@api.model` decorator from `write()`
- **ptc-011 / #116602**: demo data no longer installs on production installs
- **ptc-014 / #116606**: wrapped 2 user-facing strings in `_()` for translation

### Internal
- **ptc-015 / #116607**: added `LICENSE` (OPL-1)
- **ptc-016 / #116608**: added `CHANGELOG.md`
- **ptc-017 / #116612**: manifest `category` and `currency` compliance
- **ptc-018 / #116611**: added copyright headers to 4 model files
- **ptc-019 / #116609**: added `tests/` with 22 automated test methods
- **ptc-020 / #116610**: rewrote `static/description/index.html` to the Springboard template

---

## [19.0.1.0.0] — initial

### Features
- Initial release — customizable checklists for projects and tasks, category-based access control, per-item 4-state workflow, dynamic progress bar, and per-stage completion restriction.
