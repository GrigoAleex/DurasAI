import io
import logging
import subprocess
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from piper import PiperVoice

from app_logging import configure_logging
from brain import BrainBuilder
from config import (
    INPUT_WAV,
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

Path(INPUT_WAV).parent.mkdir(parents=True, exist_ok=True)

_voice = None
logger = logging.getLogger(__name__)
brain = (
    BrainBuilder()
    .with_system_prompt(SYSTEM_PROMPT)
    .with_llm_api_url(LLM_API_URL)
    .with_llm_model(LLM_MODEL)
    .with_llm_temperature(LLM_TEMPERATURE)
    .with_llm_max_tokens(LLM_MAX_TOKENS)
    .with_internet_mode(INTERNET_MODE)
    .with_internet_provider(INTERNET_PROVIDER)
    .with_internet_timeout_sec(INTERNET_TIMEOUT_SEC)
    .with_internet_top_k(INTERNET_TOP_K)
    .with_tavily_api_key(TAVILY_API_KEY)
    .with_tavily_search_depth(TAVILY_SEARCH_DEPTH)
    .build()
)


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


def format_assistant_output(response):
    answer = response.answer.strip()
    if not response.sources:
        return answer

    lines = [answer, "", "Sources:"]
    for source in response.sources:
        title = source.title or source.url
        lines.append(f"[{source.id}] {title} - {source.url}")

    return "\n".join(lines)

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
    log_path = configure_logging()
    logger.info("CLI started; log file: %s", log_path)

    logger.info("Recording...")
    record_audio()

    logger.info("Transcribing...")
    user_text = transcribe()
    logger.info("USER: %s", user_text)

    if not user_text:
        logger.warning("No speech detected.")
        return

    logger.info("Generating...")
    response = brain.ask(user_text)
    logger.info("ASSISTANT: %s", response.answer)

    if response.sources:
        logger.info("SOURCES:")
        for source in response.sources:
            title = source.title or source.url
            logger.info("[%s] %s - %s", source.id, title, source.url)

    logger.info("Speaking...")
    speak(response.answer)

if __name__ == "__main__":
    main()
