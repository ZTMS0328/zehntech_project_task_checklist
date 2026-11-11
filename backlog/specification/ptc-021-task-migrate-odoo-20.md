# ptc-021-task-migrate-odoo-20 — Migrate module from Odoo 19.0 to Odoo 20.0

## Metadata
- **ID**: ptc-021
- **Type**: task
- **Status**: specification
- **Complexity**: MEDIUM
- **Created**: 2026-10-27

---

## Planning

### Description
Port `zehntech_project_task_checklist` (19.0.1.1.0) to Odoo 20.0 Community. The v19 baseline is
commit `6ecee36` on `main` of `zehntech/zehntech_project_task_checklist_v20`; the migration lives on
branch `20.0-migration`, left uncommitted for review.

### Goal
The module installs and passes its full test suite on Odoo 20.0, and its behaviour and access control
are the same as on 19.

### Objectives
- Convert `ir.model.access` + `ir.rule` security to the new `ir.access` model without widening access
- Fix the button icons that silently render blank in 20 (FontAwesome removed)
- Bump the version to 20.0.1.1.0 and update the version references in the manifest and description

### Deliverables
- `security/ir.access.csv` replacing `security/ir.model.access.csv` + `security/checklist_security.xml`
- Updated views, manifest, docs (CLAUDE.md, RELEASE_NOTES.md, CHANGELOG.md, security-rules.md)
- Clean install + passing tests on an Odoo 20 throwaway DB

---

## Specification

### Complexity Score: MEDIUM

### Complexity Rationale
Few files, but the security conversion has real access-control impact (4 record rules with assignee
domains), and the icon break is silent: no error, so it isn't caught by tests. No Python/JS changes are expected
(the scanner found 0 hits outside security, views and manifest).

### Scan Baseline (odoo_scan.py, 2026-10-27)
Effort 73.5 · 5 errors (SEC-001/001b) · 24 silent warnings (VIEW-007/008, 12 buttons) · 1 info (MAN-VERSION).

### Code Changes Required
| File | Action | Description |
|------|--------|-------------|
| `security/ir.model.access.csv` | delete | Replaced by `ir.access.csv` (official script `19.4-00-ir-access`) |
| `security/checklist_security.xml` | delete | 4 `ir.rule` records folded into `ir.access.csv` |
| `security/ir.access.csv` | create | One row per model/group/operation; item-line rows keep the assignee/member domains |
| `__manifest__.py` | modify | Version 20.0.1.1.0, data list, description / live_test_url text |
| `views/checklist_add_task.xml` | modify | Button `icon="fa-*"` → Material Symbol names |
| `views/checklist_add_project.xml` | modify | Same, 8 buttons |
| `README.rst`, `static/description/index.html` | modify | Odoo 19 → 20 references, where present |
| `views/checklist_add_task.xml` | modify | *(found in install loop)* Kanban progress bar now inherits `project.view_task_card` after `tag_ids`. 20 moved the card body out of `view_task_kanban`, so the `date_deadline` anchor no longer exists there |
| `views/checklist_add_project.xml` | modify | *(found in install loop)* Kanban progress bar now inherits `project.view_project_card`, which holds `main.o_project_kanban_main` in 20 |
| `views/checklist_add_*.xml` + `i18n/*.po` | modify | *(found in install loop)* `title` on the 8 icon-only buttons (20 warns without one); reuses the already-translated state labels and adds view references in the .po files |
| `models/*.py` (3 files) | modify | *(found in install loop)* `_description` on `task.checklist`, `project.checklist`, `checklist.category`; this warning is new in 20 |
| `i18n/*.po` | modify | *(review L2)* `model:ir.model,name` references moved to the new `_description` msgids |

### Implementation Notes
- Run the official scripts via `run_upgrade_code.py` in a scratchpad work copy, then copy the result onto
  branch `20.0-migration`. **No commits in the repo** (the user reviews and commits).
- Icon mapping: `fa-clock-o`→`schedule`, `fa-check`→`check`, `fa-times`→`close`, `fa-refresh`→`refresh`.
  Each name must exist in the bundled Material Symbols subset, which a visual check confirms.
- Access semantics to preserve: `project.group_project_user` gets CRUD on item lines only where the domain matches
  (task assignee / project manager-or-follower), and `project.group_project_manager` gets CRUD on all lines. There must be **no** empty-domain
  `group_project_user` row on the two item-line models.

---

## Test Cases

### Unit Tests
| # | Test Name | Input / Condition | Expected Result | Status |
|---|-----------|-------------------|-----------------|--------|
| 1 | Existing suite (`tests/test_task_checklist.py`, `tests/test_project_checklist.py`) | `odoo_try_install.py --test` on Odoo 20 | All 22 tests pass | pass |
| 2 | Access: assignee scope (task) | Non-manager project user, item lines on an assigned task and on an unassigned task | Sees only the assigned task's lines | pass |
| 3 | Access: manager bypass | Project manager | Sees all item lines | pass |
| 4 | Access: project member scope | Non-manager user, project they don't manage/follow | Project item lines hidden | pass |

