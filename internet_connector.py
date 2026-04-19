from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import requests


@dataclass(frozen=True)
class Source:
    id: int
    title: str
    url: str
    snippet: str


class SearchProvider(Protocol):
    def search(self, query: str, top_k: int, timeout: float) -> list[Source]:
        ...


class DuckDuckGoProvider:
    API_URL = "https://api.duckduckgo.com/"

    def __init__(self, session: requests.Session | None = None):
        self._session = session or requests.Session()

    def search(self, query: str, top_k: int, timeout: float) -> list[Source]:
        normalized_query = query.strip()
        normalized_top_k = max(0, top_k)
        normalized_timeout = _normalize_timeout(timeout)

        if not normalized_query or normalized_top_k == 0:
            return []

        params = {
            "q": normalized_query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
            "no_redirect": "1",
        }

        try:
            response = self._session.get(self.API_URL, params=params, timeout=normalized_timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        return _build_sources(payload, normalized_top_k)


_DEFAULT_PROVIDER = DuckDuckGoProvider()


def search(query: str, top_k: int, timeout: float, provider: SearchProvider | None = None) -> list[Source]:
    active_provider = provider or _DEFAULT_PROVIDER
    return active_provider.search(query=query, top_k=top_k, timeout=timeout)


def _build_sources(payload: dict[str, Any], top_k: int) -> list[Source]:
    candidates: list[dict[str, str]] = []

    heading = _clean_text(payload.get("Heading"))
    abstract_url = _clean_text(payload.get("AbstractURL"))
    abstract_text = _clean_text(payload.get("AbstractText"))
    if abstract_url:
        title = heading or _title_from_text(abstract_text) or abstract_url
        candidates.append({"title": title, "url": abstract_url, "snippet": abstract_text})

    for item in payload.get("Results", []):
        if isinstance(item, dict):
            _append_candidate(candidates, item.get("FirstURL"), item.get("Text"))

    _collect_related_topics(payload.get("RelatedTopics", []), candidates)

    sources: list[Source] = []
    seen_urls: set[str] = set()
    for candidate in candidates:
        url = candidate["url"]
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        sources.append(
            Source(
                id=len(sources) + 1,
                title=candidate["title"],
                url=url,
                snippet=candidate["snippet"],
            )
        )

        if len(sources) >= top_k:
            break

    return sources


def _collect_related_topics(items: list[Any], candidates: list[dict[str, str]]) -> None:
    for item in items:
        if not isinstance(item, dict):
            continue

        nested_topics = item.get("Topics")
        if isinstance(nested_topics, list):
            _collect_related_topics(nested_topics, candidates)
            continue

        _append_candidate(candidates, item.get("FirstURL"), item.get("Text"))


def _append_candidate(candidates: list[dict[str, str]], url_value: Any, text_value: Any) -> None:
    url = _clean_text(url_value)
    text = _clean_text(text_value)
    if not url:
        return

    title = _title_from_text(text) or url
    snippet = _snippet_from_text(text)
    candidates.append({"title": title, "url": url, "snippet": snippet})


def _title_from_text(text: str) -> str:
    if not text:
        return ""

    if " - " in text:
        return text.split(" - ", 1)[0].strip()

    return text


def _snippet_from_text(text: str) -> str:
    if not text:
        return ""

    if " - " in text:
        return text.split(" - ", 1)[1].strip()

    return text


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return " ".join(value.split()).strip()

def _normalize_timeout(timeout: float) -> float:
    if timeout <= 0:
        return 10.0

    return timeout
