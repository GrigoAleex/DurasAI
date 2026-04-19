import os
from dotenv import load_dotenv
import config_utils as conf

load_dotenv()

WHISPER_BIN = os.getenv("WHISPER_BIN", "whisper-cli")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "./models/whisper/ggml-base.bin")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")

LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:8080/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = conf._as_float(os.getenv("LLM_TEMPERATURE"), 0.7)
LLM_MAX_TOKENS = conf._as_int(os.getenv("LLM_MAX_TOKENS"), 128)

INTERNET_MODE = os.getenv("INTERNET_MODE", "auto").strip().lower()
INTERNET_PROVIDER = os.getenv("INTERNET_PROVIDER", "tavily").strip().lower()
INTERNET_TIMEOUT_SEC = conf._as_float(os.getenv("INTERNET_TIMEOUT_SEC"), 6.0)
INTERNET_TOP_K = conf._as_int(os.getenv("INTERNET_TOP_K"), 3)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
TAVILY_SEARCH_DEPTH = os.getenv("TAVILY_SEARCH_DEPTH", "basic")

PIPER_MODEL = os.getenv("PIPER_MODEL", "./models/piper/en_GB-jenny_dioco-medium.onnx")
PIPER_CONFIG = os.getenv("PIPER_CONFIG", "./models/piper/en_GB-jenny_dioco-medium.onnx.json")

INPUT_WAV = os.getenv("INPUT_WAV", "./audio/input.wav")
OUTPUT_WAV = os.getenv("OUTPUT_WAV", "./audio/output.wav")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a concise, helpful voice assistant.")
RECORD_SECONDS = conf._as_int(os.getenv("RECORD_SECONDS"), 5)
