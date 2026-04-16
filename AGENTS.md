# AGENTS.md

## Repo Shape
- Single Python app (no package/workspace split): `main.py` (CLI), `gui_app.py` (Tk GUI), `config.py` (env-backed settings).
- `gui_app.py` reuses `transcribe()`, `ask_llm()`, and `speak()` from `main.py`; pipeline edits can break both interfaces.

## Setup and Run
- Use a local venv and install from `requirements.txt`.
- `.env` is not auto-loaded by code; load it in shell before running: `set -a; source .env; set +a`.
- Entrypoints: `python3 main.py` (CLI), `python3 gui_app.py` (GUI).

## Verification
- CI is compile-only on Python 3.12 (`.github/workflows/ci.yml`): `python -m py_compile config.py main.py gui_app.py`.
- Local CI-equivalent check: `python3 -m py_compile config.py main.py gui_app.py`.
- For behavior changes, test affected flow(s) end-to-end (CLI, GUI, or both). If performance/resource usage changes, include measurements.

## Workflow Rules
- Use Conventional Commits for every commit (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`).
- Store AI-generated plans in `opencode/plans/`; files there are intentionally gitignored and must not be committed.
- For implementation changes, update both the PR description and relevant `docs/` files in the same change.
- If env vars in `config.py` change, update `.env.example` and setup docs (`CONTRIBUTING.md`) in the same change.

## Gotchas
- CLI recording in `main.py` is macOS-specific (`ffmpeg -f avfoundation -i :0`).
- Tkinter UI updates from background work must go through `self.after(...)`.
- Never commit local artifacts/secrets: `.env`, `models/`, `audio/`, `blobs/`.

## Issue Triage
- Follow `docs/triage.md`.
- `infra` is a GitHub label for CI/tooling/repo infrastructure work, not a repository directory.
