# ptc-002 — Bug: All 7 ACL rules have no group restriction (#116595)

## Metadata
- **ID**: ptc-002
- **Type**: bug
- **Status**: done
- **Complexity**: MEDIUM
- **Created**: 2026-07-09
- **Redmine**: #116595 (Blocker)

---

## Planning

### Description
All 7 rows in `security/ir.model.access.csv` had a blank `group_id:id`, granting full CRUD on every checklist model to any internal user. Odoo flags this pattern as deprecated at install time.

### Goal
Restrict checklist ACLs to project users, and add record-level scoping so regular project users only see item lines on their own tasks/projects, without locking out project managers/admins.

### Objectives
- Set `group_id:id` on all 7 ACL rows to `project.group_project_user`
- Add `ir.rule` scoping `checklist.item.line` / `project.checklist.item.line` to assignees, with a manager bypass

### Deliverables
- Updated `security/ir.model.access.csv`
- New `security/checklist_security.xml`
- `__manifest__.py` registers the new security file

---

## Specification

### Complexity Score: MEDIUM
### Complexity Rationale
Touches only security/manifest files, but is security-sensitive and needs a bypass rule to avoid breaking manager access.

### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `security/ir.model.access.csv` | modify | group_id:id = project.group_project_user on all 7 rows |
| `security/checklist_security.xml` | create | ir.rule for item-line assignee scoping + manager bypass |
| `__manifest__.py` | modify | register new security XML |

### Implementation Notes
Manager/admin bypass rules use `domain_force = [(1,'=',1)]` scoped to `project.group_project_manager` so managers keep full access.

---

## Test Cases

### Functional Tests
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | Non-project user denied | Log in as user without `project.group_project_user`, open Checklists | AccessError at ORM layer | pass |
| 2 | Project user unaffected | Log in as project user, use checklist features normally | Works as before | pass |

### Test Plan for QA Team
**Scope**: ACL group restriction for all 7 checklist models.
**QA Steps**: 1) As a non-project-group user, confirm checklist models are inaccessible. 2) As a project user, confirm normal checklist CRUD still works. 3) As a project manager, confirm full access to all item lines regardless of task assignment.
**Expected Outcomes**: No regression for permitted users; non-project users blocked at ORM layer.

---

## Done

### Test Results
Verified live against local Odoo 19 test DB (`ptc_audit_test`) via `odoo-bin shell`: install succeeds with 0 errors after the ACL/ir.rule change; project users retain access, non-project users are blocked.

### Summary
Scoped all 7 checklist ACLs to `project.group_project_user` and added `ir.rule` for item-line record scoping with a manager bypass.

### Commit / PR
`f04461d` — `#116595: ACL rules have no group restriction — scope all 7 checklist ACLs to project.group_project_user, add ir.rule for item-line assignee scoping`
