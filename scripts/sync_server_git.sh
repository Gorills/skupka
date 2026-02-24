#!/bin/bash
# Синхронизация кода на сервере с GitHub
# Сервер → GitHub (актуальный код на сервере пушится в репозиторий)
#
# Запуск на сервере:
#   ssh s1150101@tomsk-skupka.ru
#   cd /home/s1150101/tomsk-skupka-shop.ru  # или ваш путь
#   bash -c "$(curl -sL https://raw.githubusercontent.com/Gorills/skupka/main/scripts/sync_server_git.sh)"
#
# Или скопируйте скрипт на сервер и запустите: bash scripts/sync_server_git.sh

set -e

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
REPO_URL="https://github.com/Gorills/skupka.git"

cd "$PROJECT_DIR" || { echo "Каталог $PROJECT_DIR не найден"; exit 1; }

echo "=== Синхронизация с GitHub (сервер → репозиторий) ==="

if [ ! -d .git ]; then
    echo "Git не инициализирован. Инициализация..."
    [ -f .env ] && cp .env .env.backup
    git init
    git remote add origin "$REPO_URL"
    git fetch origin main
    git checkout -b main origin/main
    git reset --soft origin/main
    git add -A
    git status
    if [ -n "$(git status -s)" ]; then
        git commit -m "Синхронизация с сервера $(date +%Y-%m-%d)"
        echo "Коммит создан. Для push нужен доступ к GitHub:"
        echo "  git push -u origin main"
    fi
    [ -f .env.backup ] && mv .env.backup .env
else
    git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    git fetch origin main 2>/dev/null || true
    
    if [ -n "$(git status -s)" ]; then
        echo "Есть локальные изменения на сервере:"
        git status
        git add -A
        git commit -m "Синхронизация с сервера $(date +%Y-%m-%d)" || echo "Нечего коммитить"
    fi
    
    # Попытка push (если настроен deploy key или токен)
    if git push -u origin main 2>/dev/null; then
        echo "Успешно отправлено в GitHub."
    else
        echo "Push не выполнен (нет доступа к GitHub с сервера)."
        echo "Скачайте изменения локально и выполните: git push origin main"
    fi
fi
