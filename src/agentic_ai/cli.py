"""CLI entrypoint for running the autonomous agent."""

from __future__ import annotations

import json

import typer

from .agent import AgricultureResearchAgent
from .config import settings

app = typer.Typer(help="Agentic AI CLI")


@app.command()
def run(
    user_id: str = typer.Option(..., help="User identifier for stateful execution"),
    goal: str = typer.Option(
        "Find the top 3 recent AI research papers on agriculture, summarize them, and store output.",
        help="Goal to execute",
    ),
) -> None:
    """Run the full workflow for a user and print structured JSON output."""
    agent = AgricultureResearchAgent(settings)
    result = agent.run(user_id=user_id, goal=goal)
    typer.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    app()
