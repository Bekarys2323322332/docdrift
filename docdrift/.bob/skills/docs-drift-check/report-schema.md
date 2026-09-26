# DRIFT_REPORT.json structure

Write exactly these keys. Use `null` when a value is unknown. Do not add comments.
Paths are relative to the target folder. Line numbers start at 1.

```json
{
  "tool": "DocDrift",
  "schema_version": 1,
  "repo": {
    "name": "example-repo",
    "source": "https://github.com/owner/example-repo",
    "licence": "MIT",
    "target_folder": "audits/example-repo"
  },
  "audited_at": "2026-09-26",
  "doc_files": ["README.rst"],
  "summary": {
    "claims_checked": 16,
    "ok": 14,
    "drift": 2,
    "unverified": 0,
    "trust_score": 88,
    "findings_by_severity": { "HIGH": 1, "MEDIUM": 1, "LOW": 0 }
  },
  "findings": [
    {
      "id": "D1",
      "severity": "HIGH",
      "category": "COMMAND",
      "summary": "One line describing the problem",
      "claim_ids": ["C4"],
      "doc": { "file": "README.rst", "line": 40, "quote": "exact text from the docs" },
      "evidence": [
        { "file": "src/app.py", "line": 77, "note": "what the code actually shows" }
      ],
      "why_it_matters": "One sentence on what happens to someone following the docs",
      "suggested_fix": "The exact corrected text for the docs"
    }
  ],
  "undocumented_settings": [
    { "name": "API_PORT", "file": "src/config.py", "line": 20, "default": "8000" }
  ],
  "outdated_practices": [
    { "doc": { "file": "README.md", "line": 34 }, "observation": "Uses docker-compose; newer Docker installs use docker compose. General knowledge, not evidence from the code." }
  ],
  "unverified": [
    { "id": "C25", "category": "COUNT", "claim": "68 tests", "doc": { "file": "README.md", "line": 116 }, "searched": "what was searched and why it is not conclusive" }
  ],
  "ok": [
    { "id": "C1", "category": "COMMAND", "claim": "docker compose up --build", "doc": { "file": "README.md", "line": 29 }, "evidence": { "file": "docker-compose.yml", "line": 1 } }
  ]
}
```

Rules:
- `summary.drift` counts DRIFT claims, not findings (one finding can cover several claims).
- `findings_by_severity` counts findings.
- `severity` is one of HIGH, MEDIUM, LOW. `category` is one of COMMAND, PATH, ENV, API,
  VERSION, DEPENDENCY, COUNT.
- Never put secret values in the report. Setting names and code defaults only.
