# Evidence rules for the Docs Auditor

- Every OK or DRIFT verdict must cite at least one real file path and line number.
- Quote the documentation text exactly; do not paraphrase it.
- Never invent a file, line, script or variable name. If you did not open it, do not cite it.
- When unsure, use UNVERIFIED. Precision matters more than coverage.
- Keep the report in the exact layout of report-template.md so reports from different
  repos can be compared side by side.
- Doc line numbers must point at the exact line that contains the quote. Check them before
  writing the report; being off by one line makes a finding harder to trust.
- Always write both DRIFT_REPORT.md and DRIFT_REPORT.json, with the same numbers.
- Evidence for DRIFT must be inside the repository. General knowledge about tools or versions
  goes under "Outdated practices" (advice only), never under DRIFT.
