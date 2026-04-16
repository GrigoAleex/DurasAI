import os


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


WHISPER_BIN = os.getenv("WHISPER_BIN", "whisper-cli")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "./models/whisper/ggml-base.bin")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")

LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:8080/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = _as_float(os.getenv("LLM_TEMPERATURE"), 0.7)
LLM_MAX_TOKENS = _as_int(os.getenv("LLM_MAX_TOKENS"), 128)

PIPER_MODEL = os.getenv("PIPER_MODEL", "./models/piper/en_GB-jenny_dioco-medium.onnx")
PIPER_CONFIG = os.getenv("PIPER_CONFIG", "./models/piper/en_GB-jenny_dioco-medium.onnx.json")

INPUT_WAV = os.getenv("INPUT_WAV", "./audio/input.wav")
OUTPUT_WAV = os.getenv("OUTPUT_WAV", "./audio/output.wav")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a concise, helpful voice assistant.")
RECORD_SECONDS = _as_int(os.getenv("RECORD_SECONDS"), 5)
