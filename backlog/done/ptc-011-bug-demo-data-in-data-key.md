# ptc-011 — Bug: Demo data loads on every production install (#116602)

## Metadata
- **ID**: ptc-011
- **Type**: bug
- **Status**: done
- **Complexity**: EASY
- **Created**: 2026-07-09
- **Redmine**: #116602 (High)

---

## Planning

### Description
`__manifest__.py`'s `data` key included `"data/checklist_demo_data.xml"`, so sample categories/checklists loaded on every install regardless of whether the user wanted demo data.

### Goal
Only load sample data when demo is explicitly requested.

### Deliverables
- `__manifest__.py` — moved the file to a new `demo` key

---

## Specification

### Complexity Score: EASY
### Code Changes Required
| File | Action | Description |
|------|--------|--------------|
| `__manifest__.py` | modify | move `data/checklist_demo_data.xml` from `data` to `demo` |

---

## Test Cases
| # | Test Name | Steps | Expected Result | Status |
|---|-----------|-------|-------------------|--------|
| 1 | No demo by default | Fresh install (server's default `--without-demo` behavior) | 0 checklist categories | pass |
| 2 | Demo with --with-demo | Fresh install with `--with-demo` | 10 sample checklist categories | pass |

---

## Done

### Test Results
Verified live on two fresh test databases: default install (no demo) → 0 `checklist.category` records; `--with-demo` install → 10 sample records. Confirms the manifest key move works correctly in both directions.

### Summary
Demo data now only loads when explicitly requested, not on every production install.

### Commit / PR
Committed as `#116602: Demo data loads on every production install — move checklist_demo_data.xml to the demo manifest key`