### Functional Tests
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 1 | Install without demo | Fresh 20 DB, install module | `result=OK`, no module warnings | pass |
| 2 | Install with demo | Fresh 20 DB with demo | `result=OK`, demo checklists load | pass |
| 3 | Task checklist buttons | Open a task → Checklist page | 4 row buttons show icons and work | pass |
| 4 | Project checklist buttons | Open a project → Checklist page | 4 row buttons show icons and work | pass |
| 5 | Progress bar | Task/project form, list, kanban | Progress bar renders and updates on state change | pass |
| 6 | Stage restriction | Stage form toggle; move task with open items to the stage | Toggle visible; move blocked | pass |

### Edge Cases
| # | Scenario | Expected Behaviour | Status |
|---|----------|--------------------|--------|
| 1 | Final scan | 0 errors, 0 VIEW-007/008 hits | pass |
| 2 | Upgrade-script warnings in `logs/ir-access.log` | Each reviewed and resolved | pass |
| 3 | Inherited view xpaths against 20 core views | All resolve (install succeeds) | pass |

### Test Plan for QA Team
> This section is copied verbatim into the PR description.

**Scope**: Odoo 20.0 port of Checklist for Projects and Tasks: security conversion, button icons, version bump.

**Pre-conditions**:
- Odoo 20.0 Community database with `project` installed
- Users: one Project Manager, one Project User (not manager)

**QA Steps**:
1. Install the module (with and without demo data).
2. As Project Manager, open a task → Checklist tab, add a checklist and use all 4 row buttons (in progress, done, cancel, reset).
3. Repeat on a project → Checklist tab.
4. Check the progress bar on task/project form, list and kanban views.
5. On a task stage, enable "Restrict task completion"; try to move a task with open items into it.
6. As Project User, open a task you are NOT assigned to and confirm its checklist lines are not visible; open one you are assigned to and confirm they are.

**Expected Outcomes**:
- Module installs cleanly; all 4 buttons display icons and change state
- Progress bar updates; stage restriction blocks the move
- Project Users only see checklist lines of their own tasks/projects; managers see all

**Out of Scope**:
- Enterprise-only views (not available for 20 yet)
- Data migration of an existing 19 database (module port only)

---

## Done

### Test Results
- All 13 test cases passed ✓ (Odoo 20.0 Community, throwaway DBs, 2026-10-27)
- Install without demo: `result=OK`, 0 module warnings. Install with demo + `--test`: 0 failed / 0 errors.
- Existing suite: 22/22 test methods pass. Temporary verification tests (scratchpad only, not added to the module):
  - 4 access-scope checks (`with_user`). Project user sees only lines of assigned tasks / own projects; manager sees all.
  - 4 headless-Chrome UI checks. All 8 buttons render a 14px Material glyph with a tooltip (In Progress / Done / Cancelled / To Do). The progress bar renders in the task card (50 %) and the project card.
- Final `odoo_scan.py`: 0 errors, 0 warnings, 0 silent hits (baseline: effort 73.5, 5 errors, 24 silent).
- `odoo-migration-reviewer`: no CRITICAL/HIGH. Access on a fresh install is verified equivalent to 19.
- Known environment noise, not the module: Odoo's filestore GC logs `PermissionError [WinError 5]` on Windows during test runs.

### Summary
- Security: the official `19.4-00-ir-access` script converted 7 ACLs + 4 `ir.rule` into 9 `ir.access` rows with identical effective access.
- Views: Material Symbols button icons with titles; kanban progress bar moved to the 20 card views.
- Models: `_description` on 3 models. i18n: references updated in all 4 languages. Version 20.0.1.1.0.

### Open follow-ups (from review, not blocking a fresh install)
- **M1 (upgrading an existing 19 DB only, unverified):** after the upgrade, check that each item-line model has exactly 2 active `ir.access` rows (project user with domain, manager without). Optionally add an `end-migrate` guard.
- **M2 (upgrading an existing 19 DB only, unverified):** check that the 2 kanban/card inherited views stay `active` after the upgrade. Reactivate them if the upgrade service disabled them.
- **L1:** upgraded DBs may keep `noupdate=True` on the 4 former rule xmlids.
- **L3:** the unused `<field name="checklist_id" invisible="1"/>` in both cards could be dropped (pre-existing).
- **M3 → ptc-022** (pre-existing 19 bug, confirmed at ORM level): `_extract_checklist_ids` only handles `(6, 0, ids)`. `Command.link` crashes with a SQL error (fails closed).

### Commit / PR
Uncommitted on branch `20.0-migration` — the user reviews and commits.
