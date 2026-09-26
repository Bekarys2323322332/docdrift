---
description: Audit only - check a folder's docs against its code and write DRIFT_REPORT.md and .json
argument-hint: "[target-folder] [doc-files]"
---
Switch to the docs-auditor mode if you are not already in it, then use the docs-drift-check skill.

Target folder: $1 (if empty, the workspace root)
Doc files: $2 (if empty, auto-detect)

Check the categories in parallel with explore subagents and write DRIFT_REPORT.md and
DRIFT_REPORT.json in the target folder.
