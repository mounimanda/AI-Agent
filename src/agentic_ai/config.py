"""Configuration for the agentic AI app."""

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    """Application settings loaded from environment variables."""

    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    sqlite_path: str = os.getenv("SQLITE_PATH", "agent_runs.db")
    search_max_results: int = int(os.getenv("SEARCH_MAX_RESULTS", "12"))
    search_provider: str = os.getenv("SEARCH_PROVIDER", "google")
    google_cse_id: str = os.getenv("GOOGLE_CSE_ID", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")


settings = Settings()
