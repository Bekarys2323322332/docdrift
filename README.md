# DocDrift

**Finds every place your docs no longer match your code, proves it, and fixes the docs.
Built on IBM Bob IDE.**

A new developer clones a project, follows the README, and the setup command fails. The file
it mentions was renamed, the environment variable has a different name, the endpoint moved.
Docs go stale because nothing checks them against the code. DocDrift does.

> One command in Bob: `/docdrift https://github.com/owner/repo`
> Bob clones the repo, checks every claim in the docs against the code with parallel
> subagents, shows you the results, asks what to fix, fixes the docs on a branch, and asks
> before committing.

## Results

| Test | Result |
|---|---|
| Planted-errors benchmark (10 errors hidden in a README, Bob not told) | **10 / 10 caught, 0 false alarms**, 3 min 10 s, 1.65 Bobcoins |
| My own project (time_forecasting) | **2 real bugs found**, including a HIGH one version 1 missed. Fix proven by following the README from scratch: 44 tests pass |
| Open-source project (flask-realworld-example-app, MIT) | 16 / 16 claims correct, **0 false alarms**, under 1 minute, 0.59 Bobcoins |
| Cost of one audit | about 0.6 to 1.7 Bobcoins |

<!-- Add a row for each /docdrift pipeline run: repo, trust score, findings, fixes, coins. -->

The detailed log, including what went wrong and how it was fixed, is in [NOTES.md](NOTES.md).
The benchmark answer key is in [benchmark/ANSWER_KEY.md](benchmark/ANSWER_KEY.md).

## How it works

```
/docdrift <repo>
      |
      v
DocDrift Pilot mode ---- clones into audits/<repo>, checks the licence
      |
      |  subtask
      v
Docs Auditor mode (read-only) ---- docs-drift-check skill
      |   extracts every checkable claim (commands, paths, settings, API routes,
      |   versions, dependencies, counts), then checks them with parallel
      |   explore subagents, one per category
      |   double-checks every problem, writes DRIFT_REPORT.md + .json
      v
Pilot shows results and asks: fix all / HIGH+MEDIUM / choose IDs / nothing
      |
      |  subtask, on branch docdrift/fix-docs
      v
Docs Fixer mode (docs only) ---- docs-drift-fix skill
      |
      v
Pilot shows the diff and asks before committing. Never pushes.
```

### IBM Bob features used

| Bob feature | How DocDrift uses it |
|---|---|
| Custom modes | Three modes with enforced permissions: Pilot (orchestrates, git only), Auditor (can only write its report), Fixer (can only edit docs, never code) |
| Skills | `docdrift-pipeline`, `docs-drift-check`, `docs-drift-fix`, each with supporting files (categories, report template, JSON schema) |
| Parallel subagents | One read-only `explore` subagent per claim category, run at the same time |
| Subtasks and mode switching | The Pilot hands the audit and the fix to the specialist modes |
| Document understanding | Reading README / docs in Markdown and reStructuredText and turning prose into checkable claims |
| Custom slash commands | `/docdrift`, `/docdrift-audit`, `/docdrift-fix` |
| Rules | Evidence rules: every verdict must cite a real file and line |
| .bobignore | Keeps secrets (`.env`), dependencies and the benchmark answer key away from Bob |
| Bob Shell (optional) | `scripts/docdrift.ps1` runs a hands-free audit from the terminal |

### Safety by design

- **The auditor cannot change anything.** Its edit permission is limited by a pattern to
  `DRIFT_REPORT` files.
- **The fixer cannot touch code.** The code is treated as the source of truth; anything that
  would need a code change is listed under "Needs a human decision".
- **A human decides.** The Pilot asks before fixing and before committing, and never pushes.
- **Evidence or nothing.** Every finding cites a file and line. When unsure, DocDrift says
  UNVERIFIED instead of guessing, because a false alarm costs more trust than a miss.
- **Secrets stay private.** `.env` files are blocked, and reports list setting names only.

## Quick start

1. Open this folder in Bob IDE (File > Open Folder) and trust the workspace.
2. Pick **DocDrift Pilot** in the mode menu.
3. Allow Read, Execute, Skill, Subtask, Todo and Mode in the permissions menu.
4. Type: `/docdrift https://github.com/owner/repo`
5. Answer Bob's questions. Reports land in `audits/<repo>/` and `reports/`.

Your own local project works too: `/docdrift C:\path\to\your\project` clones only committed
files, so secrets in `.env` never reach the audit.

### Dashboard

Open `dashboard/index.html` in a browser and load a report from `reports/`. You get the
trust score, each finding with "docs say" next to "code says", settings the docs never
mention, and filters. Tick findings and click **Copy command** to get the exact
`/docdrift-fix` command to paste into Bob.

### Terminal (Bob Shell, optional)

```powershell
.\scripts\docdrift.ps1 https://github.com/owner/repo
```

Clones, audits with Bob Shell (capped at 3 Bobcoins), saves the report and opens the
dashboard. It only audits; fixing always goes through Bob IDE with a human in the loop.

## What it checks

| Category | Example of drift it catches |
|---|---|
| COMMAND | `npm run dev` in the README, but no `dev` script in package.json |
| PATH | Docs mention `src/api/server.py`, the file is `src/api/main.py` |
| ENV | Docs say `DB_CONNECTION_STRING`, the code reads `DATABASE_URL`; settings the code needs that the docs never mention |
| API | Docs say `POST /health`, the route is `GET /health` |
| VERSION | Docs say Python 3.9, the Dockerfile uses 3.12 |
| DEPENDENCY | Docs list Redis, nothing in the project uses it |
| COUNT | "68 tests", checked carefully (parametrized tests counted correctly) |

## Limitations

- DocDrift checks that the docs match the code. It does not run the project, so it cannot
  tell whether dependencies still install today ("dependency rot"). That would be a good
  next feature.
- Very large docs folders are only partly audited to keep costs down (the report says so).
- AI can be confidently wrong: during development Bob once stated a wrong library default
  in its reasoning. DocDrift's defence is evidence for every finding, a double-check step,
  and a human approving every fix.
- The benchmark is one run on one project, and planted errors are cleaner than real drift.

## Repository layout

```
.bob/                custom modes, skills, rules and slash commands (the product)
dashboard/           single-file report viewer
scripts/             Bob Shell automation
benchmark/           planted-errors README and answer key
examples/            reports from real runs
reports/             reports saved by the pipeline for the dashboard
audits/              cloned repositories being audited (not committed)
bob_sessions/        Bob IDE task session screenshots (hackathon evidence)
NOTES.md             build log: every run, measurement and change
DATA_SOURCES.md      every repository used and its licence
```

## Credits

Built for the IBM Bob 2.0 Hackathon (lablab.ai, September 2026) by Beka.
All audits and fixes were performed by IBM Bob. Planning, the dashboard page and drafts of
the mode and skill files were written with help from Claude (Anthropic).
