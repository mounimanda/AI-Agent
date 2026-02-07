"""Agent workflow orchestration built with LangChain-compatible tools."""

from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4

from agentic_ai.config import Settings
from agentic_ai.storage import PaperRecord, SQLiteStore
from agentic_ai.tools import (
    DuckDuckGoSearchTool,
    GoogleProgrammableSearchTool,
    OllamaSummarizer,
    SearchTool,
    pick_top_recent,
)


class AgricultureResearchAgent:
    """Autonomous agent for finding, summarizing, and storing research papers."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = SQLiteStore(settings.sqlite_path)
        self.search_tool = self._build_search_tool()
        self.summarizer = OllamaSummarizer(settings.ollama_model)

    def _build_search_tool(self) -> SearchTool:
        """Build search provider with fallback behavior."""
        if self.settings.search_provider.lower() == "google":
            return GoogleProgrammableSearchTool(
                api_key=self.settings.google_api_key,
                cse_id=self.settings.google_cse_id,
            )
        return DuckDuckGoSearchTool()

    def build_plan(self, goal: str) -> list[str]:
        """Return deterministic decomposition for the requested goal."""
        return [
            f"Interpret goal: {goal}",
            "Search the web for recent AI research papers related to agriculture",
            "Rank and select the top 3 recent papers",
            "Summarize each paper with an agriculture impact lens",
            "Store result in SQLite and return structured output",
        ]

    def run(self, user_id: str, goal: str) -> dict:
        """Execute the full multi-step workflow with persistent state."""
        job_id = str(uuid4())
        plan = self.build_plan(goal)
        self.store.create_job(job_id=job_id, user_id=user_id, goal=goal, plan=plan)

        query = "recent AI research papers in agriculture arxiv journal"
        raw_results = self.search_tool.search(query=query, max_results=self.settings.search_max_results)
        if not raw_results and self.settings.search_provider.lower() == "google":
            raw_results = DuckDuckGoSearchTool().search(
                query=query,
                max_results=self.settings.search_max_results,
            )

        selected = pick_top_recent(raw_results, k=3)
        papers: list[PaperRecord] = []
        for item in selected:
            summary = self.summarizer.summarize(item)
            papers.append(
                PaperRecord(
                    title=item.title,
                    url=item.url,
                    year=item.year,
                    summary=summary,
                    raw=asdict(item),
                )
            )

        self.store.store_papers(job_id, papers)
        self.store.update_job_status(job_id, "completed")
        return self.store.fetch_job_report(job_id)
