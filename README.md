# Job Scout

Сервис подбора вакансий с HeadHunter: фильтрация, fit-скоринг, сопроводительные письма.

## Ветки

| Ветка | Назначение |
|-------|------------|
| **dev** | Разработка. Сюда пушим все изменения. |
| **main** | Продакшен. Merge из `dev` по запросу ? автодеплой на сервер. |

```text
feature work ? dev ? (по запросу) merge to main ? GitHub Actions ? VPS
```

## Локальный запуск

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # заполнить DEEPSEEK_API_KEY
cp profile.example.json profile.json
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

## Деплой (main)

При push в `main` срабатывает `.github/workflows/deploy-main.yml`.

**Secrets в GitHub** (Settings ? Secrets ? Actions):

| Secret | Пример |
|--------|--------|
| `DEPLOY_HOST` | `89.108.98.245` |
| `DEPLOY_USER` | `root` |
| `DEPLOY_SSH_KEY` | приватный ключ SSH (deploy) |

На сервере сохраняются: `data/`, `.env`, `profile.json` — в git не входят.

## Структура

```text
app/           FastAPI, collector, scorer, letters
app/templates/ UI
scripts/       утилиты (purge, regen)
data/          SQLite (не в git)
```
