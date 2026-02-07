"""External tool wrappers: search and summarization."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class SearchResult:
    """Search result normalized for downstream ranking."""

    title: str
    url: str
    snippet: str
    year: int | None


class SearchTool(Protocol):
    """Protocol for interchangeable web search providers."""

    def search(self, query: str, max_results: int = 12) -> list[SearchResult]:
        """Return normalized search results."""


def extract_year(text: str) -> int | None:
    """Extract a plausible publication year from text."""
    match = re.search(r"\b(20[1-2][0-9])\b", text)
    return int(match.group(1)) if match else None


class GoogleProgrammableSearchTool:
    """Google Programmable Search API wrapper with free-tier support."""

    def __init__(self, api_key: str, cse_id: str) -> None:
        self.api_key = api_key
        self.cse_id = cse_id

    def search(self, query: str, max_results: int = 12) -> list[SearchResult]:
        if not self.api_key or not self.cse_id:
            return []

        from langchain_community.utilities import GoogleSearchAPIWrapper

        wrapper = GoogleSearchAPIWrapper(google_api_key=self.api_key, google_cse_id=self.cse_id)
        rows = wrapper.results(query, min(max_results, 10))
        results: list[SearchResult] = []
        for row in rows:
            title = row.get("title", "")
            url = row.get("link", "")
            snippet = row.get("snippet", "")
            year = extract_year(f"{title} {snippet} {url}")
            if title and url:
                results.append(SearchResult(title=title, url=url, snippet=snippet, year=year))
        return results


class DuckDuckGoSearchTool:
    """Fallback no-key search tool using DuckDuckGo's public interface."""

    def search(self, query: str, max_results: int = 12) -> list[SearchResult]:
        from ddgs import DDGS

        with DDGS() as ddgs:
            rows = ddgs.text(query, max_results=max_results)
            results: list[SearchResult] = []
            for row in rows:
                title = row.get("title", "")
                snippet = row.get("body", "")
                url = row.get("href", "")
                year = extract_year(f"{title} {snippet} {url}")
                if title and url:
                    results.append(SearchResult(title=title, url=url, snippet=snippet, year=year))
            return results


class OllamaSummarizer:
    """Summarizer backed by a local Ollama model."""

    def __init__(self, model: str) -> None:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_ollama import ChatOllama

        self.llm = ChatOllama(model=model, temperature=0)
        self.prompt = ChatPromptTemplate.from_template(
            """
You are summarizing AI research papers for an agriculture-focused analyst.
Given title, snippet, url and year, produce a concise summary with:
1) Problem statement
2) Method overview
3) Why it matters for agriculture
4) One caveat
Keep it <=120 words.

Title: {title}
Snippet: {snippet}
URL: {url}
Year: {year}
            """.strip()
        )

    def summarize(self, item: SearchResult) -> str:
        """Summarize one normalized search result."""
        chain = self.prompt | self.llm
        response = chain.invoke(
            {
                "title": item.title,
                "snippet": item.snippet,
                "url": item.url,
                "year": item.year or "Unknown",
            }
        )
        return response.content if isinstance(response.content, str) else str(response.content)


def pick_top_recent(results: list[SearchResult], k: int = 3) -> list[SearchResult]:
    """Heuristic selection of top-k AI+agriculture paper-like links by recency."""
    filtered = [
        result
        for result in results
        if any(
            tag in (result.title + " " + result.snippet).lower()
            for tag in ["paper", "arxiv", "research", "journal"]
        )
    ]
    ranked = sorted(filtered or results, key=lambda item: (item.year or 0), reverse=True)
    return ranked[:k]
