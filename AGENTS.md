# AGENTS.md

## Scope
- This repo is a single Python app (no package/workspace split): `main.py` (CLI), `gui_app.py` (Tk GUI), `config.py` (env-backed settings).

## Setup and run
- Use a local venv and install from `requirements.txt`.
- Load env vars in the shell before running (`.env` is not auto-loaded by code): `set -a; source .env; set +a`.
- GUI entrypoint: `python gui_app.py`.
- CLI entrypoint: `python main.py`.

## Verification
- CI only checks import/syntax compilation (no pytest/lint/typecheck pipeline configured).
- Run the CI-equivalent check locally: `python -m py_compile config.py main.py gui_app.py`.
- CI uses Python 3.12 (`.github/workflows/ci.yml`); prefer 3.12 when debugging CI-only issues.

## AI-ready workflow rules
- Use Conventional Commits for every commit created in this repo (including OpenCode-authored commits), even when no CI check is present.
- Allowed commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Store AI-generated plans in `opencode/plans/`; plan files there are intentionally gitignored and should not be committed.

## Repo-specific gotchas
- `main.py` recording path is macOS-specific (`ffmpeg -f avfoundation -i :0`); changes here can break CLI on non-macOS.
- `gui_app.py` reuses `transcribe()`, `ask_llm()`, and `speak()` from `main.py`; shared pipeline changes affect both interfaces.
- Tkinter UI updates from background work must stay on the main thread via `self.after(...)`.
- If you add or rename env vars in `config.py`, update both `.env.example` and `README.md` in the same change.
- Treat model/audio outputs as local artifacts (`models/`, `audio/`, `blobs/`, `.env` are intended to stay out of PRs).
