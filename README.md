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

## Деплой (main) — без SSH-ключа в GitHub

При push в `main` Actions вызывает **webhook** на уже работающем сервере. Сервер делает `git pull` и `systemctl restart`. SSH в Secrets не нужен.

### 1. Один раз на VPS

```bash
cd /opt/hh-job-scout
# если папка не git-репозиторий:
bash scripts/setup_git_on_server.sh

# в .env добавьте (сгенерируйте: openssl rand -hex 32):
FITLETTER_DEPLOY_HOOK_TOKEN=ваш_длинный_секрет

systemctl restart hh-job-scout
```

`data/`, `.env`, `profile.json` при `git reset` не трогаются (они в `.gitignore`).

### 2. Secrets в GitHub

Settings ? Secrets and variables ? Actions:

| Secret | Пример |
|--------|--------|
| `DEPLOY_HOOK_URL` | `http://89.108.98.245:8090/api/hooks/deploy` |
| `DEPLOY_HOOK_TOKEN` | тот же токен, что в `.env` на сервере |

Старые `DEPLOY_HOST` / `DEPLOY_USER` / `DEPLOY_SSH_KEY` можно удалить.

### 3. Проверка

```bash
curl -X POST -H "Authorization: Bearer ВАШ_ТОКЕН" http://89.108.98.245:8090/api/hooks/deploy
# {"ok":true,"message":"deploy started"}
tail -f /opt/hh-job-scout/data/deploy.log
```

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
