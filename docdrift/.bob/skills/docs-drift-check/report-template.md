# DocDrift Report: <repo name>

**Docs trust score: <score>%**  (<OK> of <OK + DRIFT> checkable claims are correct)

Source: <URL or local folder> | Licence: <licence> | Audited: <date>

| Claims checked | OK | DRIFT | UNVERIFIED |
|---|---|---|---|
| <total> | <ok> | <drift> (<high> high, <medium> medium, <low> low) | <unverified> |

Files audited: <list of doc files>

## Drift findings

Sorted by severity, HIGH first. One block per finding:

### D1 [HIGH] [COMMAND] <one-line summary>
- **Docs say** (`README.md:42`): "<exact quote from the docs>"
- **Code says** (`package.json:8`): <what the code actually shows>
- **Why it matters:** <one sentence on what happens to someone following the docs>
- **Suggested fix:** <the exact corrected text for the docs>

## Undocumented settings

Environment variables and config keys the code reads but the docs never mention
(names only, never values):

| Name | Read at | Default in code |
|---|---|---|

## Outdated practices (advice only, not counted)

Observations based on general knowledge rather than the code, for example a deprecated
command. They do not affect the trust score and are not fixed automatically.

| Doc location | Observation |
|---|---|

## Unverified claims

| ID | Claim | Doc location | What was searched |
|---|---|---|---|

## Verified claims (OK)

| ID | Category | Claim | Evidence |
|---|---|---|---|
