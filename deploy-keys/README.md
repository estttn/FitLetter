# Deploy SSH key (FitLetter / job-scout)

Ключ **только для GitHub Actions → VPS**. Не коммитьте приватный ключ.

| Файл | Назначение |
|------|------------|
| `fitletter_github_actions` | Приватный → Secret `DEPLOY_SSH_KEY` в GitHub |
| `fitletter_github_actions.pub` | Публичный → `authorized_keys` на сервере |

## Сервер (один раз)

```bash
# на VPS под пользователем деплоя (часто root):
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys << 'EOF'
# вставьте одну строку из fitletter_github_actions.pub
EOF
chmod 600 ~/.ssh/authorized_keys
```

Или из репозитория на сервере:

```bash
bash /opt/hh-job-scout/scripts/install_deploy_pubkey.sh
```

## GitHub Secrets

Settings → Secrets and variables → Actions:

| Secret | Значение |
|--------|----------|
| `DEPLOY_HOST` | `89.108.98.245` |
| `DEPLOY_USER` | `root` |
| `DEPLOY_SSH_KEY` | полное содержимое файла `fitletter_github_actions` (включая `BEGIN`/`END`) |

После этого push в `main` запускает деплой.
