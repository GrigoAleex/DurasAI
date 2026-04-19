import os
from dotenv import load_dotenv

load_dotenv()

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


def _as_bool(value, default):
    if value is None:
        return default

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _as_search_depth(value, default):
    if value is None:
        return default

    normalized = str(value).strip().lower()
    if normalized in {"basic", "advanced"}:
        return normalized

    return default


WHISPER_BIN = os.getenv("WHISPER_BIN", "whisper-cli")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "./models/whisper/ggml-base.bin")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")

LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:8080/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = _as_float(os.getenv("LLM_TEMPERATURE"), 0.7)
LLM_MAX_TOKENS = _as_int(os.getenv("LLM_MAX_TOKENS"), 128)

INTERNET_ENABLED = _as_bool(os.getenv("INTERNET_ENABLED"), False)
INTERNET_MODE = os.getenv("INTERNET_MODE", "auto").strip().lower()
INTERNET_PROVIDER = os.getenv("INTERNET_PROVIDER", "tavily").strip().lower()
INTERNET_TIMEOUT_SEC = _as_float(os.getenv("INTERNET_TIMEOUT_SEC"), 6.0)
INTERNET_TOP_K = _as_int(os.getenv("INTERNET_TOP_K"), 3)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
TAVILY_SEARCH_DEPTH = _as_search_depth(os.getenv("TAVILY_SEARCH_DEPTH"), "basic")

PIPER_MODEL = os.getenv("PIPER_MODEL", "./models/piper/en_GB-jenny_dioco-medium.onnx")
PIPER_CONFIG = os.getenv("PIPER_CONFIG", "./models/piper/en_GB-jenny_dioco-medium.onnx.json")

INPUT_WAV = os.getenv("INPUT_WAV", "./audio/input.wav")
OUTPUT_WAV = os.getenv("OUTPUT_WAV", "./audio/output.wav")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a concise, helpful voice assistant.")
RECORD_SECONDS = _as_int(os.getenv("RECORD_SECONDS"), 5)
