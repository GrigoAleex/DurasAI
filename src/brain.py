import logging
import re
import time
import requests
from collections.abc import Callable

from dataclasses import dataclass
from internet_connector import Source, search as search_internet

logger = logging.getLogger(__name__)

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


@dataclass(frozen=True)
class _BrainConfig:
    system_prompt: str
    llm_api_url: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    internet_mode: str
    internet_provider: str
    internet_timeout_sec: float
    internet_top_k: int
    tavily_api_key: str
    tavily_search_depth: str


class Brain:
    def __init__(self, config: _BrainConfig):
        self._config = config

    def ask(self, user_input: str) -> AssistantResponse:
        started_at = time.perf_counter()
        user_text = user_input.strip()
        sources: list[Source] = []
        messages = [{"role": "system", "content": self._config.system_prompt}]

        logger.info("Brain ask started: model=%s", self._config.llm_model)

        if self._should_use_internet(user_text):
            if sources := self._lookup_sources(user_text):
                logger.info("Internet context attached: sources=%d", len(sources))
                messages += [
                    {"role": "system", "content": (
                        "You have supplemental web context for this conversation. "
                        "When it influences your answer, cite sources with brackets like [1]."
                    )},
                    {"role": "system", "content": self._build_web_context_message(sources)},
                ]
            else:
                logger.debug("Internet lookup returned no sources")

        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self._config.llm_model,
            "messages": messages,
            "temperature": self._config.llm_temperature,
            "max_tokens": self._config.llm_max_tokens,
        }

        logger.debug(
            "Brain LLM request prepared: url=%s messages=%d max_tokens=%d temperature=%s",
            self._config.llm_api_url,
            len(messages),
            self._config.llm_max_tokens,
            self._config.llm_temperature,
        )

        try:
            response = requests.post(
                self._config.llm_api_url,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"].strip()
        except Exception:
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            logger.exception("Brain ask failed after %dms", elapsed_ms)
            raise

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        logger.info(
            "Brain ask completed: sources_len=%d answer_len=%d elapsed_ms=%d",
            len(sources),
            len(answer),
            elapsed_ms,
        )

        return AssistantResponse(answer=answer, sources=sources)

    def _should_use_internet(self, text: str) -> bool:
        handlers: dict[str, Callable[[str], bool]] = {
            "off":    lambda _: False,
            "always": lambda _: True,
            "auto": self._auto_internet
        }

        mode = self._config.internet_mode
        lowered = text.lower()

        if mode in handlers:
            result = handlers[mode](lowered)
            logger.debug("Internet mode %r → %s", mode, result)
            return result
        
        logger.warning("Unknown internet mode %r — defaulting to off", mode)
        return False
    
    # Maybe use pyahocorasick for searching hints
    def _auto_internet(self, lowered: str) -> bool:
        _YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

        trigger = (
            "keyword hint" if any(h in lowered for h in _AUTO_WEB_HINTS) else
            "year pattern" if _YEAR_RE.search(lowered) else
            None
        )
        
        logger.debug("Internet auto mode: %s", f"triggered by {trigger}" if trigger else "no trigger")
        return trigger is not None

    def _lookup_sources(self, query: str) -> list[Source]:
        if self._config.internet_provider != "tavily":
            logger.debug("Unsupported internet provider: %s", self._config.internet_provider)
            return []

        try:
            sources = search_internet(
                query=query,
                top_k=self._config.internet_top_k,
                timeout=self._config.internet_timeout_sec,
                api_key=self._config.tavily_api_key,
                search_depth=self._config.tavily_search_depth,
            )
            logger.debug("Internet lookup completed: provider=tavily sources_len=%d", len(sources))
            return sources
        except Exception:
            logger.warning("Internet lookup failed: provider=tavily", exc_info=True)
            return []

    def _build_web_context_message(self, sources: list[Source]) -> str:
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


class BrainBuilder:
    def __init__(self):
        self._system_prompt = "You are a concise, helpful voice assistant."
        self._llm_api_url = "http://127.0.0.1:8080/v1/chat/completions"
        self._llm_model = "mistral"
        self._llm_temperature = 0.7
        self._llm_max_tokens = 128
        self._internet_mode = "auto"
        self._internet_provider = "tavily"
        self._internet_timeout_sec = 6.0
        self._internet_top_k = 3
        self._tavily_api_key = ""
        self._tavily_search_depth = "basic"

    def with_system_prompt(self, value: str) -> "BrainBuilder":
        self._system_prompt = value
        return self

    def with_llm_api_url(self, value: str) -> "BrainBuilder":
        self._llm_api_url = value
        return self

    def with_llm_model(self, value: str) -> "BrainBuilder":
        self._llm_model = value
        return self

    def with_llm_temperature(self, value: float) -> "BrainBuilder":
        self._llm_temperature = value
        return self

    def with_llm_max_tokens(self, value: int) -> "BrainBuilder":
        self._llm_max_tokens = value
        return self

    def with_internet_mode(self, value: str) -> "BrainBuilder":
        self._internet_mode = value
        return self

    def with_internet_provider(self, value: str) -> "BrainBuilder":
        self._internet_provider = value
        return self

    def with_internet_timeout_sec(self, value: float) -> "BrainBuilder":
        self._internet_timeout_sec = value
        return self

    def with_internet_top_k(self, value: int) -> "BrainBuilder":
        self._internet_top_k = value
        return self

    def with_tavily_api_key(self, value: str) -> "BrainBuilder":
        self._tavily_api_key = value
        return self

    def with_tavily_search_depth(self, value: str) -> "BrainBuilder":
        self._tavily_search_depth = value
        return self

    def build(self) -> Brain:
        config = _BrainConfig(
            system_prompt=self._system_prompt,
            llm_api_url=self._llm_api_url,
            llm_model=self._llm_model,
            llm_temperature=self._llm_temperature,
            llm_max_tokens=self._llm_max_tokens,
            internet_mode=self._internet_mode,
            internet_provider=self._internet_provider,
            internet_timeout_sec=self._internet_timeout_sec,
            internet_top_k=self._internet_top_k,
            tavily_api_key=self._tavily_api_key,
            tavily_search_depth=self._tavily_search_depth,
        )
        return Brain(config)
