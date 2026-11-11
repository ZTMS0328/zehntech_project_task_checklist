# PTC — Task Index

| ID | Type | Title | Status | Complexity | Updated |
|----|------|-------|--------|------------|---------|
| ptc-001 | task | Code Quality Audit Fixes — umbrella (superseded by ptc-002..ptc-020, split per ticket) | done | HIGH | 2026-07-09 |
| ptc-002 | bug | ACL no group restriction (#116595) | done | MEDIUM | 2026-07-09 |
| ptc-003 | bug | State bypass via direct ORM write() (#116596) | done | EASY | 2026-07-09 |
| ptc-004 | bug | create() validates only first checklist ID (#116597) | done | EASY | 2026-07-09 |
| ptc-005 | bug | check_user_permission() AttributeError crash (#116599) | done | EASY | 2026-07-09 |
| ptc-006 | bug | checklist.category SQL constraint broken on Odoo 19 (not a Flux ticket) | done | EASY | 2026-07-09 |
| ptc-007 | bug | create() crashes under Odoo 19 batch-create API (not a Flux ticket) | done | MEDIUM | 2026-07-09 |
| ptc-008 | bug | write() validates current checklist, not incoming vals (#116598) | done | EASY | 2026-07-09 |
| ptc-009 | bug | project.checklist.project_id wrong comodel (#116600) | done | EASY | 2026-07-09 |
| ptc-010 | bug | write() wrong @api.model decorator (#116601) | done | EASY | 2026-07-09 |
| ptc-011 | bug | Demo data loads on every install (#116602) | done | EASY | 2026-07-09 |
| ptc-012 | improvement | Missing @api.depends on progress compute (#116603) | done | EASY | 2026-07-09 |
| ptc-013 | improvement | N+1 queries + unbounded search (#116604, #116605) | done | MEDIUM | 2026-07-09 |
| ptc-014 | improvement | Missing _() translation wrap (#116606) | done | EASY | 2026-07-09 |
| ptc-015 | task | LICENSE file (#116607) | done | EASY | 2026-07-09 |
| ptc-016 | task | CHANGELOG file (#116608) | done | EASY | 2026-07-09 |
| ptc-017 | task | Manifest category/currency (#116612) | done | EASY | 2026-07-09 |
| ptc-018 | task | File headers on 4 model files (#116611) | done | EASY | 2026-07-09 |
| ptc-019 | task | Automated tests (#116609) | done | MEDIUM | 2026-07-09 |
| ptc-020 | task | index.html Springboard rewrite (#116610) | done | MEDIUM | 2026-07-09 |
| ptc-021 | task | Migrate module from Odoo 19.0 to Odoo 20.0 | specification | MEDIUM | 2026-10-27 |
| ptc-022 | bug | checklist_id permission helper crashes on LINK commands (pre-existing, from ptc-021 review) | planning | — | 2026-10-27 |

---

## Changelog

| Timestamp | Task ID | Changed By | Change |
|-----------|---------|------------|--------|
| 2026-06-30 00:00 | — | Mayank Sisodiya | SDD framework initialized — backlog, CLAUDE.md, RELEASE_NOTES.md, and security-rules.md created |
| 2026-07-09 00:00 | ptc-001 | Mayank Sisodiya | Created task — 18 audit tickets (#116595-#116612) fetched from Redmine Flux, moved to planning |
| 2026-07-09 00:00 | ptc-001 | Mayank Sisodiya | Specification complete — complexity: HIGH, 18 fixes mapped to code changes and test cases |
| 2026-07-09 12:00 | ptc-001 | Mayank Sisodiya | Split into 19 individual per-ticket tasks (ptc-002..ptc-020) per instruction — each with its own planning/specification/test cases, moved to done as its commit landed |
| 2026-07-09 12:00 | ptc-002..ptc-020 | Mayank Sisodiya | All 19 tasks (18 audit tickets + 1 combined N+1/unbounded-search pair) fixed, verified live against a local Odoo 19 instance, committed one ticket per commit on code_quality_improvements, moved to done |
| 2026-07-09 12:00 | ptc-006, ptc-007 | Mayank Sisodiya | 2 additional Odoo 19 compatibility bugs discovered during pre-commit verification (checklist.category SQL constraint, create() batch-API signature) — fixed directly, not filed as new Flux tickets per instruction |
| 2026-07-09 12:00 | — | Mayank Sisodiya | Final verification pass: fresh install with/without demo (0 errors both), full automated test suite (22/22 passing) |
| 2026-10-27 12:49 | ptc-021 | Mayank Sisodiya | Created task — Odoo 19→20 migration, scan baseline effort 73.5 (5 errors, 24 silent), moved to planning |
| 2026-10-27 12:50 | ptc-021 | Mayank Sisodiya | Specification complete — complexity: MEDIUM, moved to specification |
| 2026-10-27 13:42 | ptc-021 | Mayank Sisodiya | All 13 test cases passed on Odoo 20 (install with/without demo, 22/22 suite, access + UI checks, scan 0 hits, review clean) — left uncommitted on 20.0-migration for review; stays in specification until the PR is raised |
| 2026-10-27 13:42 | ptc-022 | Mayank Sisodiya | Created task — pre-existing LINK-command crash in checklist_id permission helper (ptc-021 review M3), moved to planning |
