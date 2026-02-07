"""SQLite persistence for user-specific, stateful runs."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator


@dataclass(slots=True)
class PaperRecord:
    """Normalized paper record saved in the database."""

    title: str
    url: str
    year: int | None
    summary: str
    raw: dict[str, Any]


class SQLiteStore:
    """Simple SQLite-backed store with user and job-level state."""

    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self._init_db()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    rank_order INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    year INTEGER,
                    summary TEXT NOT NULL,
                    raw_json TEXT NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
                )
                """
            )

    def ensure_user(self, user_id: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, ?)",
                (user_id, datetime.utcnow().isoformat()),
            )

    def create_job(self, job_id: str, user_id: str, goal: str, plan: list[str]) -> None:
        self.ensure_user(user_id)
        now = datetime.utcnow().isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs (job_id, user_id, goal, plan_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'running', ?, ?)
                """,
                (job_id, user_id, goal, json.dumps(plan), now, now),
            )

    def update_job_status(self, job_id: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
                (status, datetime.utcnow().isoformat(), job_id),
            )

    def store_papers(self, job_id: str, papers: list[PaperRecord]) -> None:
        with self.connect() as conn:
            for idx, paper in enumerate(papers, start=1):
                conn.execute(
                    """
                    INSERT INTO papers (job_id, rank_order, title, url, year, summary, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        idx,
                        paper.title,
                        paper.url,
                        paper.year,
                        paper.summary,
                        json.dumps(paper.raw),
                    ),
                )

    def fetch_job_report(self, job_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            job = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            papers = conn.execute(
                "SELECT rank_order, title, url, year, summary FROM papers WHERE job_id = ? ORDER BY rank_order",
                (job_id,),
            ).fetchall()

        if job is None:
            raise ValueError(f"Unknown job_id: {job_id}")

        return {
            "job_id": job["job_id"],
            "user_id": job["user_id"],
            "goal": job["goal"],
            "status": job["status"],
            "plan": json.loads(job["plan_json"]),
            "papers": [dict(row) for row in papers],
        }
