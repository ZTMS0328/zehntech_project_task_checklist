# CLAUDE.md — zehntech_project_task_checklist

## Project Overview
- **Module Name**: Checklist for Projects and Tasks
- **Technical Name**: `zehntech_project_task_checklist`
- **Version**: 20.0.1.1.0
- **Author**: Zehntech Technologies Inc.
- **License**: OPL-1
- **Odoo Version**: 20
- **Description**: Attaches multiple customizable checklists to Odoo projects and tasks, with a 4-state item workflow (todo → in_progress → done / cancel) and a dynamic progress bar. Checklists are organized by category, access is controlled per category via user groups, and task stages can be configured to block completion until all checklist items are done or cancelled.

---

## Architecture

```
zehntech_project_task_checklist/
├── models/         ← Python models: checklist categories, task & project checklists, item lines, stage restriction
├── views/          ← XML views, menus and actions for categories, task/project checklists, and form inheritance
├── security/       ← ir.access.csv (Odoo 20: CRUD permissions + item-line assignee/member domain scoping)
├── data/           ← Demo data: sample categories and checklists (loaded only when demo is enabled)
├── tests/          ← Automated tests (TransactionCase) for both task- and project-side models
├── static/
│   ├── description/ ← App store assets (banner, icon, index.html, images)
│   └── src/css/     ← style.css (button + progress bar styling)
├── i18n/           ← Translations: de, es, fr, ja_JP
├── LICENSE         ← OPL-1 license text
└── CHANGELOG.md    ← Version history
```

---

## Key Files

| File | Purpose |
|------|---------|
| `__manifest__.py` | Module manifest — depends on `project`, lists data/view files and CSS asset |
| `models/checklist_category.py` | `checklist.category` model — groups checklists, ties access to a user group |
| `models/task_checklist.py` | Task-side models: `task.checklist`, `checklist.item`, `checklist.item.line`, and `project.task` extension |
| `models/project_checklist.py` | Project-side mirror models: `project.checklist`, `project.checklist.item`, `project.checklist.item.line`, and `project.project` extension |
| `models/task_stage_restriction.py` | `project.task.type` extension — adds `restrict_task_completion` |
| `views/checklist_category_views.xml` | Category list/form/action/menu |
| `views/task_menu_action_views.xml` | `task.checklist` + `checklist.item` views, actions, root "Checklist" menu |
| `views/project_menu_action_views.xml` | `project.checklist` + `project.checklist.item` views, actions, menu |
| `views/checklist_add_task.xml` | Inherits `project.task` form/tree/kanban — adds Checklist page + progress bar |
| `views/checklist_add_project.xml` | Inherits `project.project` form/tree/kanban — adds Checklist page + progress bar |
| `views/task_stage_restriction.xml` | Inherits `project.task.type` form — adds `restrict_task_completion` toggle |
| `data/checklist_demo_data.xml` | Demo categories + sample task/project checklists (manifest `demo` key, not `data`) |
| `security/ir.access.csv` | All access (replaces `ir.model.access.csv` + `checklist_security.xml` in 20): CRUD for `project.group_project_user` on 7 models; item-line rows carry the assignee/member `domain`, with an empty-domain row only for `project.group_project_manager` |
| `tests/test_task_checklist.py` | Task-side coverage: creation, state cycle, direct-write bypass, progress bar, stage restriction, category permission on create()/write() |
| `tests/test_project_checklist.py` | Project-side mirror of the above |
| `static/src/css/style.css` | Styling for action buttons (cancel/success/in-progress/reset) and progress bar |
| `LICENSE` | OPL-1 license text |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |

---

## Data Models

| Model | Extended/New | Key Fields | Purpose |
|-------|-------------|------------|---------|
| `checklist.category` | new | `name`, `description`, `group_permission` (M2o res.groups) | Categorizes checklists; `group_permission` gates who can act on items in the category |
| `task.checklist` | new | `name`, `checklist_category`, `checklist_ids` (O2m → checklist.item), `task_ids` (M2o project.task), `project_id` (M2o project.project) | A named checklist template for tasks |
| `checklist.item` | new | `name`, `sequence`, `description`, `checklist_id` (M2o task.checklist) | A line item belonging to a task checklist |
| `checklist.item.line` | new | `check_list_item_id`, `projects_id` (M2o project.task), `checklist_id`, `state` (todo/in_progress/done/cancel) | Per-task instance of a checklist item with workflow state |
| `project.task` | extended | `checklist_id` (M2m), `checklists` (O2m line), `checklist_progress`, `has_checklist`, `checklist_category`, `category_domain`, `checklist_domain` | Adds checklist tracking + progress to tasks |
| `project.checklist` | new | `name`, `checklist_category`, `checklist_ids` (O2m → project.checklist.item), `task_ids` (M2o project.task), `project_id` (M2o project.project) | Project-side mirror of `task.checklist` |
| `project.checklist.item` | new | `name`, `sequence`, `description`, `checklist_id` (M2o project.checklist) | Project-side mirror of `checklist.item` |
| `project.checklist.item.line` | new | `check_list_item_id`, `projects_id` (M2o project.project), `checklist_id`, `state` | Project-side mirror of `checklist.item.line` |
| `project.project` | extended | `checklist_id` (M2m), `checklists` (O2m line), `checklist_progress`, `has_checklist`, `checklist_category`, `category_domain`, `checklist_domain` | Adds checklist tracking + progress to projects |
| `project.task.type` | extended | `restrict_task_completion` (Boolean) | When set on a stage, blocks tasks from entering it until all checklist items are done/cancelled |

