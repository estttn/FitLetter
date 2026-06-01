# -*- coding: utf-8 -*-
"""Remove vacancies that require English."""
from __future__ import annotations

import time
import urllib.request
from urllib.error import HTTPError, URLError

from app.db import connect, init_db
from app.profile_loader import load_profile
from app.scorer import english_requirement_reason, score_vacancy
from app.scraper import parse_vacancy_description

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch_vacancy_description(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=40) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        return parse_vacancy_description(html)
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"Description fetch failed {url}: {e}")
        return ""


def purge_english(*, fetch_descriptions: bool = True) -> dict:
    init_db()
    profile = load_profile()
    delay = profile.get("request_delay_sec", 0.6)

    with connect() as conn:
        rows = conn.execute(
            "SELECT id, title, company, salary, url FROM vacancies ORDER BY first_seen DESC"
        ).fetchall()

    removed_title = 0
    removed_desc = 0
    kept = 0
    ids_to_delete: list[str] = []

    for row in rows:
        vid, title, url = row["id"], row["title"], row["url"]
        if english_requirement_reason(title):
            ids_to_delete.append(vid)
            removed_title += 1
            print(f"  - [title] {title[:70]}")
            continue

        if not fetch_descriptions:
            kept += 1
            continue

        description = fetch_vacancy_description(url)
        time.sleep(delay)
        fit, reason = score_vacancy(
            title=title,
            company=row["company"] or "",
            salary=row["salary"] or "",
            description=description,
            profile=profile,
        )
        if fit == "no" and reason and reason.startswith("english"):
            ids_to_delete.append(vid)
            removed_desc += 1
            print(f"  - [{reason}] {title[:70]}")
        else:
            kept += 1

    if ids_to_delete:
        with connect() as conn:
            placeholders = ",".join("?" * len(ids_to_delete))
            conn.execute(f"DELETE FROM vacancies WHERE id IN ({placeholders})", ids_to_delete)
            conn.commit()

    return {
        "total_before": len(rows),
        "removed_title": removed_title,
        "removed_desc": removed_desc,
        "removed": len(ids_to_delete),
        "kept": kept,
    }


if __name__ == "__main__":
    print(purge_english())
