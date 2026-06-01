#!/bin/bash
# One-time: copy DeepSeek PRO credentials into project-local .env (not bot/.env)
set -e
DEST=/opt/hh-job-scout/.env
SRC=/opt/bot/.env

if [ ! -f "$SRC" ]; then
  echo "Missing $SRC"
  exit 1
fi

get_val() { grep -m1 "^$1=" "$SRC" | cut -d= -f2-; }

{
  echo "DEEPSEEK_BASE_URL=$(get_val DEEPSEEK_BASE_URL)"
  echo "DEEPSEEK_MODEL_PRO=$(get_val DEEPSEEK_MODEL_PRO)"
  echo "DEEPSEEK_MAX_TOKENS_PRO=$(get_val DEEPSEEK_MAX_TOKENS_PRO)"
  KEY=$(get_val DEEPSEEK_API_KEY_MAX)
  [ -z "$KEY" ] && KEY=$(get_val DEEPSEEK_API_KEY_TELEGRAM)
  [ -z "$KEY" ] && KEY=$(get_val DEEPSEEK_API_KEY)
  echo "DEEPSEEK_API_KEY=$KEY"
} > "$DEST"

chmod 600 "$DEST"
echo "Created $DEST (DeepSeek PRO, project-local)"
grep -E '^DEEPSEEK_(BASE|MODEL|MAX)' "$DEST" | sed 's/=.*/=***/'
grep -c '^DEEPSEEK_API_KEY=.' "$DEST" | xargs -I{} echo "API key present: {}"
