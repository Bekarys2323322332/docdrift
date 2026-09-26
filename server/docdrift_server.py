"""
DocDrift local server
=====================

Lets you start a DocDrift audit from the dashboard: paste a repository link, click
"Audit", and the report appears when IBM Bob has finished.

What it does, step by step:
  1. serves the DocDrift folder (dashboard + reports) at http://127.0.0.1:8765
  2. when you click Audit, clones the repository into audits/<name>
  3. runs the Docs Auditor mode through Bob Shell ("bob run", non-interactive)
  4. checks the report is valid JSON, stamps the real date, saves it in reports/
     and adds it to reports/index.json, so the dashboard loads it automatically

Safety choices:
  - Listens on 127.0.0.1 only, so nobody else on the network can start audits
    (or spend your Bobcoins).
  - Only AUDITS. It never fixes or commits anything. Fixing stays in Bob IDE, where a
    human approves every change.
  - Every run has a Bobcoin cap (--max-cost).
  - Only one audit runs at a time.
  - Never reads or sends your Bob credentials: Bob Shell uses its own login.

Requirements: Python 3.9+ (standard library only), git, and Bob Shell installed and
logged in with the hackathon account.

Run it from the DocDrift folder:
    python server/docdrift_server.py
then open http://127.0.0.1:8765/dashboard/
"""

import datetime
import json
import re
import shutil
import subprocess
import threading
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"          # local machine only
PORT = 8765
DEFAULT_MAX_COST = 2.0      # Bobcoin cap per audit
MAX_COST_LIMIT = 5.0        # the dashboard can never ask for more than this
BOB_TIMEOUT_SECONDS = 20 * 60

# The DocDrift workspace is the folder above this file (it contains .bob/).
ROOT = Path(__file__).resolve().parent.parent
AUDITS = ROOT / "audits"
REPORTS = ROOT / "reports"

# Accept https links to the big public Git hosts only.
ALLOWED_HOSTS = {"github.com", "gitlab.com", "bitbucket.org", "codeberg.org"}

# ---------------------------------------------------------------------------
# Job bookkeeping (kept in memory; restarting the server forgets old jobs)
# ---------------------------------------------------------------------------

jobs = {}                       # job id -> dict with status, log lines, result
jobs_lock = threading.Lock()    # protects the jobs dict
audit_running = threading.Lock()  # held while an audit runs, so only one at a time


def new_job(repo):
    job_id = uuid.uuid4().hex[:8]
    job = {"id": job_id, "repo": repo, "status": "queued", "log": [], "report": None,
           "error": None, "started": datetime.datetime.now().isoformat(timespec="seconds")}
    with jobs_lock:
        jobs[job_id] = job
    return job


def log(job, message):
    """Add a line to the job's log (the dashboard shows the last lines as progress)."""
    line = message.rstrip()
    if not line:
        return
    with jobs_lock:
        job["log"].append(line)
        del job["log"][:-300]   # keep the last 300 lines only
    print(f"[{job['id']}] {line}")


# ---------------------------------------------------------------------------
# Input checks
# ---------------------------------------------------------------------------

def repo_name(repo):
    """'https://github.com/owner/my-repo.git' -> 'my-repo', made safe for a folder name."""
    last = re.split(r"[\\/]", repo.rstrip("/\\"))[-1]
    last = re.sub(r"\.git$", "", last)
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", last).strip(".-")
    return safe or "repo"


def check_repo(repo):
    """Return an error message, or None if the repository source is acceptable."""
    repo = repo.strip()
    if not repo:
        return "Paste a repository link first."
    parsed = urlparse(repo)
    if parsed.scheme == "https":
        if parsed.hostname not in ALLOWED_HOSTS:
            return "Only https links to GitHub, GitLab, Bitbucket or Codeberg are accepted."
        if len([p for p in parsed.path.split("/") if p]) < 2:
            return "The link should look like https://github.com/owner/repository."
        return None
    # Otherwise treat it as a local folder on this computer that is a Git repository.
    path = Path(repo)
    if path.is_dir() and (path / ".git").exists():
        return None
    return "Use an https link to a public repository, or a local folder that is a Git repository."


# ---------------------------------------------------------------------------
# Running commands
# ---------------------------------------------------------------------------

def find_program(name):
    """Find git / bob on PATH. On Windows this also finds bob.cmd and similar shims."""
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"Could not find '{name}'. Install it and make sure it is on PATH.")
    return found


def run_streaming(job, command, cwd, timeout):
    """Run a command, copy its output into the job log line by line, return the exit code."""
    process = subprocess.Popen(
        command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
    )
    timer = threading.Timer(timeout, process.kill)  # stop runaway runs
    timer.start()
    try:
        for line in process.stdout:
            log(job, line)
        return process.wait()
    finally:
        timer.cancel()


# ---------------------------------------------------------------------------
# The audit itself
# ---------------------------------------------------------------------------

