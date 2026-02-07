# Agentic AI: Autonomous Agriculture Research Assistant

This project implements a **stateful LangChain-based agent** that can autonomously:
1. Plan a multi-step workflow
2. Search for recent AI-agriculture research papers
3. Summarize top 3 papers using a local Ollama model
4. Store outputs in SQLite in structured format

## Tech Stack
- Python + LangChain
- Search: Google Programmable Search API (free tier) with DuckDuckGo fallback
- Summarization: Ollama (local)
- Storage: SQLite
- Interfaces: CLI + Streamlit web app

## Project Structure
- `src/agentic_ai/agent.py` - orchestrator and agent flow
- `src/agentic_ai/tools.py` - search + summarization tool wrappers
- `src/agentic_ai/storage.py` - persistent user-specific state
- `src/agentic_ai/cli.py` - CLI interface
- `src/agentic_ai/webapp.py` - web interface
- `docs/architecture.md` - architecture diagram

## Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Make sure Ollama is running locally and your model is available:
```bash
ollama pull llama3.1
ollama serve
```

## Search Provider Configuration
Google Programmable Search has a free tier (100 queries/day). Configure it with:
```bash
export SEARCH_PROVIDER=google
export GOOGLE_API_KEY=<your-google-api-key>
export GOOGLE_CSE_ID=<your-programmable-search-engine-id>
```

If Google credentials are missing or quota is exhausted, the agent automatically falls back to DuckDuckGo.

Optional environment variables:
```bash
export OLLAMA_MODEL=llama3.1
export SQLITE_PATH=agent_runs.db
export SEARCH_MAX_RESULTS=12
```

## Run CLI
```bash
PYTHONPATH=src python -m agentic_ai.cli run --user-id alice
```

## Run Web App
```bash
PYTHONPATH=src streamlit run src/agentic_ai/webapp.py
```

## Agent Workflow
1. Build plan from user goal.
2. Execute search tool for agriculture + AI papers.
3. Select top 3 recent candidates.
4. Summarize each paper via Ollama.
5. Persist job + papers by `user_id` in SQLite.
6. Return structured JSON output.

## Sample Output (CLI)
```json
{
  "job_id": "2fbcf4ef-ae27-4071-8c4e-5dc3d24ec8f7",
  "user_id": "alice",
  "goal": "Find the top 3 recent AI research papers on agriculture...",
  "status": "completed",
  "plan": [
    "Interpret goal...",
    "Search the web for recent AI research papers related to agriculture",
    "Rank and select the top 3 recent papers",
    "Summarize each paper with an agriculture impact lens",
    "Store result in SQLite and return structured output"
  ],
  "papers": [
    {
      "rank_order": 1,
      "title": "Example Paper",
      "url": "https://arxiv.org/abs/....",
      "year": 2025,
      "summary": "..."
    }
  ]
}
```

## Sample Output (Web app)
![alt text](<Screenshot 2026-02-07 at 11.28.58 AM.png>)