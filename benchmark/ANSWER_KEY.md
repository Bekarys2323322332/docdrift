# DocDrift Benchmark: Answer Key

IMPORTANT: never put this file inside the project that Bob is auditing.
If Bob can read the answers, the test is meaningless.

## Setup

- Base project: `time_forecasting` (my own project, so no data or licence issues)
- Starting point: the README after the real `.env.example` fix, which DocDrift v2 had
  already rated clean apart from items it marked UNVERIFIED
- 10 errors were planted by hand (no Bob, no coins) into `README_planted.md`
- Bob was NOT told that errors were planted. It got the normal audit prompt.

## The 10 planted errors

| # | Category | Line | README now says (wrong) | Truth in the code | Difficulty |
|---|---|---|---|---|---|
| P1 | COMMAND | 55 | `uvicorn src.api.server:app` | `src/api/main.py` (there is no server.py) | Easy |
| P2 | COMMAND | 56 | `streamlit run dashboard/main.py` | `dashboard/app.py` | Easy |
| P3 | PATH | 105 | `src/api/endpoints.py` | `src/api/routes.py` | Easy |
| P4 | PATH | 109 | `src/training/lstm_model.py` | `src/training/lstm_trainer.py` | Easy |
| P5 | API | 81 | `GET /models` | route is `GET /tickers` (line 71 of the README still says /tickers) | Medium |
| P6 | API | 85 | `POST /predict` | route is `POST /forecast` | Medium |
| P7 | API | 80 | `POST /health` | route is `GET /health` (only the method is wrong) | Hard |
| P8 | VERSION | 204 | Python 3.9 | Python 3.12 (Dockerfiles / project config) | Medium |
| P9 | DEPENDENCY | 205 | Redis is part of the stack | Redis is not used anywhere | Medium |
| P10 | ENV | 52 | set `DB_CONNECTION_STRING` for PostgreSQL | the code reads `DATABASE_URL` | Hard |

Difficulty is my own guess before the run:
- Easy: a file name that simply does not exist.
- Medium: something that exists under a different name, or needs checking config files.
- Hard: the name is plausible and only a detail is wrong (HTTP method, variable name).

## How to score

For each planted error, mark it:
- CAUGHT: reported as DRIFT with correct evidence
- PARTIAL: noticed but marked UNVERIFIED, or wrong evidence
- MISSED: not reported at all

Then count separately:
- FALSE ALARMS: DRIFT findings that are NOT one of the 10 and are NOT real problems
- EXTRA REAL FINDINGS: DRIFT findings that are not planted but turn out to be genuinely true
  (these are a bonus, not a false alarm; check each one by hand)

## Results (fill in after the run)

| # | Result | Notes |
|---|---|---|
| P1 | CAUGHT | D1 HIGH, evidence src/api/main.py |
| P2 | CAUGHT | D2 HIGH, evidence dashboard/app.py |
| P3 | CAUGHT | D5 MEDIUM, correct file; cited README line 104 (actual 105) |
| P4 | CAUGHT | D6 MEDIUM, correct file; cited README line 108 (actual 109) |
| P5 | CAUGHT | D4 HIGH, evidence src/api/routes.py:69 |
| P6 | CAUGHT | D7 MEDIUM, evidence src/api/routes.py:198 |
| P7 | CAUGHT | D8 MEDIUM, spotted wrong HTTP method only, routes.py:59 |
| P8 | CAUGHT | D9 LOW, evidence Dockerfile.api:3 python:3.12-slim |
| P9 | CAUGHT | D10 LOW, checked requirements.txt, docker-compose.yml and src/; cited line 204 (actual 205) |
| P10 | CAUGHT | D3 HIGH, code reads DATABASE_URL at src/config.py:17 |

- Caught: 10 / 10
- Partial: 0
- Missed: 0
- False alarms: 0
- Extra real findings: 2 undocumented settings (API_PORT at src/config.py:20, API_BASE_URL at dashboard/app.py:34), both genuinely missing from the README
- Bobcoins used: 1.65
- Time taken by Bob: 3 min 10 s
- Manual comparison: I already know these answers, so I cannot time myself fairly here.
  Instead, time a manual audit of a DIFFERENT README I have not seen: __ minutes

## Headline sentence for the README / demo

"On a README with 10 planted errors, DocDrift caught 10 of 10 with 0 false alarms,
for 1.65 Bobcoins in about 3 minutes."

## Honest caveats

- One run, on one project. A second run or a second project would make the result stronger.
- README line numbers were off by one for 3 findings (P3, P4, and P9, which cited line 204 for Redis on 205). The file and the
  fix were correct, so a developer would still find the spot instantly.
- The planted errors were written by me, so they are cleaner than real-world drift.
