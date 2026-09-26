---
name: docs-drift-check
description: Audit a repository's documentation (README, CONTRIBUTING, docs folder) against the actual code and list every statement that is no longer true, with file-and-line evidence. Writes DRIFT_REPORT.md and DRIFT_REPORT.json. Use when asked to check, audit or verify docs for drift or outdated content.
---

# DocDrift: documentation drift audit

Goal: find every place where the documentation says something the code no longer supports,
prove it with evidence, and write one clear report for humans (Markdown) and one for tools
(JSON, used by the DocDrift dashboard).

Keep costs low. Do not re-read files you have already read. Use read-only `explore`
subagents for checking (they run on a lighter model and cannot change files).

<Steps>
<Step>
**Find the target.** The target folder is the folder the user names (for example
`audits/flask-realworld-example-app`). If none is named, the target is the workspace root.
All paths in the report are written relative to the target folder.
Never audit the DocDrift tool's own files (`.bob/`, `dashboard/`, `benchmark/`, `bob_sessions/`)
unless the target folder is the workspace root and the user asked for it.
</Step>

<Step>
**Find the docs.** If the user named doc files, audit only those. Otherwise audit, in order:
README (any of README.md, README.rst, README.txt, README), CONTRIBUTING, other top-level
.md/.rst files, then a docs/ folder if it is small (at most 10 files; otherwise only the
README and CONTRIBUTING, and say so in the report). Skip CHANGELOG, LICENSE, auto-generated
API reference and anything in node_modules, vendor, venv, .venv, bin, obj, dist, build, .git.
</Step>

<Step>
**Record the licence.** Read the LICENSE file (or the "license" field of package.json,
pyproject.toml or setup.cfg) and record the licence name, for example MIT or Apache-2.0.
If none is found, record "NOT FOUND". This matters because only permissively licensed
projects may be used in the hackathon.
</Step>

<Step>
**Extract claims.** Read the docs and pull out every statement that can be checked
against the code. Sort each one into a category from `categories.md`:
COMMAND, PATH, ENV, API, VERSION, DEPENDENCY, COUNT.
Give each claim an ID (C1, C2, ...) and record the doc file and line it came from.
Ignore opinions, marketing text and things that cannot be checked from the repo.
Write the claim list into your todo list so progress is visible.
</Step>

<Step>
**Check claims in parallel.** Spawn one read-only `explore` subagent per category
that has claims (up to six). Give each subagent:
- the target folder,
- the list of claims in its category (ID, exact quoted text, doc location), and
- the checking rules for that category from `categories.md`.

Each subagent must return, for every claim, one verdict:
- OK: the code confirms it (cite file:line),
- DRIFT: the code contradicts it (cite file:line and say what the truth is),
- UNVERIFIED: no clear evidence either way (say what was searched).

If there are fewer than 5 claims in total, check them directly instead of spawning subagents.
Also run the ENV reverse check from `categories.md` (settings the code reads that the docs
never mention), even if there are no ENV claims.
</Step>

<Step>
**Double-check every DRIFT.** Before reporting a DRIFT:
1. Re-open the cited code evidence yourself and confirm it. If it is weak, downgrade the
   claim to UNVERIFIED. A false alarm is worse than a missed problem.
2. Re-open the doc file and confirm the quoted text is on exactly the cited line number.
   Line numbers start at 1. If the quote is on a different line, correct the number.
</Step>

<Step>
**Group by root cause.** If several DRIFT claims come from the same underlying problem
(for example a missing file that is mentioned in two places), report them as ONE finding
and list all the affected claim IDs and doc lines in it. Each claim still counts
separately in the trust score.
</Step>

<Step>
**Rate severity** for each finding using `categories.md`:
HIGH (a new developer following the docs will fail), MEDIUM (confusing or misleading),
LOW (cosmetic or minor).
</Step>

<Step>
**Write the reports** into the target folder:
1. `DRIFT_REPORT.md`, using exactly the layout in `report-template.md`.
2. `DRIFT_REPORT.json`, using exactly the structure in `report-schema.md`. It must be valid
   JSON (double quotes, no comments, no trailing commas) and contain the same numbers and
   findings as the Markdown report.

Trust score = OK claims / (OK + DRIFT claims) x 100, rounded to a whole number.
UNVERIFIED claims are listed but not counted in the score. If there are no OK or DRIFT
claims at all, the score is null.
</Step>

<Step>
**Finish** with a short chat summary: target, licence, number of claims checked, DRIFT
findings by severity, and the trust score. If you were started as a subtask, return this
summary as your result so the Pilot can use it.
</Step>
</Steps>