---

## Feature Flags

| Config Field | Feature | Default |
|-------------|---------|---------|
| `project.task.type.restrict_task_completion` | Per-stage gate: task cannot move to this stage until all checklist items are done/cancelled | False |
| `checklist.category.group_permission` | Access control: only members of this group may change item states in the category (enforced by `check_user_permission()`) | empty (no restriction) |

> Note: access is granted to `project.group_project_user` in `security/ir.access.csv`. `checklist.item.line` / `project.checklist.item.line` rows carry a `domain` limiting them to the task/project's assignees/members, with an unrestricted `project.group_project_manager` row. Category-level authorization is enforced by `check_user_permission()` against `group_permission`, called from both button methods and `write()` (never rely on button methods alone — see Development Rules).

---

## Development Rules

Module-specific conventions (extend the global Zehntech SDD rules):
1. **Dual task/project symmetry** — task-side models (`task.checklist`, `checklist.item`, `checklist.item.line`, `project.task` ext) have project-side mirrors (`project.checklist`, `project.checklist.item`, `project.checklist.item.line`, `project.project` ext). A change to one side almost always needs the mirror change on the other.
2. **Gate every state change in `write()`, not just in button methods** — `checklist.item.line` / `project.checklist.item.line` override `write()` to call `check_user_permission()` whenever `'state'` is in `vals`. The button methods (`approve_and_next` / `mark_completed` / `mark_canceled` / `reset_stage`) keep their own explicit calls as defense in depth, but the `write()` override is the authoritative server-side gate — a check that lives only in a button method is bypassable via direct ORM/RPC calls.
3. **Validate the full Many2many command, both directions** — `ChecklistProgress`/`ProjectChecklistProgress`'s `_check_checklist_category_permission()` helper must be called with *every* id in a `checklist_id` M2M command (never just `ids[0]`), from both `create()` (on `vals`) and `write()` (on incoming `vals`, not just the record's current value).
4. **`create()` must use `@api.model_create_multi` with a `vals_list` parameter, never plain `@api.model` with a singular `vals`** — Odoo 19's `api.model` decorator auto-wraps any method literally named `create` with `model_create_multi`, which always passes a list. A `def create(self, vals):` override will crash with `AttributeError: 'list' object has no attribute 'get'` on every call. `write()` does not have this issue — keep `write()` undecorated (no `@api.model`), since it always operates on a real recordset.
5. **Don't add `from . import tests` to the root `__init__.py`** — Odoo's test loader auto-discovers each module's `tests/` package when running in test mode; explicitly importing it causes the test framework to load on every normal (non-test) install too.
6. **Never create a new module** — extend this one.
7. **Field/method conventions**: `checklist_*` field prefix; `*_id` / `*_ids` for relations; `_compute_*` for computed fields; `_onchange_*` for onchange handlers; `_check_*` for `@api.constrains` validators.
8. **State workflow**: item `state` uses `todo` → `in_progress` → `done`, or `cancel`. Progress = done / (total − cancelled). Keep this denominator rule when touching `_compute_checklist_progress`, and keep its `@api.depends('checklists', 'checklists.state')` — without it the progress bar won't recompute on state change.
9. **Odoo 20 `ir.access` rows are OR-ed per group** — never add an empty-domain `project.group_project_user` row for `checklist.item.line` / `project.checklist.item.line`; it silently grants every project user all lines (SEC-005).
10. **Kanban progress bar inherits the card views** — `project.view_task_card` / `project.view_project_card`, not `view_task_kanban` / `view_project_kanban` (20 moved the card body out of the kanban view).
11. **Button icons are Material Symbol names** (`schedule`, `check`, `close`, `refresh`), never `fa-*` (renders blank in 20), and every icon-only `<button>` needs a `title`. Check a new name actually renders (the bundled font is a subset).
12. **Every model needs a `_description`** — Odoo 20 logs a warning without one. Keep `model:ir.model,name` .po references on the matching msgid.

---

## Project Management

- **Project Key**: `ptc` (used in task IDs, e.g. `ptc-001-feature-...`)
- **Task Index**: `backlog/TODO.md`
- **Security Rules**: `documents/security-rules.md`
- **Release Notes**: `RELEASE_NOTES.md`
