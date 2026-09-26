<#
.SYNOPSIS
  Hands-free DocDrift audit from the terminal, using Bob Shell.

.DESCRIPTION
  One command does everything for an audit:
    1. clones the repository into audits/<name> (or reuses an existing clone)
    2. runs the Docs Auditor mode through Bob Shell (non-interactive)
    3. copies DRIFT_REPORT.json into reports/ for the dashboard
    4. opens the dashboard

  This script only AUDITS. It never fixes anything, because fixing should always
  have a human in the loop. To fix, use the /docdrift or /docdrift-fix command
  in Bob IDE, or tick findings in the dashboard and paste the command into Bob.

  Requirements:
    - git
    - Bob Shell (optional hackathon tool): https://bob.ibm.com/docs/shell
      installed and logged in with the hackathon account.

  Note: in non-interactive mode Bob Shell pre-approves all tool calls. The Docs Auditor
  mode itself can only write DRIFT_REPORT files, which keeps this safe.

.EXAMPLE
  .\scripts\docdrift.ps1 https://github.com/gothinkster/flask-realworld-example-app

.EXAMPLE
  .\scripts\docdrift.ps1 https://github.com/owner/repo -Docs "README.md docs/setup.md" -MaxCost 2
#>
param(
  # Git URL of the repository to audit, or a local folder that is a Git repository.
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Repo,

  # Which doc files to audit. Leave as "auto-detect" to let the skill find the README and docs.
  [string]$Docs = "auto-detect",

  # Safety cap on Bobcoins for this one run.
  [double]$MaxCost = 3,

  # Skip opening the dashboard at the end.
  [switch]$NoDashboard
)

$ErrorActionPreference = "Stop"

# The DocDrift workspace is the folder above this script (the one containing .bob).
$root = Split-Path -Parent $PSScriptRoot

# --- Check the tools we need --------------------------------------------------
foreach ($tool in @("git", "bob")) {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
    Write-Host "Could not find '$tool'. Install it first (see the comments at the top of this script)." -ForegroundColor Red
    exit 1
  }
}

# --- Work out the repository name -----------------------------------------------
# "https://github.com/owner/repo.git" -> "repo"; "C:\code\my-app" -> "my-app"
$name = ($Repo.TrimEnd('/', '\') -split '[\\/]')[-1] -replace '\.git$', ''
$target = "audits/$name"
$targetPath = Join-Path $root $target

# --- Clone (or reuse) --------------------------------------------------------------
if (Test-Path $targetPath) {
  Write-Host "Reusing existing clone in $target" -ForegroundColor Yellow
} else {
  Write-Host "Cloning $Repo into $target ..."
  New-Item -ItemType Directory -Force (Join-Path $root "audits") | Out-Null
  if (Test-Path $Repo) {
    # Local folder: clone it, which copies only committed files (no .env, no secrets).
    git clone $Repo $targetPath
  } else {
    git clone --depth 1 $Repo $targetPath
  }
  if ($LASTEXITCODE -ne 0) { Write-Host "git clone failed." -ForegroundColor Red; exit 1 }
}

# Remove an old report so we never show stale results by mistake.
Remove-Item (Join-Path $targetPath "DRIFT_REPORT.json") -ErrorAction SilentlyContinue

# --- Run the audit with Bob Shell ------------------------------------------------------
$prompt = @"
Use the docs-drift-check skill.
Target folder: $target
Source: $Repo
Doc files: $Docs
Check the categories in parallel with explore subagents and write DRIFT_REPORT.md and
DRIFT_REPORT.json in the target folder. Then return the short summary.
"@

Write-Host "Running the Docs Auditor with Bob Shell (max $MaxCost Bobcoins) ..."
$started = Get-Date
bob run --workspace $root --mode docs-auditor --max-cost $MaxCost $prompt
$seconds = [int]((Get-Date) - $started).TotalSeconds
Write-Host "Bob finished in $seconds seconds."

# --- Save the report for the dashboard ------------------------------------------------
$report = Join-Path $targetPath "DRIFT_REPORT.json"
if (-not (Test-Path $report)) {
  Write-Host "No DRIFT_REPORT.json was written. Check Bob's output above." -ForegroundColor Red
  exit 1
}

# Make sure it is valid JSON before we save it.
try { $data = Get-Content $report -Raw | ConvertFrom-Json }
catch { Write-Host "DRIFT_REPORT.json is not valid JSON. Ask Bob to rewrite it." -ForegroundColor Red; exit 1 }

$reportsDir = Join-Path $root "reports"
New-Item -ItemType Directory -Force $reportsDir | Out-Null
$date = Get-Date -Format "yyyy-MM-dd"
$dest = Join-Path $reportsDir "$name-$date.json"
$n = 2
while (Test-Path $dest) { $dest = Join-Path $reportsDir "$name-$date-$n.json"; $n++ }
Copy-Item $report $dest

$s = $data.summary
Write-Host ""
Write-Host "Trust score: $($s.trust_score)%  |  claims: $($s.claims_checked)  |  drift: $($s.drift)  |  unverified: $($s.unverified)" -ForegroundColor Cyan
Write-Host "Report saved to reports\$(Split-Path -Leaf $dest)"

if (-not $NoDashboard) {
  Start-Process (Join-Path $root "dashboard\index.html")
  Write-Host "Dashboard opened. Click 'Load reports' and pick the file above."
}
