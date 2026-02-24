# -*- coding: utf-8 -*-
import os
import sys
import time
import traceback
import signal

activate_this = '/home/s1150101/python3.6/bin/activate_this.py'
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec(code, dict(__file__=activate_this))

sys.path.insert(0, '/home/s1150101/tomsk-skupka-shop.ru/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.core.wsgi import get_wsgi_application
try:
    application = get_wsgi_application()
except RuntimeError:
    traceback.print_exc()
    os.kill(os.getpid(), signal.SIGINT)
    time.sleep(2.5)
