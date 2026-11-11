# Security & Critical Rules — zehntech_project_task_checklist

> Shared rule book for the Zehntech development team.
> Every security finding must be recorded here regardless of severity.
> Rules are never deleted — resolved issues are marked fixed.

---

## Rule Index

| Rule ID | Category | Severity | Status | Title |
|---------|----------|----------|--------|-------|
| SEC-001 | Access Control | HIGH | fixed | ACL rules must always specify a `group_id` |
| SEC-002 | Access Control | HIGH | fixed | State-change fields must be guarded in `write()`, not just in button methods |
| SEC-003 | Access Control | MEDIUM | fixed | Validate every id in a Many2many command, not just the first |
| SEC-004 | Access Control | MEDIUM | fixed | `write()` must validate incoming vals, not only the record's current value |
| SEC-005 | Access Control | HIGH | fixed | Odoo 20 `ir.access`: never add an empty-domain project-user row on item-line models |

---

## Rules

### SEC-001 — ACL rules must always specify a `group_id`

- **Category**: Access Control
- **Severity**: HIGH
- **Status**: fixed
- **Discovered**: 2026-07-08 (audit ticket #116595)
- **Fixed**: 2026-07-09
- **Related Task**: ptc-002
- **Affected File(s)**: `security/ir.model.access.csv`, `security/checklist_security.xml`

**The Rule**:
Every row in `ir.model.access.csv` must specify a `group_id:id` — a blank group grants that access line to every internal user, including ones who should never see the model.

**Why**:
All 7 checklist ACL rows had a blank `group_id:id`, giving full CRUD to any internal user regardless of whether they had anything to do with the Project app. Odoo itself flags this pattern as deprecated at install time.

**How to detect violations**:
`grep -n ',,' security/ir.model.access.csv` — a comma immediately followed by another comma in the `group_id:id` column position means the field is blank.

**Correct implementation**:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_task_checklist,access.task.checklist,model_task_checklist,project.group_project_user,1,1,1,1
```

**Fix applied**:
Set `group_id:id` to `project.group_project_user` on all 7 rows; added `security/checklist_security.xml` with `ir.rule` scoping `checklist.item.line` / `project.checklist.item.line` to task/project assignees, with an explicit `project.group_project_manager` bypass rule.

---

### SEC-002 — State-change fields must be guarded in `write()`, not just in button methods

- **Category**: Access Control
- **Severity**: HIGH
- **Status**: fixed
- **Discovered**: 2026-07-08 (audit ticket #116596)
- **Fixed**: 2026-07-09
- **Related Task**: ptc-003
- **Affected File(s)**: `models/task_checklist.py`, `models/project_checklist.py`

**The Rule**:
If a field's permission check lives only in a button method, a direct `write()` call (sudo, JSON-RPC, a different button, a script) bypasses it entirely — the check must also live in a `write()` override for that model.

**Why**:
`checklist.item.line.state` was `readonly=True` at the field level and permission-checked only inside `approve_and_next()` / `mark_completed()` / `mark_canceled()` / `reset_stage()`. A direct `env['checklist.item.line'].write({'state': 'done'})` skipped every check, and the stage-restriction logic trusts `item.state` to decide whether a task can advance — so this was also a workflow-integrity bypass, not just an authorization gap.

**How to detect violations**:
Any model where a `readonly` field is only mutated through dedicated action methods that call a permission check — search for the field name in `write()` overrides; if it's absent, the check is UI-only.

**Correct implementation**:
```python
def write(self, vals):
    if 'state' in vals:
        self.check_user_permission()
    return super().write(vals)
```

**Fix applied**:
Added the `write()` override above to both `checklist.item.line` and `project.checklist.item.line`. Button methods keep their existing explicit calls as defense in depth.

---

### SEC-003 — Validate every id in a Many2many command, not just the first

- **Category**: Access Control
- **Severity**: MEDIUM
- **Status**: fixed
- **Discovered**: 2026-07-08 (audit ticket #116597)
- **Fixed**: 2026-07-09
- **Related Task**: ptc-004
- **Affected File(s)**: `models/task_checklist.py`, `models/project_checklist.py`

**The Rule**:
When validating permissions against a Many2many field passed as a `(6, 0, [ids])` command, iterate over every id — checking only `ids[0]` lets every subsequent id skip validation entirely.

**Why**:
`create()` validated `checklist_ids[0]`'s category permission only; a task created with `checklist_id: [(6, 0, [allowed.id, restricted.id])]` persisted the restricted checklist unchecked as long as it wasn't listed first.

**How to detect violations**:
Search for `[0]` indexing immediately after extracting ids from an M2M command, followed by a permission check that isn't inside a loop over the full id list.

**Correct implementation**:
```python
for checklist in self.env['task.checklist'].browse(checklist_ids):
    category = checklist.checklist_category
    if category and category.group_permission:
        if not any(group in user_groups for group in category.group_permission):
            raise AccessError(...)
```

**Fix applied**:
Factored `_extract_checklist_ids()` / `_check_checklist_category_permission()` helpers that loop over every id, used by both `create()` and `write()`.

---

### SEC-004 — `write()` must validate incoming vals, not only the record's current value

- **Category**: Access Control
- **Severity**: MEDIUM
- **Status**: fixed
- **Discovered**: 2026-07-08 (audit ticket #116598)
- **Fixed**: 2026-07-09
- **Related Task**: ptc-008
- **Affected File(s)**: `models/task_checklist.py`, `models/project_checklist.py`

**The Rule**:
A permission check inside `write()` that only inspects the record's *current* field value, and never the *incoming* `vals`, doesn't actually gate the write it's supposed to gate.

**Why**:
`write()` checked `task.checklist_id.checklist_category` (the value before the write) but never inspected `vals.get('checklist_id')` (the value being written), so a non-permitted user could swap in a restricted checklist via `write()` without ever triggering a permission error.

**How to detect violations**:
Any `write()` override with a permission check — confirm it reads from `vals`, not exclusively from `self`/the pre-write record state, for every field the check is meant to protect.

**Correct implementation**:
```python
def write(self, vals):
    if 'checklist_id' in vals:
        self._check_checklist_category_permission(self._extract_checklist_ids(vals['checklist_id']))
    ...
    return super().write(vals)
```

**Fix applied**:
Reused the SEC-003 helper inside `write()`, gated on `'checklist_id' in vals`, in addition to the pre-existing current-value check.

---

### SEC-005 — Odoo 20 `ir.access`: never add an empty-domain project-user row on item-line models

- **Category**: Access Control
- **Severity**: HIGH
- **Status**: fixed
- **Discovered**: 2026-10-27 (Odoo 19 → 20 migration, architectural decision)
- **Fixed**: 2026-10-27
- **Related Task**: ptc-021
- **Affected File(s)**: `security/ir.access.csv` (replaces `security/ir.model.access.csv` + `security/checklist_security.xml`)

**The Rule**:
On `checklist.item.line` and `project.checklist.item.line`, the only `project.group_project_user` rows in `ir.access.csv` must carry the assignee/member `domain`; an empty-domain row is allowed only for `project.group_project_manager`.

**Why**:
Odoo 20 merged `ir.model.access` and `ir.rule` into one `ir.access` model. Rows for the groups a user belongs to are OR-ed together, so a single extra `project.group_project_user,crud,` row with no domain would silently grant every project user all item lines — undoing SEC-001's assignee scoping without any error or failing install.

**How to detect violations**:
`grep -nE "item\.line,project\.group_project_user,[a-z]+,$" security/ir.access.csv` — any hit is an unscoped project-user row on an item-line model.

**Correct implementation**:
```csv
id,name,model_id,group_id/id,operation,domain
checklist_item_line_rule_assignee,Checklist Item Line: task assignees only,checklist.item.line,project.group_project_user,crud,"[('projects_id.user_ids', 'in', [user.id])]"
checklist_item_line_rule_manager,Checklist Item Line: project managers full access,checklist.item.line,project.group_project_manager,crud,
```

**Fix applied**:
`security/ir.access.csv` generated by Odoo's official `19.4-00-ir-access` upgrade script and reviewed: 9 rows, item-line rows domain-scoped for project users, unrestricted for managers. Verified on Odoo 20 with `with_user` checks (user sees only assigned task / own project lines; manager sees all).
