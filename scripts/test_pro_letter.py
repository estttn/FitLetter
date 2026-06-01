import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.collector import fetch_vacancy_description
from app.letters import generate_cover_letter

url = "https://hh.ru/vacancy/132093778"
desc = fetch_vacancy_description(url)
letter = generate_cover_letter(
    title="Service Delivery Manager",
    company="Evrone",
    salary="—",
    description=desc,
)
print("len:", len(letter))
print(letter)
