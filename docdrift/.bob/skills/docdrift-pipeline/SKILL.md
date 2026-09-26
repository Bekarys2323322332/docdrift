---
name: docdrift-pipeline
description: Run the full DocDrift pipeline on a repository from start to finish - clone it into audits/, check its licence, delegate the audit to Docs Auditor, ask the user which findings to fix, delegate the fixes to Docs Fixer on a new branch, and commit only with approval. Use for the /docdrift command or when asked to run DocDrift end to end.
---

# DocDrift Pilot: end-to-end pipeline

You coordinate. You never audit or edit documentation yourself: the Docs Auditor and
Docs Fixer modes do that work as subtasks. Keep the user in control: ask before any
change to their files and before any commit. Never push to a remote.

Use terminal commands that work in the user's shell. `git` commands work everywhere.
For copying files use `Copy-Item` on Windows PowerShell or `cp` on macOS/Linux.
Git commands must never wait for input, or the task hangs:
- always write `git --no-pager ...` for commands that print (status, diff, log, show),
- always commit with `-m "<message>"` so no editor opens,
- if a commit fails because git has no user name or email, stop and tell the user to run
  `git config --global user.name "Their Name"` and `git config --global user.email "their@email"`,
- if git says `index.lock` exists, tell the user a previous git command was interrupted and
  ask before deleting that lock file.

<Steps>
<Step>
**Understand the request.** The user gives one of:
- a Git URL (for example https://github.com/owner/repo), or
- a local folder path on their computer that is a Git repository, or
- a folder that already exists inside `audits/`.
They may also name the doc files to audit. If nothing is given, ask which repository to audit.
Set `name` to the last part of the URL or path, without `.git`.
Set the target folder to `audits/<name>`.
</Step>

<Step>
**Prepare the repository.**
- If `audits/<name>` already exists, ask the user: reuse it, or delete it and clone fresh.
- For a URL: `git clone --depth 1 <url> audits/<name>`.
- For a local folder: `git clone "<path>" audits/<name>`. Tell the user this copies only
  committed files (uncommitted changes and ignored files such as `.env` are not copied,
  which also keeps secrets out of the audit).
Never run the project's own code, installers, scripts or tests.
</Step>

<Step>
**Get today's date.** Run `Get-Date -Format yyyy-MM-dd` (Windows PowerShell) or `date +%F`
(macOS/Linux) and remember the result as <today>. Never guess the date: it is used in the
report and in the report file name.
</Step>

<Step>
**Check the licence.** Look at LICENSE / LICENSE.md / COPYING, or the licence field in
package.json, pyproject.toml or setup.cfg. Permissive licences (MIT, Apache-2.0, BSD,
ISC, Unlicense) are fine. If the licence is missing or different, tell the user it may not
be allowed under the hackathon data rules and ask whether to continue. Skip this check for
a local folder the user owns, but still record the licence if there is one.
</Step>

<Step>
**Delegate the audit.** Start a subtask in the `docs-auditor` mode with this message:
"Use the docs-drift-check skill. Target folder: audits/<name>. Source: <url or path>.
Doc files: <files, or 'auto-detect'>. Today's date: <today>. Write DRIFT_REPORT.md and
DRIFT_REPORT.json in the target folder and return the summary."
If subtasks cannot be started in a specific mode, switch to `docs-auditor` yourself,
run the skill, then switch back to `docdrift-pilot`.
</Step>

<Step>
**Present the results.** Read `audits/<name>/DRIFT_REPORT.json`. Show the user:
the trust score, the licence, and a short table of findings (ID, severity, category,
one-line summary). Keep it brief; the full details are in the report and the dashboard.
If there are no DRIFT findings, say so, skip to the last step, and do not create a branch.
</Step>

<Step>
**Ask what to fix.** Ask the user one question with these choices:
1. Fix all findings
2. Fix HIGH and MEDIUM only
3. Let me choose finding IDs
4. Do not fix anything now
If a finding could mean either the docs or the code is wrong (for example the docs
describe a file that is missing), ask the user which is true before fixing it.
</Step>

<Step>
**Create a branch.** In the target folder run
`git -C audits/<name> checkout -b docdrift/fix-docs`.
If that branch already exists, add today's date to the name.
</Step>

<Step>
**Delegate the fix.** Start a subtask in the `docs-fixer` mode with this message:
"Use the docs-drift-fix skill. Target folder: audits/<name>. Fix these findings: <IDs or 'all'>.
User decisions: <any decisions, or 'none'>. Return the table of changes."
If subtasks cannot be started in a specific mode, switch to `docs-fixer` yourself, run the
skill, then switch back to `docdrift-pilot`.
</Step>

<Step>
**Review and commit with approval.** Run `git --no-pager -C audits/<name> status --short` and
`git --no-pager -C audits/<name> diff --stat` and show the result. Ask the user whether to commit.
Only if they say yes, add exactly the changed documentation files (and `.env.example` if
it was created), not the DRIFT_REPORT files, then commit with the message
"docs: fix <N> documentation drift issues found by DocDrift".
Never push. Tell the user they can push the branch or open a pull request themselves.
</Step>

<Step>
**Save the report for the dashboard.** Copy `audits/<name>/DRIFT_REPORT.json` to
`reports/<name>-<today>.json` (create `reports/` if needed). If a file with that name
exists, add `-2`, `-3` and so on.
Then update `reports/index.json`: a JSON array of the report file names in `reports/`
(newest first), for example `["microblog-api-2026-09-26.json", "flask-realworld-example-app-2026-09-26.json"]`.
Create it if it does not exist. The online dashboard uses this list to load reports.
</Step>

<Step>
**Finish** with a short summary: repository, licence, trust score, findings fixed,
branch name, and where the reports are. Remind the user to:
- open `dashboard/index.html` and load the file from `reports/`, and
- take the task summary screenshot for the `bob_sessions` folder.
</Step>
</Steps>