def run_audit(job, repo, docs, max_cost):
    today = datetime.date.today().isoformat()   # the real date, never guessed by the AI
    name = repo_name(repo)
    target = AUDITS / name
    target_rel = f"audits/{name}"

    try:
        git = find_program("git")
        bob = find_program("bob")

        # 1. Clone (or reuse an existing clone).
        with jobs_lock:
            job["status"] = "cloning"
        AUDITS.mkdir(exist_ok=True)
        if target.exists():
            log(job, f"Reusing existing clone in {target_rel}")
        else:
            log(job, f"Cloning {repo} into {target_rel} ...")
            clone = [git, "clone", repo, str(target)] if Path(repo).is_dir() \
                else [git, "clone", "--depth", "1", repo, str(target)]
            if run_streaming(job, clone, ROOT, 10 * 60) != 0:
                raise RuntimeError("git clone failed. Check the link and that the repository is public.")

        # Remove an old report so a failed run can never show stale results.
        report = target / "DRIFT_REPORT.json"
        report.unlink(missing_ok=True)

        # 2. Run the Docs Auditor through Bob Shell.
        with jobs_lock:
            job["status"] = "auditing"
        prompt = (
            "Use the docs-drift-check skill. "
            f"Target folder: {target_rel}. Source: {repo}. "
            f"Doc files: {docs or 'auto-detect'}. Today's date: {today}. "
            "Check the categories in parallel with explore subagents and write "
            "DRIFT_REPORT.md and DRIFT_REPORT.json in the target folder. "
            "Then return the short summary."
        )
        log(job, f"Running Bob (Docs Auditor mode, max {max_cost} Bobcoins) ...")
        args = ["run", "--workspace", str(ROOT), "--mode", "docs-auditor",
                "--max-cost", str(max_cost), "--trust", "--accept-license", prompt]
        if bob.lower().endswith(".ps1"):
            # Bob Shell installed as a PowerShell script: run it through PowerShell.
            command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", bob, *args]
        else:
            command = [bob, *args]
        code = run_streaming(job, command, ROOT, BOB_TIMEOUT_SECONDS)
        if code != 0:
            log(job, f"Bob exited with code {code}.")

        # 3. Check and save the report.
        with jobs_lock:
            job["status"] = "saving"
        if not report.exists():
            raise RuntimeError("Bob finished but did not write DRIFT_REPORT.json. See the log above.")
        try:
            data = json.loads(report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            raise RuntimeError(f"DRIFT_REPORT.json is not valid JSON ({err}).") from err
        if "summary" not in data or "findings" not in data:
            raise RuntimeError("DRIFT_REPORT.json is missing 'summary' or 'findings'.")

        # Stamp facts the server knows for certain, instead of trusting the AI with them.
        data["audited_at"] = today
        data.setdefault("repo", {})
        data["repo"].setdefault("name", name)
        data["repo"]["target_folder"] = target_rel
        data["repo"].setdefault("source", repo)

        REPORTS.mkdir(exist_ok=True)
        dest = REPORTS / f"{name}-{today}.json"
        n = 2
        while dest.exists():
            dest = REPORTS / f"{name}-{today}-{n}.json"
            n += 1
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        update_index(dest.name)

        summary = data.get("summary", {})
        log(job, f"Done. Trust score {summary.get('trust_score')}%, "
                 f"{summary.get('drift', 0)} drift, {summary.get('claims_checked', 0)} claims. "
                 f"Saved reports/{dest.name}")
        with jobs_lock:
            job["status"] = "done"
            job["report"] = dest.name
    except Exception as err:   # report any failure to the dashboard instead of crashing
        log(job, f"Error: {err}")
        with jobs_lock:
            job["status"] = "failed"
            job["error"] = str(err)
    finally:
        audit_running.release()


def update_index(new_name):
    """Put the new report first in reports/index.json (the dashboard's list of reports)."""
    index = REPORTS / "index.json"
    try:
        names = json.loads(index.read_text(encoding="utf-8"))
        if not isinstance(names, list):
            names = []
    except (FileNotFoundError, json.JSONDecodeError):
        names = []
    names = [new_name] + [n for n in names if n != new_name]
    index.write_text(json.dumps(names, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# HTTP handler: static files + a tiny JSON API
# ---------------------------------------------------------------------------

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    # Never serve Bob's configuration, secrets or cloned code over HTTP.
    BLOCKED = (".bob", ".git", "audits", ".env", "bob_sessions", "benchmark/ANSWER_KEY")

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self.send_json(200, {"ok": True, "busy": audit_running.locked()})
        if path.startswith("/api/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            with jobs_lock:
                job = jobs.get(job_id)
                snapshot = dict(job, log=job["log"][-40:]) if job else None
            if not snapshot:
                return self.send_json(404, {"error": "Unknown job."})
            return self.send_json(200, snapshot)
        if any(part in path for part in self.BLOCKED):
            return self.send_json(403, {"error": "Not available."})
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/dashboard/")
            self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/audit":
            return self.send_json(404, {"error": "Unknown endpoint."})
        # Only accept requests from our own page (blocks other websites in your browser).
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}"):
            return self.send_json(403, {"error": "Requests are only accepted from the DocDrift dashboard."})
        try:
            length = min(int(self.headers.get("Content-Length", 0)), 10_000)
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Invalid request."})

        repo = str(body.get("repo", "")).strip()
        # Doc file names only: letters, digits and simple path characters (no shell symbols).
        docs = re.sub(r"[^A-Za-z0-9 ._/\\-]", "", str(body.get("docs", "")))[:200].strip()
        try:
            max_cost = min(max(float(body.get("max_cost", DEFAULT_MAX_COST)), 0.5), MAX_COST_LIMIT)
        except (TypeError, ValueError):
            max_cost = DEFAULT_MAX_COST

        problem = check_repo(repo)
        if problem:
            return self.send_json(400, {"error": problem})
        if not audit_running.acquire(blocking=False):
            return self.send_json(409, {"error": "An audit is already running. Wait for it to finish."})

        job = new_job(repo)
        threading.Thread(target=run_audit, args=(job, repo, docs, max_cost), daemon=True).start()
        return self.send_json(202, {"job": job["id"]})

    def log_message(self, fmt, *args):
        pass   # keep the terminal for audit progress, not every file request


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"DocDrift server running. Open http://{HOST}:{PORT}/dashboard/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
