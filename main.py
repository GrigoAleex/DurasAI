import io
import subprocess
import wave
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
from piper import PiperVoice

from config import (
    INPUT_WAV,
    LLM_API_URL,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    PIPER_CONFIG,
    PIPER_MODEL,
    RECORD_SECONDS,
    SYSTEM_PROMPT,
    WHISPER_BIN,
    WHISPER_LANGUAGE,
    WHISPER_MODEL,
)

Path(INPUT_WAV).parent.mkdir(parents=True, exist_ok=True)

_voice = None


def _get_voice():
    global _voice

    if _voice is not None:
        return _voice

    load_kwargs = {"model_path": PIPER_MODEL}
    if PIPER_CONFIG:
        load_kwargs["config_path"] = PIPER_CONFIG
    _voice = PiperVoice.load(**load_kwargs)
    return _voice

def record_audio():
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "avfoundation",
        "-i", ":0",
        "-t", str(RECORD_SECONDS),
        "-ac", "1",
        "-ar", "16000",
        INPUT_WAV
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def transcribe():
    cmd = [
        WHISPER_BIN,
        "-m", WHISPER_MODEL,
        "-f", INPUT_WAV,
        "-l", WHISPER_LANGUAGE,
        "-nt",
        "-np"
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""

def ask_llm(text):
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS
    }

    r = requests.post(
        LLM_API_URL,
        json=payload,
        timeout=120
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

def speak(text):
    voice = _get_voice()
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    buffer.seek(0)

    with wave.open(buffer, "rb") as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        sample_rate = wav_file.getframerate()

    sd.play(audio, samplerate=sample_rate)
    sd.wait()

def main():
    print("Recording...")
    record_audio()

    print("Transcribing...")
    user_text = transcribe()
    print("USER:", user_text)

    if not user_text:
        print("No speech detected.")
        return

    print("Generating...")
    answer = ask_llm(user_text)
    print("ASSISTANT:", answer)

    print("Speaking...")
    speak(answer)

if __name__ == "__main__":
    main()
