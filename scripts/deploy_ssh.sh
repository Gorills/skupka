#!/bin/bash
# Деплой через SSH
# Запуск: ./scripts/deploy_ssh.sh
#
# Переменные (опционально):
#   SSH_SERVER   — s1150101@tomsk-skupka.ru
#   REMOTE_PATH  — tomsk-skupka-shop.ru (относительно домашнего каталога)
#   SKIP_STATIC  — 1 чтобы не собирать статику локально (быстрее при мелких правках)
#   DRY_RUN      — 1 для проверки без реальной загрузки

set -e

SSH_SERVER="${SSH_SERVER:-s1150101@tomsk-skupka.ru}"
REMOTE_PATH="${REMOTE_PATH:-tomsk-skupka-shop.ru}"
DRY_RUN="${DRY_RUN:-0}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Деплой на сервер ==="
echo "Сервер: $SSH_SERVER"
echo "Путь: $REMOTE_PATH"
echo "Проект: $PROJECT_ROOT"
echo

# 1. Сбор статики локально
if [ "${SKIP_STATIC}" != "1" ]; then
    echo "1. Сбор статики..."
    python manage.py collectstatic --noinput --clear
    echo "   Готово."
else
    echo "1. Пропуск collectstatic (SKIP_STATIC=1)"
fi

# 2. Загрузка файлов через rsync
echo
echo "2. Загрузка файлов на сервер..."
RSYNC_OPTS="-avz --delete"
[ "$DRY_RUN" = "1" ] && RSYNC_OPTS="$RSYNC_OPTS -n --verbose"
rsync $RSYNC_OPTS \
  --exclude 'venv' \
  --exclude '.git' \
  --exclude 'db.sqlite3' \
  --exclude '.env' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.log' \
  --exclude 'deploy.tar.gz' \
  --exclude '.idea' \
  --exclude '.vscode' \
  --exclude 'node_modules' \
  --filter 'protect .env' \
  --filter 'protect db.sqlite3' \
  --filter 'protect venv/' \
  --filter 'protect tmp/' \
  "$PROJECT_ROOT/" \
  "$SSH_SERVER:~/$REMOTE_PATH/"

echo "   Файлы загружены."

# 3. Выполнение команд на сервере
echo
if [ "$DRY_RUN" = "1" ]; then
    echo "3. Пропуск (DRY_RUN=1): migrate, collectstatic, restart"
else
echo "3. Выполнение команд на сервере..."
ssh "$SSH_SERVER" "cd $REMOTE_PATH && \
  source /home/s1150101/python3.6/bin/activate && \
  python manage.py migrate --noinput && \
  python manage.py collectstatic --noinput 2>/dev/null || true && \
  sed -i \"s/# deploy: .*/# deploy: \$(date +%s)/\" index.wsgi && \
  echo '   Миграции применены. Приложение перезапущено.'"
fi

echo
echo "=== Деплой завершён ==="
