from app.collector import fetch_vacancy_description
from app.letters import generate_cover_letter

url = "https://hh.ru/vacancy/132093778"
d = fetch_vacancy_description(url)
l = generate_cover_letter(
    title="Service Delivery Manager (SDM)",
    company="evrone.ru",
    salary="—",
    description=d,
)
print("len", len(l))
print(l)
