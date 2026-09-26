# DocDrift: Build Notes

Running log of what happened, what I measured, and what I changed. This is the raw
material for the final README, the pitch and the demo video.

## The idea

DocDrift finds every place a project's documentation no longer matches its code,
proves each problem with file-and-line evidence, and fixes the docs.
Built entirely on IBM Bob IDE features: custom modes, skills, parallel explore
subagents, rules files and document understanding.

## Setup (Friday 25 Sep)

- Bob IDE v2.2.0, hackathon Enterprise account, 40 Bobcoins
- Two custom modes:
  - Docs Auditor: can read everything but can only write DRIFT_REPORT files
  - Docs Fixer: can only edit documentation files and .env.example, never code
- Two skills: docs-drift-check (audit) and docs-drift-fix (repair)
- Rules file forcing file:line evidence for every verdict
- `.bobignore` keeps secrets (.env), the virtual environment and large data files away
  from Bob. This protects secrets and saves Bobcoins.
- Mode, skill and rule files were drafted with Claude (as a planning assistant).
  All audits and fixes were performed by IBM Bob.

## Run 1: first audit of my own project (skill v1)

- Project: time_forecasting (my own FastAPI / PyTorch / Streamlit project)
- 46 claims checked, 4 parallel explore subagents
- Cost: 0.79 Bobcoins
- Findings:
  - REAL: README says `copy .env.example .env`, but `.env.example` did not exist.
    A new developer gets stuck on setup step 3.
  - FALSE ALARM: said "68 tests" was wrong because it counted 63 `def test_` lines.
    I checked by hand with `pytest --collect-only -q`: the real total is
    15 + 19 + 18 + 16 = 68. The README was right. Cause: parametrized tests turn one
    function into several tests.

## What I changed after run 1 (skill v2)

- Added a COUNT category that treats parametrized tests carefully and says UNVERIFIED
  instead of guessing when it cannot run the tests.
- A file that exists but is blocked from reading now counts as OK for path claims.
- Added a reverse check for settings: list every setting the code reads that the
  docs never mention (names only, never values).
- Findings with the same root cause are grouped into one.

## Run 2: same project, skill v2

- 48 claims checked
- Found a NEW HIGH problem that v1 missed: the README promises "the default .env uses
  SQLite, no database server needed", but `.env.example` was missing, so the code fell
  back to its built-in PostgreSQL default (`src/config.py:17`, also `docker-compose.yml`).
  Anyone following the local setup would get a database connection error.
- Test count now correctly marked UNVERIFIED (no false alarm).
- 0 false alarms.

## Something the audit led me to (found while checking by hand)

- Running the tests revealed that `src/config.py` rejects unknown settings, and my own
  `.env` contains `API_BASE_URL` (used by the dashboard). Result: settings fail to load
  and two test files crash on collection. The docs pointed me at the setup section,
  and checking it by hand exposed a real bug.

## Run 3: fix (Docs Fixer, skill v3)

- My decision: the README is right (local dev should use SQLite); the missing
  `.env.example` is the bug.
- Bob created `.env.example` with `DATABASE_URL=sqlite:///./timeseries.db`, and left
  `API_BASE_URL` out, listing it under "Needs a human decision".
- Bob made a factual mistake in its reasoning: it claimed pydantic-settings ignores unknown
  settings by default. My own test run showed the opposite ("Extra inputs are not
  permitted"). The action was still correct because my instruction told it what to do.
  Lesson: AI can be confidently wrong, so every finding needs evidence and a human check.
- Proof the fix works: acting as a brand-new developer, I followed the README exactly
  (copied .env.example to .env) and ran `pytest -m "not slow"`:
  44 passed, 24 deselected.
  Before the fix, the same README step failed because the file did not exist.

## Run 4: planted-errors benchmark (Saturday 26 Sep)

- 10 errors planted by hand, answer key kept OUTSIDE the project (benchmark/ANSWER_KEY.md)
- Bob was not told errors were planted. Stopwatch: 3 min 10 s.
- 43 claims checked. Result: 10 / 10 caught, 0 missed, 0 false alarms, 0 unverified.
- Even the two hardest ones were caught: the wrong HTTP method (POST /health instead of GET)
  and the wrong variable name (DB_CONNECTION_STRING instead of DATABASE_URL).
- Bonus: the reverse settings check listed 2 settings the README never mentions
  (API_PORT, API_BASE_URL). Both are real.
- Caveat: 3 findings cited a README line number off by one. Correct file, correct fix.

## Run 5: real open-source project (flask-realworld-example-app, MIT, last updated 2019)

- Audited README.rst (shows it works on reStructuredText, not just Markdown)
- 16 claims checked, under 1 minute, 0.59 Bobcoins
- Result: 16 OK, 0 DRIFT, 0 UNVERIFIED, trust score 100%
- I spot-checked Bob's evidence by hand: the env vars (CONDUIT_SECRET, FLASK_APP,
  FLASK_DEBUG, DATABASE_URL), the custom `flask test` command and both file paths all match
  the code. The 100% is correct, and there were no false alarms on an unfamiliar project.
