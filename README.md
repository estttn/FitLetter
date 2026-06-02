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
cp .env.example .env      # заполните DEEPSEEK_API_KEY
cp profile.example.json profile.json
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

## Деплой (main) и SSH

При push в `main` GitHub Actions копирует код на VPS и запускает `deploy.sh`.

Подробнее: [deploy-keys/README.md](deploy-keys/README.md)

### 1. Ключ для VPS

```bash
cd /opt/hh-job-scout
git pull origin main   # или scp, если ещё не git
bash scripts/install_deploy_pubkey.sh
```

### 2. Secrets в GitHub

Settings ? Secrets and variables ? Actions:

| Secret | Значение |
|--------|----------|
| `DEPLOY_HOST` | `89.108.98.245` |
| `DEPLOY_USER` | `root` |
| `DEPLOY_SSH_KEY` | приватный ключ из `deploy-keys/fitletter_github_actions` (файл не в git) |

Опционально: webhook `/api/hooks/deploy` (см. `.env.example`) вместо только SCP.

## Сбор вакансий

Параллельная загрузка с HH — настройки в `.env` или в панели сбора.

| Переменная | По умолчанию | Назначение |
|------------|--------------|------------|
| `COLLECT_DESC_WORKERS` | `8` | Потоки описаний с HH |
| `COLLECT_LETTER_WORKERS` | `15` | Потоки писем в DeepSeek |

## Структура

```text
app/           FastAPI, collector, scorer, letters
app/templates/ UI
scripts/       утилиты (purge, regen, deploy)
data/          SQLite (не в git)
```

Репозиторий на GitHub: `estttn/job-scout` (внутреннее имя; бренд в продукте — **Бюро Скаут**).
