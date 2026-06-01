"""Import vacancies from hh-vacancy-tracker.md into SQLite."""
from __future__ import annotations

import re
from pathlib import Path

from app.db import init_db, upsert_vacancy

TRACKER = Path(__file__).resolve().parent.parent / "hh-vacancy-tracker.md"

ROW_RE = re.compile(
    r"\|\s*☐\s*\|\s*\d+\s*\|\s*(✅|🟡)\s*\|\s*([^|]+)\|\s*\[([^\]]+)\]\((https://[^)]+/vacancy/(\d+))\)\s*\|\s*([^|]+)\|"
)
LETTER_RE = re.compile(
    r"### №(\d+).*?\{#p\d+\}\s*\n\n.*?\n\n((?:> .+\n?)+)",
    re.DOTALL,
)


def parse_letters(text: str) -> dict[int, str]:
    out: dict[int, str] = {}
    for m in LETTER_RE.finditer(text):
        num = int(m.group(1))
        body = m.group(2)
        lines = [ln[2:].strip() for ln in body.strip().splitlines() if ln.startswith("> ")]
        out[num] = "\n".join(lines)
    return out


def seed(path: Path = TRACKER) -> int:
    init_db()
    text = path.read_text(encoding="utf-8")
    letters = parse_letters(text)
    count = 0
    for i, m in enumerate(ROW_RE.finditer(text), start=1):
        fit = "yes" if m.group(1) == "✅" else "partial"
        company = m.group(2).strip() or "—"
        title = m.group(3).strip()
        url = m.group(4).strip()
        vid = m.group(5).strip()
        salary = m.group(6).strip()
        letter = letters.get(i, f"Добрый день!\n\nОткликаюсь на «{title}».\n\nВладислав")
        upsert_vacancy(
            {
                "id": vid,
                "title": title,
                "company": company,
                "salary": salary,
                "url": url,
                "fit": fit,
                "reason": "import from tracker",
                "cover_letter": letter,
            }
        )
        count += 1
    return count


if __name__ == "__main__":
    print({"imported": seed()})
