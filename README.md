# FitLetter

Подбор вакансий на HeadHunter под ваш профиль: fit-скоринг, персональные сопроводительные письма, трекер откликов.

## Ветки

| Ветка | Назначение |
|-------|------------|
| **dev** | Разработка. Вся работа и выгрузки сюда. |
| **main** | Продакшен. Merge из `dev` по запросу ? автодеплой на сервер. |

```text
feature work ? dev ? (по запросу) merge to main ? GitHub Actions ? webhook ? VPS
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

## Деплой (main) — SSH

При push в `main` GitHub Actions копирует файлы на VPS по SCP и запускает `deploy.sh`.

Подробно: [deploy-keys/README.md](deploy-keys/README.md)

### 1. Один раз на VPS

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
| `DEPLOY_SSH_KEY` | приватный ключ из `deploy-keys/fitletter_github_actions` (локально, не в git) |

Опционально: webhook `/api/hooks/deploy` (см. `.env.example`) — для деплоя без SCP.

## Сбор вакансий

Кнопка «Обновить с HH» сначала загружает вакансии, затем в фоне параллельно генерирует письма.

| Переменная | По умолчанию | Назначение |
|------------|--------------|------------|
| `COLLECT_DESC_WORKERS` | `8` | Потоки загрузки описаний с HH |
| `COLLECT_LETTER_WORKERS` | `15` | Потоки запросов к DeepSeek |

## Структура

```text
app/           FastAPI, collector, scorer, letters
app/templates/ UI
scripts/       утилиты (purge, regen, deploy)
data/          SQLite (не в git)
```
