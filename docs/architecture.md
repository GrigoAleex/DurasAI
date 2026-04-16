# Current Architecture

> [!WARNING]  
> Under work

## Overview

DurasAI is a local-first voice assistant with two interfaces:

- CLI entrypoint: `main.py`
- GUI entrypoint: `gui_app.py`

Both interfaces use the same processing pipeline:

1. Capture user audio.
2. Transcribe with `whisper-cli`.
3. Send transcript to an OpenAI-compatible chat endpoint.
4. Synthesize answer with Piper TTS.
5. Play output audio.

## Runtime flow

```text
User audio -> WAV -> whisper-cli -> transcript -> LLM API -> answer text -> Piper -> speaker
```

## Component responsibilities

- `config.py`
  - Single source of runtime settings from environment variables.
  - Applies numeric parsing with safe defaults.

- `main.py`
  - CLI orchestration pipeline.
  - CLI recording currently uses `ffmpeg -f avfoundation -i :0` (macOS specific).
  - Hosts shared functions used by GUI: `transcribe()`, `ask_llm()`, `speak()`.

- `gui_app.py`
  - Tkinter hold-to-talk experience.
  - Uses `sounddevice.InputStream` for press-and-hold capture.
  - Runs long operations in a worker thread.
  - Marshals UI updates back to the main Tk thread with `self.after(...)`.

## Local artifacts and state

Runtime artifacts are local-only and excluded from git:

- `.env`
- `audio/`
- `models/`
- `blobs/`

The repository keeps `.gitkeep` placeholders where needed.

## Verification baseline

Current CI and local baseline check:

```bash
python3 -m py_compile config.py main.py gui_app.py
```

CI runs this on Python 3.12.
