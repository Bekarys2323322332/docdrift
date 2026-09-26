---
description: Run DocDrift end to end on a repository - audit the docs, choose fixes, fix on a branch
argument-hint: "<github-url-or-local-folder> [doc-files]"
---
Run the full DocDrift pipeline using the docdrift-pipeline skill.

Repository: $1
Doc files to audit: $2 (if empty, auto-detect the README and other docs)

If you are not already in the DocDrift Pilot mode, switch to the docdrift-pilot mode first.
Ask me before changing any files and before committing. Never push.
