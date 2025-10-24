# Security Scanning — Local & CI

This repository includes security scanning in CI and guidance to run local scans and handle findings.

## Files added
- `tools/parse_trufflehog.py` — streaming parser that redacts and summarizes TruffleHog findings.
- `trufflehog-summary.json`, `trufflehog-summary.txt` — concise summaries generated from local run (created automatically).
- `.github/workflows/security-scan.yml` — workflow that runs TruffleHog and Dependency-Check, uploads artifacts, and fails on verified issues/high CVSS.
- `.github/workflows/suppression.xml` — suppression file template for dependency-check false positives.

## Run local scans
### Install tools
Use your Python environment (Windows PowerShell examples):

```powershell
python -m pip install --upgrade pip
pip install trufflehog ggshield
```

### Run TruffleHog (local filesystem scan)
Run a history/contents scan and output JSON (recommended):

```powershell
# scan repo and write newline-delimited JSON
trufflehog filesystem . --json > trufflehog-report.json
```

### Run GitGuardian (ggshield) — optional
You need an API key; set `GITGUARDIAN_API_KEY` as an environment variable before running.

```powershell
setx GITGUARDIAN_API_KEY "<your_api_key>"
# or in current session
$env:GITGUARDIAN_API_KEY = '<your_api_key>'

# run ggshield scan (example)
ggshield scan repo --output-format json > ggshield-report.json
```

## Summarize and redact findings
A parser is included to create a concise redacted summary:

```powershell
python tools\parse_trufflehog.py
# Outputs: trufflehog-summary.json and trufflehog-summary.txt
```

The parser redacts potentially sensitive strings (keeps a small prefix/suffix and masks the middle) and groups findings by reason/detector.

## CI notes
- The GitHub workflow uses least-privilege permissions for the token.
- TruffleHog results and Dependency-Check reports are uploaded as artifacts for review.
- The workflow will fail if TruffleHog produces verified secrets or Dependency-Check finds CVSS >= 7.

## Handling findings
1. Triage: open `trufflehog-summary.txt` and check grouped reasons. Many findings in this repo are false positives (e.g., code snippets from Stack Overflow).
2. If you identify a real secret:
   - Rotate/revoke the secret immediately.
   - Remove the secret from history (use tools like `git filter-repo`) and force-push cleaned history.
   - Re-run local scans and CI.
3. For false positives, add suppressions to `.github/workflows/suppression.xml` (dependency-check) or document exceptions.

## Triggering the workflow manually
You can trigger the workflow dispatch using a PAT with `repo` and `workflow` scopes. Example (PowerShell using curl):

```powershell
# set token in env variable first
$env:GITHUB_TOKEN = '<your_pat>'
$body = '{"ref":"main"}'
curl -X POST -H "Authorization: token $env:GITHUB_TOKEN" -H "Accept: application/vnd.github+json" -d $body "https://api.github.com/repos/MarchingTorpedo/Stackoverflow_question_quality_analysis/actions/workflows/security-scan.yml/dispatches"
```

Note: keep PATs and API keys out of the repository.

