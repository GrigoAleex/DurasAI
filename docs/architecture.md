# Current Architecture

> [!WARNING]  
> Under work

## Overview

DurasAI is a local-first voice assistant with two interfaces:

- CLI entrypoint: `src/main.py`
- GUI entrypoint: `src/gui_app.py`

Both interfaces use the same processing pipeline:

1. Capture user audio.
2. Transcribe with `whisper-cli`.
3. Optionally fetch web sources for time-sensitive or factual questions.
4. Send transcript (and optional web context) to an OpenAI-compatible chat endpoint.
5. Synthesize answer with Piper TTS.
6. Play output audio.

## Runtime flow

```text
User audio -> WAV -> whisper-cli -> transcript -> (optional web lookup) -> LLM API -> answer text -> Piper -> speaker
```

## Component responsibilities

- `src/config.py`
  - Single source of runtime settings from environment variables.
  - Applies numeric parsing with safe defaults.
  - Controls internet connector behavior with `INTERNET_*` settings.

- `src/config_utils.py`
  - Shared parsing helpers for env-backed runtime settings.

- `src/internet_connector.py`
  - Defines provider contract for web search.
  - Implements Tavily Search API lookup.
  - Normalizes results into `Source` records and fails closed to empty results.

- `src/brain.py`
  - LLM orchestration and optional web augmentation.
  - `Brain.ask(user_input)` is the shared request path for both CLI and GUI.
  - `BrainBuilder` configures `Brain` from runtime settings.

- `src/app_logging.py`
  - Initializes root logging for both app entrypoints.
  - Creates per-start log files at `logs/{timestamp}.log`.

- `src/main.py`
  - CLI orchestration pipeline.
  - CLI recording currently uses `ffmpeg -f avfoundation -i :0` (macOS specific).
  - Builds a shared `brain` instance and hosts shared functions used by GUI: `transcribe()`, `speak()`, `format_assistant_output()`.

- `src/gui_app.py`
  - Tkinter hold-to-talk experience.
  - Uses `sounddevice.InputStream` for press-and-hold capture.
  - Runs long operations in a worker thread.
  - Marshals UI updates back to the main Tk thread with `self.after(...)`.

## Local artifacts and state

Runtime artifacts are local-only and excluded from git:

- `.env`
- `audio/`
- `logs/`
- `models/`
- `blobs/`

The repository keeps `.gitkeep` placeholders where needed.

## Verification baseline

Current CI and local baseline check:

```bash
python3 -m py_compile src/config.py src/config_utils.py src/internet_connector.py src/app_logging.py src/brain.py src/main.py src/gui_app.py
```

CI runs this on Python 3.12.
