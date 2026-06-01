import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hhscout.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                salary TEXT,
                url TEXT NOT NULL,
                fit TEXT NOT NULL,
                reason TEXT,
                cover_letter TEXT NOT NULL,
                applied INTEGER NOT NULL DEFAULT 0,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def upsert_vacancy(row: dict) -> bool:
    """Returns True if this is a newly inserted vacancy."""
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        cur = conn.execute("SELECT id FROM vacancies WHERE id = ?", (row["id"],))
        exists = cur.fetchone()
        if exists:
            conn.execute(
                "UPDATE vacancies SET last_seen = ?, salary = COALESCE(?, salary) WHERE id = ?",
                (now, row.get("salary"), row["id"]),
            )
            conn.commit()
            return False
        conn.execute(
            """
            INSERT INTO vacancies (id, title, company, salary, url, fit, reason, cover_letter, applied, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                row["id"],
                row["title"],
                row.get("company") or "—",
                row.get("salary") or "—",
                row["url"],
                row["fit"],
                row.get("reason") or "",
                row["cover_letter"],
                now,
                now,
            ),
        )
        conn.commit()
        return True


def list_vacancies(*, only_new: bool = False, hide_applied: bool = False) -> list[dict]:
    clauses = []
    if only_new:
        clauses.append("date(first_seen) = date(last_seen)")
    if hide_applied:
        clauses.append("applied = 0")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM vacancies
            {where}
            ORDER BY
              CASE fit WHEN 'yes' THEN 0 WHEN 'partial' THEN 1 ELSE 2 END,
              first_seen DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def mark_applied(vacancy_id: str) -> None:
    with connect() as conn:
        conn.execute("UPDATE vacancies SET applied = 1 WHERE id = ?", (vacancy_id,))
        conn.commit()


def stats() -> dict:
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM vacancies").fetchone()[0]
        applied = conn.execute("SELECT COUNT(*) FROM vacancies WHERE applied = 1").fetchone()[0]
        new_today = conn.execute(
            "SELECT COUNT(*) FROM vacancies WHERE date(first_seen) = date('now')"
        ).fetchone()[0]
    return {"total": total, "applied": applied, "new_today": new_today}
