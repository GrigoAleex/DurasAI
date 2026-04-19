# Contributing to DurasAI

Thanks for helping build a lightweight, local-first AI assistant with a high quality bar.

## Project principles

- Keep it practical and fast: avoid unnecessary complexity.
- Prefer small, focused pull requests.
- No slop: every change should be understandable and intentional.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Run the app:

```bash
python main.py
python gui_app.py
```

Optional internet connector settings in `.env`:

```bash
INTERNET_ENABLED=true
INTERNET_MODE=auto
INTERNET_PROVIDER=duckduckgo
INTERNET_TIMEOUT_SEC=6
INTERNET_TOP_K=3
```

## Required before opening a PR

1. Verify your change locally.
2. Run the project check:

```bash
python3 -m py_compile config.py main.py gui_app.py
```

3. Test the affected flow(s) end-to-end (CLI, GUI, or both depending on your change).
4. If the change impacts performance or resource usage, include measurements when possible.
5. Document the implementation in two places:
   - PR description (what changed, why, and how you validated it)
   - `docs/` directory (create/update docs as part of the same PR)

## PR ownership and accountability

- The person opening a PR owns it even after merge.
- Address review feedback, update tests/docs, and keep the PR merge-ready.
- If a contributor intentionally submits a breaking or harmful change, they may be excluded from future project development.

## AI-assisted contributions

- AI-assisted coding is allowed. 
- The submitter is fully responsible for correctness, testing, and maintainability.
- AI-generated code must be reviewed by the contributor before submission.

## Commit format

Use Conventional Commits for every commit:

- `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

Example:

```text
feat(gui): add push-to-talk state indicator
```

## Issue triage

Issue labels and triage process are documented in `docs/triage.md`.

## Do not commit local artifacts

Never commit local-only files such as `.env`, `models/`, `audio/`, or `blobs/`.

## Security issues

For vulnerabilities, follow `SECURITY.md` and use private reporting.
