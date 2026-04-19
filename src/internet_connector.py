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
    def search(
        self,
        query: str,
        top_k: int,
        timeout: float,
        *,
        api_key: str,
        search_depth: str,
    ) -> list[Source]:
        ...


class TavilyProvider:
    API_URL = "https://api.tavily.com/search"

    def __init__(self, session: requests.Session | None = None):
        self._session = session or requests.Session()

    def search(
        self,
        query: str,
        top_k: int,
        timeout: float,
        *,
        api_key: str,
        search_depth: str,
    ) -> list[Source]:
        normalized_query = query.strip()
        normalized_top_k = _normalize_top_k(top_k)
        normalized_timeout = _normalize_timeout(timeout)
        normalized_api_key = _clean_text(api_key)
        normalized_search_depth = _normalize_search_depth(search_depth)

        if not normalized_query or normalized_top_k == 0:
            return []

        if not normalized_api_key:
            return []

        payload = {
            "api_key": normalized_api_key,
            "query": normalized_query,
            "search_depth": normalized_search_depth,
            "max_results": normalized_top_k,
            "include_answer": False,
            "include_raw_content": False,
        }

        try:
            response = self._session.post(self.API_URL, json=payload, timeout=normalized_timeout)
            response.raise_for_status()
            response_payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        return _build_sources(response_payload.get("results"), normalized_top_k)


_DEFAULT_PROVIDER = TavilyProvider()


def search(
    query: str,
    top_k: int,
    timeout: float,
    *,
    api_key: str,
    search_depth: str,
    provider: SearchProvider | None = None,
) -> list[Source]:
    active_provider = provider or _DEFAULT_PROVIDER
    return active_provider.search(
        query=query,
        top_k=top_k,
        timeout=timeout,
        api_key=api_key,
        search_depth=search_depth,
    )


def _build_sources(results: Any, top_k: int) -> list[Source]:
    if not isinstance(results, list):
        return []

    sources: list[Source] = []
    seen_urls: set[str] = set()

    for item in results:
        if not isinstance(item, dict):
            continue

        url = _clean_text(item.get("url"))
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        title = _clean_text(item.get("title")) or url
        snippet = _clean_text(item.get("content"))
        sources.append(
            Source(
                id=len(sources) + 1,
                title=title,
                url=url,
                snippet=snippet,
            )
        )

        if len(sources) >= top_k:
            break

    return sources


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return " ".join(value.split()).strip()


def _normalize_top_k(top_k: int) -> int:
    try:
        normalized = int(top_k)
    except (TypeError, ValueError):
        return 0

    return max(0, normalized)


def _normalize_timeout(timeout: float) -> float:
    try:
        normalized = float(timeout)
    except (TypeError, ValueError):
        return 10.0

    if normalized <= 0:
        return 10.0

    return normalized


def _normalize_search_depth(search_depth: str) -> str:
    normalized = _clean_text(search_depth).lower()
    if normalized in {"basic", "advanced"}:
        return normalized

    return "basic"
