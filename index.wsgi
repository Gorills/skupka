# -*- coding: utf-8 -*-

import os
import sys
import time
import traceback
import signal

# Путь к проекту на сервере (FTP: /tomsk-skupka-shop.ru)
PROJECT_ROOT = '/home/s1150101/tomsk-skupka-shop.ru/'
# Путь к activate_this.py (если есть)
VENV_ACTIVATE = '/home/s1150101/tomsk-skupka-shop.ru/venv/bin/activate_this.py'

# Активация виртуального окружения
if os.path.exists(VENV_ACTIVATE):
    with open(VENV_ACTIVATE) as f:
        code = compile(f.read(), VENV_ACTIVATE, 'exec')
        exec(code, dict(__file__=VENV_ACTIVATE))
else:
    # Python 3.8+: activate_this нет — добавляем venv/lib/.../site-packages в path
    venv_root = os.path.dirname(os.path.dirname(VENV_ACTIVATE))
    venv_site = os.path.join(venv_root, 'lib', 'python%d.%d' % sys.version_info[:2], 'site-packages')
    if os.path.exists(venv_site):
        sys.path.insert(0, venv_site)

sys.path.insert(0, PROJECT_ROOT)

import django

# Модуль настроек этого проекта — config.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if django.VERSION[0] < 2 and django.VERSION[1] <= 6:
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()
else:
    from django.core.wsgi import get_wsgi_application
    try:
        application = get_wsgi_application()
    except RuntimeError:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
