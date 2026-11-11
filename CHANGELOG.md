# Changelog — Checklist for Projects and Tasks

All notable changes to this module are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [20.0.1.1.0] — 2026-10-27 — Odoo 20.0 port

### Changed
- Ported to Odoo 20.0 Community
- Access rights moved from `ir.model.access.csv` + `ir.rule` to Odoo 20's single `security/ir.access.csv` (same effective access)
- Checklist row buttons use Material Symbols icons (Odoo 20 dropped FontAwesome) and show a tooltip
- Kanban progress bar moved to Odoo 20's task/project card views

### Fixed
- Blank action-button icons on Odoo 20
- Install failure on Odoo 20: task kanban inheritance targeted a removed `date_deadline` anchor
- "Model has no _description" warnings for `task.checklist`, `project.checklist`, `checklist.category`

---

## [19.0.1.1.0] — 2026-10-27 — code quality & security audit fixes

### Security
- Scoped all 7 checklist ACLs to `project.group_project_user`; added `ir.rule` for item-line assignee scoping
- Closed a direct-ORM state bypass on `checklist.item.line` / `project.checklist.item.line`
- `create()`/`write()` now validate every checklist id in the M2M command, not just the first / current value

### Fixed
- `check_user_permission()` no longer crashes with `AttributeError`
- `project.checklist.project_id` now correctly links to `project.project`
- `write()` no longer uses the incorrect `@api.model` decorator
- `create()` overrides rewritten for Odoo 19's batch-create contract (`@api.model_create_multi`)
- Demo data no longer installs on production installs (moved to the `demo` manifest key)
- Removed a non-functional `checklist.category` SQL constraint declaration (Odoo 19 no longer supports `_sql_constraints`; the expression-based constraint never worked at the database level in any version)

### Performance
- Eliminated N+1 query pattern and unbounded `search([])` fallback in `_compute_category_domain`

### Internal
- Added OPL-1 copyright headers to model files
- Added `LICENSE` and this `CHANGELOG.md`
- Added automated test coverage under `tests/`
- Rewrote `static/description/index.html` with outcome-led copy
- Manifest: single-value `category`, `currency` set to `USD`

---

## [19.0.1.0.0] — Odoo 19 migration

### Added
- Migrated from Odoo 18 to Odoo 19

---

## [18.0.1.0.0] — Odoo 18 migration

### Added
- Migrated from Odoo 17 to Odoo 18
- Checklist categories with per-category group-based access control
- Restrict task completion until all checklist items are done/cancelled

---

## [17.0.1.0.0] — Odoo 17 migration

### Added
- Migrated from Odoo 16 to Odoo 17

---

## [16.0.1.0.0] — Initial release

### Added
- Task-based checklists with a 4-state item workflow (todo / in progress / done / cancel)
- Category-based predefined checklist templates
- Project-level checklist mirroring the task-level feature
- Dynamic progress bar on task and project views
