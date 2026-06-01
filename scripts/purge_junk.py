# -*- coding: utf-8 -*-
"""Remove vacancies that no longer pass the scorer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db import connect, init_db
from app.profile_loader import load_profile
from app.scorer import score_vacancy


def main() -> None:
    init_db()
    profile = load_profile()
    removed = 0
    with connect() as conn:
        rows = conn.execute("SELECT id, title, company, salary, applied FROM vacancies").fetchall()
        for row in rows:
            fit, reason = score_vacancy(
                title=row["title"],
                company=row["company"] or "",
                salary=row["salary"] or "",
                description="",
                profile=profile,
            )
            if fit == "no":
                conn.execute("DELETE FROM vacancies WHERE id = ?", (row["id"],))
                removed += 1
                print(f"removed {row['id']}: {row['title'][:60]} ({reason})")
        conn.commit()
    print(f"removed total: {removed}")


if __name__ == "__main__":
    main()
