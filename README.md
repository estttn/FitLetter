# Бюро Скаут

Сервис поиска на HeadHunter для своей команды: fit-скоринг, персонализированные сопроводительные письма, учёт откликов.

**Roadmap (конкуренты ? план, 3 спринта):** [ROADMAP.md](ROADMAP.md)

## Ветки

| Ветка | Назначение |
|-------|------------|
| **dev** | Разработка. Вся работа и выгрузки сюда. |
| **main** | Продакшен. Merge из `dev` по запросу ? автодеплой на сервер. |

```text
feature work ? dev ? (по запросу) merge to main ? GitHub Actions ? VPS
```

## Локальный запуск

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
cp profile.example.json profile.json
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

## Деплой (main)

При push в `main` GitHub Actions копирует код на `/opt/hh-job-scout` и запускает `deploy.sh`.

Подробнее: [deploy-keys/README.md](deploy-keys/README.md)

| Secret | Значение |
|--------|----------|
| `DEPLOY_HOST` | `89.108.98.245` |
| `DEPLOY_USER` | `root` |
| `DEPLOY_SSH_KEY` | приватный ключ `deploy-keys/fitletter_github_actions` |

На сервере не перезаписываются: `data/`, `.env`, `profile.json`.

## Структура

```text
app/           FastAPI, collector, scorer, letters
app/templates/ UI
scripts/       утилиты
data/          SQLite (не в git)
```

Репозиторий: `estttn/job-scout` (внутреннее имя; бренд в продукте — **Бюро Скаут**).
