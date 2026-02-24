#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт деплоя на FTP.
Режимы:
  - Обычный: загрузка файлов по FTP
  - Архив: DEPLOY_ARCHIVE=1 — собирает tar.gz, загружает один файл, распаковка на сервере

Переменные: FTP_HOST, FTP_USER, FTP_PASS, FTP_REMOTE_DIR
"""
import os
import sys
import subprocess
import tarfile
import tempfile
from pathlib import Path
from ftplib import FTP

# Каталоги и файлы, которые НЕ загружаем
EXCLUDE = {
    'venv', '__pycache__', '.git', 'node_modules',
    '.idea', '.vscode', '*.log',
}
EXCLUDE_FILES = {'.env', 'db.sqlite3', 'db.sqlite3-journal'}

# Файлы в корне, которые загружаем
INCLUDE_FILES = {'manage.py', 'index.wsgi', 'requirements.txt', '.env.example'}


def should_exclude(path: Path, base: Path) -> bool:
    rel = path.relative_to(base)
    if path.name in EXCLUDE_FILES:
        return True
    for part in rel.parts:
        if part in EXCLUDE or (part.startswith('.') and part != '..'):
            return True
    if path.is_file() and path.suffix in ('.pyc', '.pyo'):
        return True
    return False


def ensure_remote_path(ftp: FTP, base: str, path: str) -> None:
    """Создаёт вложенные каталоги по пути (cwd в каждый уровень)."""
    ftp.cwd(base)
    for part in path.rstrip('/').split('/'):
        if not part:
            continue
        try:
            ftp.cwd(part)
        except Exception:
            try:
                ftp.mkd(part)
            except Exception:
                pass
            ftp.cwd(part)
    ftp.cwd(base)


def upload_dir(ftp: FTP, local: Path, remote: str, project_root: Path, remote_base: str):
    """Рекурсивно загружает каталог."""
    for item in sorted(local.iterdir()):
        if should_exclude(item, project_root):
            continue
        rel = item.relative_to(local)
        remote_path = f"{remote}/{rel}".replace('\\', '/')
        if item.is_dir():
            ensure_remote_path(ftp, remote_base, remote_path)
            upload_dir(ftp, item, remote_path, project_root, remote_base)
        else:
            parent = '/'.join(remote_path.split('/')[:-1])
            filename = remote_path.split('/')[-1]
            if parent:
                ensure_remote_path(ftp, remote_base, parent)
            try:
                ftp.cwd(remote_base)
                for part in parent.split('/'):
                    if part:
                        ftp.cwd(part)
                with open(item, 'rb') as f:
                    ftp.storbinary(f'STOR {filename}', f)
                print(f"  ↑ {remote_path}")
            except Exception as e:
                print(f"  ✗ {remote_path}: {e}")


def create_archive(base: Path) -> Path:
    """Создаёт tar.gz с проектом (без venv, .git, .env и т.д.)."""
    archive_name = base / 'deploy.tar.gz'
    if archive_name.exists():
        archive_name.unlink()
    dirs = ['config', 'core', 'templates', 'static', 'staticfiles', 'media']
    files = ['manage.py', 'index.wsgi', 'requirements.txt', '.env.example']
    with tarfile.open(archive_name, 'w:gz') as tar:
        for name in files:
            f = base / name
            if f.exists():
                tar.add(f, arcname=name)
        for dirname in dirs:
            d = base / dirname
            if d.exists() and d.is_dir():
                for item in d.rglob('*'):
                    if should_exclude(item, base):
                        continue
                    if item.is_file():
                        arcname = item.relative_to(base)
                        tar.add(item, arcname=str(arcname))
    return archive_name


def deploy_via_archive(base: Path, host: str, user: str, password: str, remote_dir: str) -> None:
    """Сбор статики → архив → загрузка на FTP."""
    print("1. Сбор статики...")
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'], check=True)
    print("2. Создание архива deploy.tar.gz...")
    archive = create_archive(base)
    size_mb = archive.stat().st_size / (1024 * 1024)
    print(f"   Размер: {size_mb:.1f} МБ")
    print("3. Подключение к FTP...")
    ftp = FTP(host, user, password)
    ftp.encoding = 'utf-8'
    try:
        ftp.cwd(remote_dir)
    except Exception:
        for part in remote_dir.strip('/').split('/'):
            if part:
                try:
                    ftp.mkd(part)
                except Exception:
                    pass
                ftp.cwd(part)
    print("4. Загрузка deploy.tar.gz...")
    with open(archive, 'rb') as f:
        ftp.storbinary('STOR deploy.tar.gz', f)
    ftp.quit()
    archive.unlink()
    print("Готово.")
    print()
    print("На сервере распакуйте архив:")
    print("  • SSH: cd /home/s1150101/tomsk-skupka-shop.ru && tar -xzf deploy.tar.gz && rm deploy.tar.gz")
    print("  • Панель хостинга: Файловый менеджер → deploy.tar.gz → Распаковать")
    print("  • Затем: python manage.py migrate && python manage.py load_initial_data && python manage.py createsuperuser")


def main():
    base = Path(__file__).resolve().parent
    os.chdir(base)

    host = os.environ.get('FTP_HOST', '141.8.192.20')
    user = os.environ.get('FTP_USER', 's1150101')
    password = os.environ.get('FTP_PASS')
    remote_dir = os.environ.get('FTP_REMOTE_DIR', '/tomsk-skupka-shop.ru')

    if not password:
        print("Задайте пароль: export FTP_PASS='ваш_пароль'")
        sys.exit(1)

    if os.environ.get('DEPLOY_ARCHIVE', '').lower() in ('1', 'true', 'yes'):
        deploy_via_archive(base, host, user, password, remote_dir)
        return

    staticfiles_only = os.environ.get('DEPLOY_STATICFILES_ONLY', '').lower() in ('1', 'true', 'yes')

    if not staticfiles_only:
        print("1. Сбор статики...")
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'], check=True)
    else:
        print("1. Только staticfiles (DEPLOY_STATICFILES_ONLY=1)")

    print("2. Подключение к FTP...")
    ftp = FTP(host, user, password)
    ftp.encoding = 'utf-8'

    print("3. Переход в каталог...")
    try:
        ftp.cwd(remote_dir)
    except Exception:
        # Создаём путь по частям
        for part in remote_dir.strip('/').split('/'):
            if part:
                try:
                    ftp.mkd(part)
                except Exception:
                    pass
                ftp.cwd(part)

    print("4. Загрузка файлов...")
    # Загружаем корневые файлы (пропуск при staticfiles_only)
    if not staticfiles_only:
        for name in INCLUDE_FILES:
            f = base / name
            if f.exists():
                with open(f, 'rb') as fp:
                    ftp.storbinary(f'STOR {name}', fp)
                print(f"  ↑ {name}")

    # Загружаем каталоги
    dirs_to_upload = ['staticfiles'] if staticfiles_only else ['config', 'core', 'templates', 'static', 'staticfiles', 'media']
    for dirname in dirs_to_upload:
        d = base / dirname
        if d.exists() and d.is_dir():
            try:
                ftp.mkd(dirname)
            except Exception:
                pass
            try:
                ftp.cwd(dirname)
            except Exception:
                pass
            upload_dir(ftp, d, dirname, base, remote_dir)
            ftp.cwd('/')
            try:
                ftp.cwd(remote_dir)
            except Exception:
                pass

    ftp.quit()
    print("Готово.")


if __name__ == '__main__':
    main()
