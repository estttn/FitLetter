"""Daily cron: collect HH vacancies for all active users and resumes."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.collector import collect_all_sync

if __name__ == "__main__":
    results = collect_all_sync()
    for r in results:
        print(r)
    print(f"Done: {len(results)} resume(s) processed")
