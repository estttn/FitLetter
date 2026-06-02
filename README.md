# FitLetter

˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜ ˜˜ HeadHunter ˜˜˜ ˜˜˜ ˜˜˜˜˜˜˜: fit-˜˜˜˜˜˜˜, ˜˜˜˜˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜, ˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜.

**Roadmap (˜˜˜˜˜˜˜˜˜˜ ? ˜˜˜˜, 3 ˜˜˜˜˜˜˜):** [ROADMAP.md](ROADMAP.md)

## ˜˜˜˜˜

| ˜˜˜˜˜ | ˜˜˜˜˜˜˜˜˜˜ |
|-------|------------|
| **dev** | ˜˜˜˜˜˜˜˜˜˜. ˜˜˜ ˜˜˜˜˜˜ ˜ ˜˜˜˜˜˜˜˜ ˜˜˜˜. |
| **main** | ˜˜˜˜˜˜˜˜˜. Merge ˜˜ `dev` ˜˜ ˜˜˜˜˜˜˜ ? ˜˜˜˜˜˜˜˜˜˜ ˜˜ ˜˜˜˜˜˜. |

```text
feature work ? dev ? (˜˜ ˜˜˜˜˜˜˜) merge to main ? GitHub Actions ? webhook ? VPS
```

## ˜˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # ˜˜˜˜˜˜˜˜˜ DEEPSEEK_API_KEY
cp profile.example.json profile.json
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

## ˜˜˜˜˜˜ (main) ˜ SSH

˜˜˜ push ˜ `main` GitHub Actions ˜˜˜˜˜˜˜˜ ˜˜˜˜˜ ˜˜ VPS ˜˜ SCP ˜ ˜˜˜˜˜˜˜˜˜ `deploy.sh`.

˜˜˜˜˜˜˜˜: [deploy-keys/README.md](deploy-keys/README.md)

### 1. ˜˜˜˜ ˜˜˜ ˜˜ VPS

```bash
cd /opt/hh-job-scout
git pull origin main   # ˜˜˜ scp, ˜˜˜˜ ˜˜˜ ˜˜ git
bash scripts/install_deploy_pubkey.sh
```

### 2. Secrets ˜ GitHub

Settings ? Secrets and variables ? Actions:

| Secret | ˜˜˜˜˜˜˜˜ |
|--------|----------|
| `DEPLOY_HOST` | `89.108.98.245` |
| `DEPLOY_USER` | `root` |
| `DEPLOY_SSH_KEY` | ˜˜˜˜˜˜˜˜˜ ˜˜˜˜ ˜˜ `deploy-keys/fitletter_github_actions` (˜˜˜˜˜˜˜˜, ˜˜ ˜ git) |

˜˜˜˜˜˜˜˜˜˜˜: webhook `/api/hooks/deploy` (˜˜. `.env.example`) ˜ ˜˜˜ ˜˜˜˜˜˜ ˜˜˜ SCP.

## ˜˜˜˜ ˜˜˜˜˜˜˜˜

˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜˜ ˜ HH˜ ˜˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜, ˜˜˜˜˜ ˜ ˜˜˜˜ ˜˜˜˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜.

| ˜˜˜˜˜˜˜˜˜˜ | ˜˜ ˜˜˜˜˜˜˜˜˜ | ˜˜˜˜˜˜˜˜˜˜ |
|------------|--------------|------------|
| `COLLECT_DESC_WORKERS` | `8` | ˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜ ˜ HH |
| `COLLECT_LETTER_WORKERS` | `15` | ˜˜˜˜˜˜ ˜˜˜˜˜˜˜˜ ˜ DeepSeek |

## ˜˜˜˜˜˜˜˜˜

```text
app/           FastAPI, collector, scorer, letters
app/templates/ UI
scripts/       ˜˜˜˜˜˜˜ (purge, regen, deploy)
data/          SQLite (˜˜ ˜ git)
```
