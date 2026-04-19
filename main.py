import io
import re
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
from piper import PiperVoice

from config import (
    INPUT_WAV,
    INTERNET_ENABLED,
    INTERNET_MODE,
    INTERNET_PROVIDER,
    INTERNET_TIMEOUT_SEC,
    INTERNET_TOP_K,
    LLM_API_URL,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    PIPER_CONFIG,
    PIPER_MODEL,
    RECORD_SECONDS,
    SYSTEM_PROMPT,
    TAVILY_API_KEY,
    TAVILY_SEARCH_DEPTH,
    WHISPER_BIN,
    WHISPER_LANGUAGE,
    WHISPER_MODEL,
)
from internet_connector import Source, search as search_internet

Path(INPUT_WAV).parent.mkdir(parents=True, exist_ok=True)

_voice = None
_AUTO_WEB_HINTS = {
    "today",
    "latest",
    "current",
    "currently",
    "news",
    "weather",
    "forecast",
    "price",
    "stock",
    "market",
    "release",
    "version",
    "update",
    "breaking",
    "result",
    "score",
}

@dataclass(frozen=True)
class AssistantResponse:
    answer: str
    sources: list[Source]


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


def _should_use_internet(text):
    if not INTERNET_ENABLED:
        return False

    if INTERNET_MODE == "off":
        return False

    if INTERNET_MODE == "always":
        return True

    if INTERNET_MODE != "auto":
        return False

    lowered = text.lower()
    if any(hint in lowered for hint in _AUTO_WEB_HINTS):
        return True

    return bool(re.search(r"\b(19|20)\d{2}\b", lowered))


def _lookup_sources(query):
    if INTERNET_PROVIDER != "tavily":
        return []

    try:
        return search_internet(
            query=query,
            top_k=INTERNET_TOP_K,
            timeout=INTERNET_TIMEOUT_SEC,
            api_key=TAVILY_API_KEY,
            search_depth=TAVILY_SEARCH_DEPTH,
        )
    except Exception:
        return []


def _build_web_context_message(sources):
    lines = [
        "Web context is provided below.",
        "Use it only when relevant to the user request.",
        "If you use web context for factual claims, cite with bracketed ids like [1].",
        "Do not invent citations.",
        "",
        "Web sources:",
    ]

    for source in sources:
        title = source.title or source.url
        snippet = source.snippet or "No snippet available."
        lines.append(f"[{source.id}] {title}")
        lines.append(f"URL: {source.url}")
        lines.append(f"Snippet: {snippet}")

    return "\n".join(lines)


def format_assistant_output(response):
    answer = response.answer.strip()
    if not response.sources:
        return answer

    lines = [answer, "", "Sources:"]
    for source in response.sources:
        title = source.title or source.url
        lines.append(f"[{source.id}] {title} - {source.url}")

    return "\n".join(lines)


def ask_llm(text):
    user_text = text.strip()
    sources = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if _should_use_internet(user_text):
        sources = _lookup_sources(user_text)
        if sources:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "You can use supplemental web context in this conversation. "
                        "When it influences your answer, include bracket citations like [1]."
                    ),
                }
            )
            messages.append({"role": "system", "content": _build_web_context_message(sources)})

    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }

    r = requests.post(
        LLM_API_URL,
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    answer = data["choices"][0]["message"]["content"].strip()
    return AssistantResponse(answer=answer, sources=sources)

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
    response = ask_llm(user_text)
    print("ASSISTANT:", response.answer)

    if response.sources:
        print("SOURCES:")
        for source in response.sources:
            title = source.title or source.url
            print(f"[{source.id}] {title} - {source.url}")

    print("Speaking...")
    speak(response.answer)

if __name__ == "__main__":
    main()
