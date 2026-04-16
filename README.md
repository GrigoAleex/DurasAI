# Local Assist

Local Assist is a local-first voice assistant intended as an AI replacement for Siri-style interactions.
It records your voice, transcribes with `whisper.cpp`, sends text to a local OpenAI-compatible LLM endpoint, and speaks the reply with Piper TTS.

This project is not affiliated with Apple.

## Features

- Hold-to-talk desktop UI (`gui_app.py`)
- CLI interaction mode (`main.py`)
- Local speech-to-text via `whisper-cli`
- Local text generation through a chat completion API
- Local text-to-speech playback with Piper
- Runtime configuration via environment variables

## Architecture

1. Record microphone input to WAV.
2. Transcribe WAV with `whisper-cli`.
3. Send transcript to LLM API (`/v1/chat/completions`).
4. Synthesize answer to speech with Piper.
5. Play audio through your default output device.

## Prerequisites

- macOS (current recording command uses AVFoundation)
- Python 3.11+
- `ffmpeg`
- `whisper-cli` binary and Whisper model file
- Piper voice model (`.onnx` and `.onnx.json`)
- Local LLM server exposing an OpenAI-compatible endpoint

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create and load env vars:

```bash
cp .env.example .env
set -a
source .env
set +a
```

Update `.env` paths for your local model locations.

## Run

GUI:

```bash
python gui_app.py
```

CLI:

```bash
python main.py
```

## GitHub-Ready Defaults Included

- `.gitignore` excludes virtual envs, model files, audio outputs, and local blobs
- `requirements.txt` for Python dependencies
- `.env.example` for portable configuration
- Basic CI workflow for import/syntax validation
- MIT license

## Suggested Repository Naming

- `local-assist`
- `siri-replacement-ai`
- `private-voice-assistant`

## Push To GitHub

```bash
git init -b main
git add .
git commit -m "Initial commit: local voice assistant"
gh repo create local-assist --source=. --private --remote=origin --push
```

You can replace `--private` with `--public` if desired.
