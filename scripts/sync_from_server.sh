#!/bin/bash
# Скачивает код с сервера и пушит в GitHub
# Запуск локально: ./scripts/sync_from_server.sh
# Требует: SSH-доступ к серверу (пароль или ключ)

set -e

SERVER="${SSH_SERVER:-s1150101@tomsk-skupka.ru}"
REMOTE_PATH="${REMOTE_PATH:-/home/s1150101/tomsk-skupka-shop.ru}"
LOCAL_PATH="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Синхронизация: сервер → локально → GitHub ==="
echo "Сервер: $SERVER"
echo "Путь на сервере: $REMOTE_PATH"
echo "Локальный проект: $LOCAL_PATH"
echo

# Исключаем venv, .git, db, .env, media при скачивании
rsync -avz --progress \
  --exclude 'venv' \
  --exclude '.git' \
  --exclude 'db.sqlite3' \
  --exclude '.env' \
  --exclude '__pycache__' \
  --exclude 'staticfiles' \
  --exclude '*.pyc' \
  "$SERVER:$REMOTE_PATH/" \
  "$LOCAL_PATH/"

cd "$LOCAL_PATH"
echo
echo "=== Git статус ==="
git status

if [ -n "$(git status -s)" ]; then
  git add -A
  git commit -m "Синхронизация с сервера $(date +%Y-%m-%d)"
  git push origin main
  echo "Готово. Изменения отправлены в GitHub."
else
  echo "Изменений нет. Код уже синхронизирован."
fi
