---
name: docdrift-fix
description: Fix only - apply chosen findings from an existing DRIFT_REPORT to the docs
metadata:
  user-invocable: true
  disable-model-invocation: true
  argument-hint: '<target-folder> <finding-IDs or all> [decisions]'
---

Switch to the docs-fixer mode if you are not already in it, then use the docs-drift-fix skill.

Target folder: $1
Findings to fix: $2
My decisions, if any: $3

Change documentation only. List anything that needs a code change under "Needs a human decision".
