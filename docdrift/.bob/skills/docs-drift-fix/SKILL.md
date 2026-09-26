---
name: docs-drift-fix
description: Apply the fixes listed in DRIFT_REPORT.md to the documentation files, changing only the lines with confirmed drift. Use after a docs-drift-check audit when asked to fix the docs.
---

# DocDrift: fix the docs

<Steps>
<Step>
**Find the target and the report.** The target folder is the folder you were given
(for example `audits/flask-realworld-example-app`), or the workspace root if none was given.
Read `DRIFT_REPORT.md` in that folder (and `DRIFT_REPORT.json` if it exists). If there is
no report, stop and say the audit has to run first.
</Step>

<Step>
**Decide what to fix.** If you were given a list of finding IDs (for example D1 D3 D4),
fix only those. If you were given "all", fix every DRIFT finding. Skip OK and UNVERIFIED
items. Also follow any decisions the user stated (for example "the README is right, the
file is missing").
</Step>

<Step>
For each finding to fix, open the doc file at the cited line and apply the suggested fix.
Make the smallest possible change. Keep the original wording, formatting and tone everywhere
else. If the cited line does not contain the quoted text, search the file for the quote and
fix it where it actually is.
</Step>

<Step>
For findings where the docs are missing something (for example a required
environment variable), add it to the most relevant existing section rather than
creating a new section.
</Step>

<Step>
If a finding says the docs point to a missing `.env.example` file, create `.env.example`
using the "Undocumented settings" table from the report plus any variables the docs
already mention. For each variable write its name, a short comment explaining it, and
either the default value from the code or a safe placeholder such as
`your-api-key-here`. Never copy values from the real `.env` file and never write real
secrets or passwords.
</Step>

<Step>
Never edit source code, config files or scripts. The code is the source of truth.
If a finding can only be solved by changing code (for example the docs describe the
intended behaviour and the code is wrong), do not change the code: list it in a
"Needs a human decision" section of your summary and explain the two options.
</Step>

<Step>
**Finish** with a short table: finding ID, file:line changed, and a one-line
description of the change, followed by any "Needs a human decision" items.
If you were started as a subtask, return this as your result so the Pilot can use it.
Otherwise suggest committing with a message such as
"docs: fix N drift issues found by DocDrift".
</Step>
</Steps>