- Honest limitation this revealed: DocDrift checks that the docs match the code. It does not
  check whether the project still installs today. This repo pins very old packages
  (SQLAlchemy 1.1.9 from 2017) next to unpinned Flask, which may well fail on a modern
  Python. That is "dependency rot", a different problem and a possible future feature.

## Numbers for the pitch

- Cost per full audit: about 0.8 to 1.7 Bobcoins
- Real bugs found in my own project: 2 (missing .env.example, SQLite/PostgreSQL mismatch)
- v1 false alarms: 1; v2 false alarms: 0
- Benchmark: 10 / 10 caught, 0 false alarms, 3 min 10 s
- Manual audit time vs DocDrift time: __ min vs __ min

## Bobcoin log

| Task | What | Coins |
|---|---|---|
| 1 | Audit v1 | 0.79 |
| 2 | Audit v2 | |
| 3 | Fix | |
| 4 | Benchmark audit (3 min 10 s) | 1.65 |
| 5 | flask-realworld audit (under 1 min) | 0.59 |

## Automation (Saturday evening)

Goal: remove every manual step (copying .bob, typing prompts, switching modes).
- One DocDrift workspace: repositories are cloned into audits/, so .bob is never copied again.
- New DocDrift Pilot mode + docdrift-pipeline skill: clones, checks the licence, delegates the
  audit to Docs Auditor and the fix to Docs Fixer as subtasks, asks which findings to fix,
  works on a branch, asks before committing, never pushes.
- Slash commands: /docdrift <repo>, /docdrift-audit, /docdrift-fix.
- Reports are now also written as DRIFT_REPORT.json (machine-readable).
- Audit skill now double-checks doc line numbers (fixes the off-by-one seen in the benchmark)
  and records the repository licence (hackathon data rules).
- Dashboard (dashboard/index.html): trust score, docs-vs-code comparison per finding, filters,
  and a fix-command builder that produces the /docdrift-fix command to paste into Bob.
- scripts/docdrift.ps1: hands-free audit from the terminal using Bob Shell (audit only).

Pipeline runs:
| Repo | Trust score | Findings | Fixed | Coins | Time |
|---|---|---|---|---|---|
| miguelgrinberg/microblog-api (MIT, updated 2024) | 93% | 1 weak finding + 1 real gap | real gap fixed | 1.74 | not recorded |

## Run 6: first full /docdrift pipeline run (microblog-api)

- One command: `/docdrift https://github.com/miguelgrinberg/microblog-api`. The Pilot cloned
  the repo, confirmed the MIT licence, delegated the audit as a subtask to Docs Auditor,
  presented results, asked what to fix, delegated the fix as a subtask to Docs Fixer, and
  asked before committing. Git commands needed my approval each time (by design).
- The auditor's only DRIFT finding (`docker-compose` vs `docker compose`) was based on
  general knowledge about Docker, not on evidence in the repository. I rejected it.
  -> Changed the skill: outside knowledge now goes to "Outdated practices" (advice only,
     not counted in the score).
- The real problem was filed as "informational": `.env.example` line 1 promises
  "A complete list of supported variables is included in the documentation", but no list
  existed; config.py reads 23 settings, 16 of them documented nowhere.
  -> Changed the skill: a doc that promises documentation which does not exist is DRIFT.
- Fix: Docs Fixer added a Configuration section to README.md.
- Human review caught two mistakes in the fix before commit:
  1. SECRET_KEY default written as "change-in-production"; the real default in config.py:21
     is "top-secret!". A fix for drift must not introduce new drift.
  2. The table had 16 rows, but a "complete list" needs all 23 (the 7 already in .env.example
     were missing).
  Both corrected by Bob. The commit step then hung (a git command waited for input in
  Bob's terminal) and I had to restart Bob, so I committed by hand.
  -> Changed the skill: git always runs with --no-pager and commits with -m, so it can
     never wait for input.
- Cost: 1.74 Bobcoins for the whole pipeline (clone, audit, fix, corrections).
- Lesson for the pitch: the human-in-the-loop step is not decoration. It caught one weak
  finding and two errors in a fix during a single run.
