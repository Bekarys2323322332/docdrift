# Claim categories and how to check them

## COMMAND
Shell commands the docs tell people to run (install, build, test, start, migrate).
Check:
- npm / yarn / pnpm scripts exist in package.json "scripts".
- make targets exist in the Makefile.
- dotnet commands point to real .csproj / .sln files and projects.
- python commands point to real modules or scripts; pip install uses real requirement files.
- docker / docker compose commands point to real Dockerfiles, compose files and service names.
- Flags and arguments are still accepted by the script, if the script is in the repo.

## PATH
Files and folders the docs mention (config files, entry points, folders to edit).
Check: the path exists exactly as written (case matters). If not, search for a file
with the same name elsewhere. If one is found, it was probably moved: report the new path.
A PATH claim only needs the file or folder to exist. If a file is listed by a directory
listing or glob but its contents are blocked (for example by .bobignore), it still
exists: mark the claim OK, not UNVERIFIED.

## COUNT
Numbers the docs state about the code ("68 tests", "5 endpoints", "3 models").
Check: count carefully, and watch for things that multiply the count.
For tests in particular, @pytest.mark.parametrize, test classes, and fixtures with
params make the real number of tests larger than the number of `def test_` lines.
If any of these are present and you cannot run the test collector, mark the claim
UNVERIFIED and explain why, instead of reporting DRIFT from a simple text count.

## ENV
Environment variables and config keys (DATABASE_URL, PORT, API keys, appsettings keys).
Check:
- Search the code for where the variable is read (process.env, os.environ, os.getenv,
  Environment.GetEnvironmentVariable, IConfiguration keys, .env.example).
- DRIFT if the docs name a variable the code never reads, or if the code requires a
  variable the docs setup section never mentions (report the missing one too).
- Also check default values and ports if the docs state them.
- ALWAYS do a reverse check, even if the docs make no ENV claims: search the code for
  every environment variable and config key it reads, and list any that the docs never
  mention. Record each one's name, where it is read (file:line), and its default value
  if the code has one. Never read or quote the values in .env files: only the names.
  This list is what the fixer needs to write correct setup instructions.
- Report the undocumented settings as a DRIFT finding (not just a note) when either:
  (a) a doc file, including comments in .env.example, promises that the settings are
      documented ("a complete list is in the documentation") and they are not, or
  (b) the code REQUIRES a setting (no default, startup fails without it) and the setup
      instructions never mention it.
  Otherwise list them only in the "Undocumented settings" table.
- Before saying a setting (or anything else) is undocumented, search for documentation that
  lives inside the code as well: module docstrings, API documentation pages generated from
  docstrings (for example a table in `api/__init__.py` shown at `/docs`), help text in CLI
  commands, and docs folders. Documentation in those places counts as documentation.

## API
Code examples, function / class names, parameters, HTTP routes and methods.
Check:
- Functions and classes in examples exist with the same name and parameter list.
- HTTP routes exist with the same path and method (look at route decorators,
  controllers, router definitions, MapGet/MapPost calls).
- Request/response field names match the models.

## VERSION
Runtime and tool versions (Node 18, Python 3.11, .NET 8, Java 17).
Check against: package.json "engines", .nvmrc, .python-version, pyproject.toml,
global.json, TargetFramework in .csproj, Dockerfile base images, CI config files.

## DEPENDENCY
Libraries and services the docs say are needed (PostgreSQL, Redis, a specific package).
Check: they appear in dependency files, docker-compose services or config.
DRIFT if the docs require something the project no longer uses, or the project
clearly needs something the docs never mention.

# Evidence must come from the repository

A DRIFT verdict needs evidence inside the repository (a file and line that contradicts
the docs). Knowledge about the outside world (a tool release, a deprecated command, a newer
library version) is NOT evidence of drift, because the docs may still match the code.
List such observations separately under "Outdated practices" (advice only, never counted in
the trust score, never fixed automatically), and say plainly that they come from general
knowledge, not from the code.

# Severity guide

- HIGH: following the docs will fail. Examples: a setup command that does not exist,
  a required env var that is missing from the docs, a wrong runtime major version.
- MEDIUM: misleading or will waste time but does not block. Examples: a moved file,
  an outdated code example, a renamed route in an API table.
- LOW: cosmetic. Examples: a stale default value that is rarely used, wrong casing
  in a path on a case-insensitive system, outdated optional steps.
