# ptc-022-bug-checklist-link-command-crash — Bug: checklist_id permission helper crashes on LINK commands

## Metadata
- **ID**: ptc-022
- **Type**: bug
- **Status**: planning
- **Complexity**: (filled at specification stage)
- **Created**: 2026-10-27

---

## Planning

### Description
Found by the ptc-021 migration review (finding M3). It is a pre-existing bug, also present on 19.0.
`_extract_checklist_ids()` (`models/task_checklist.py`, mirrored in `models/project_checklist.py`) only
normalizes a `[(6, 0, ids)]` command. For any other command shape, the fallback returns the raw command list.
That list goes to `browse()`, so `[Command.link(id)]` (`[(4, id, 0)]`) produces
`SELECT ... WHERE id IN ((4, 5, 0))` and a PostgreSQL error.
The web client's `many2many_tags` saves with LINK/UNLINK commands (`web/.../static_list.js`, 19 and 20).
So adding a checklist to a task or project from the form most likely fails, and the SEC-003/SEC-004 category checks never
evaluate UI input. Behaviour is fail-closed (an error, not a permission bypass).

Reproduced on Odoo 20 (ORM level, 2026-10-27): `project.task.with_user(<project manager>).create({..., 'checklist_id': [Command.link(cl.id)]})`
→ `psycopg2` "operator does not exist: integer = record". The form-level reproduction is still to be confirmed in the UI.

### Goal
Category permission checks work for every Many2many command the client or RPC can send, and the form saves normally.

### Objectives
- Normalize LINK (4), SET (6), CREATE (0) and plain ids into the checked id list; ignore UNLINK (3) and CLEAR (5)
- Apply the fix on both task and project sides (dual-symmetry rule)
- Add tests that write `Command.link` / `Command.set` as a non-admin, for allowed and restricted categories

### Deliverables
- Fixed `_extract_checklist_ids` (task + project)
- New tests in `tests/test_task_checklist.py` / `tests/test_project_checklist.py`
- `documents/security-rules.md` SEC-003 cross-reference, if the fix changes the rule's guidance

### Related observations from the same review (separate tasks to decide)
- `check_user_permission()` assumes a singleton ("Expected singleton" on multi-record writes), and blocks non-admins when the category has no `group_permission`.
- `copy()` reads `self.checklist_id` on a recordset. When a project is duplicated, its tasks are copied in one batch, so each copied task gets the union of all tasks' checklists.
