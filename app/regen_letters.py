"""Regenerate cover letters via DeepSeek PRO."""
from __future__ import annotations

import sys
import time

from app.collector import fetch_vacancy_description
from app.db import connect, init_db
from app.letters import generate_cover_letter, is_bad_letter, is_complete_letter
from app.profile_loader import load_profile


def regen_all(
    *,
    skip_applied: bool = True,
    only_bad: bool = False,
    only_incomplete: bool = False,
    limit: int | None = None,
) -> dict:
    init_db()
    profile = load_profile()
    delay = profile.get("letter_delay_sec", 1.2)

    clauses = []
    if skip_applied:
        clauses.append("applied = 0")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT id, title, company, salary, url, cover_letter FROM vacancies {where} ORDER BY first_seen DESC"
    if limit:
        sql += f" LIMIT {limit}"

    with connect() as conn:
        rows = conn.execute(sql).fetchall()

    if only_bad:
        rows = [r for r in rows if is_bad_letter(r["cover_letter"] or "")]
    if only_incomplete:
        rows = [r for r in rows if not is_complete_letter(r["cover_letter"] or "")]

    updated = 0
    failed = 0
    for row in rows:
        vid = row["id"]
        title, company, salary, url = row["title"], row["company"], row["salary"], row["url"]
        try:
            desc = fetch_vacancy_description(url)
            time.sleep(profile.get("request_delay_sec", 0.6))
            letter = generate_cover_letter(
                title=title,
                company=company or "—",
                salary=salary or "—",
                description=desc,
                profile=profile,
            )
            with connect() as conn:
                conn.execute("UPDATE vacancies SET cover_letter = ? WHERE id = ?", (letter, vid))
                conn.commit()
            updated += 1
            print(f"  [{updated}/{len(rows)}] OK {title[:55]}", flush=True)
        except Exception as e:
            failed += 1
            print(f"  FAIL [{title[:40]}]: {e}", flush=True)
        time.sleep(delay)

    return {"updated": updated, "failed": failed, "total": len(rows)}


if __name__ == "__main__":
    skip = "--all" not in sys.argv
    only_bad = "--only-bad" in sys.argv
    only_incomplete = "--incomplete" in sys.argv
    print(regen_all(skip_applied=skip, only_bad=only_bad, only_incomplete=only_incomplete))
