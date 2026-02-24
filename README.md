# TOMSK-SKUPKA.RU

Современный сайт для компании по скупке и ремонту техники в Томске.

## Возможности

- Полностью редактируемый контент через админку
- CKEditor для форматирования текста
- SEO-оптимизация (meta-теги, Open Graph, Schema.org)
- Адаптивный современный дизайн
- Форма обратной связи с AJAX-отправкой
- Управление страницами из админки

## Установка

1. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

4. Примените миграции:

```bash
python manage.py migrate
```

5. Загрузите начальные данные:

```bash
python manage.py load_initial_data
```

6. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

7. Запустите сервер разработки:

```bash
python manage.py runserver
```

## Структура проекта

```
tomsk-skupka/
├── config/           # Настройки Django
├── core/             # Основное приложение
│   ├── models.py     # Модели данных
│   ├── admin.py      # Настройка админки
│   ├── views.py      # Views
│   └── forms.py      # Формы
├── templates/        # Шаблоны
├── static/           # Статические файлы
└── media/            # Загружаемые файлы
```

## Админка

Доступ к админке: `/admin/`

### Разделы:

- **Настройки сайта** — телефон, адрес, статистика
- **Страницы** - управление страницами сайта
- **Заявки** - заявки с формы обратной связи

### Создание новой страницы:

1. Перейдите в раздел "Страницы"
2. Нажмите "Добавить страницу"
3. Заполните поля:
   - Заголовок и URL (slug)
   - Тип страницы
   - Hero-секцию
   - Контент (CKEditor)
   - Преимущества (если нужны)
   - SEO-настройки
4. Сохраните страницу

## Деплой на https://tomsk-skupka.ru

Сайт настроен для работы на домене **tomsk-skupka.ru** (HTTPS, sitemap, безопасные cookie).

### Загрузка по FTP

**Вариант 1 — архив (рекомендуется):** один файл вместо сотен, быстрее.

```bash
export FTP_HOST=141.8.192.20
export FTP_USER=s1150101
export FTP_PASS='ваш_пароль'
export FTP_REMOTE_DIR=/tomsk-skupka-shop.ru
export DEPLOY_ARCHIVE=1

python deploy.py
```

Скрипт соберёт статику, создаст `deploy.tar.gz`, загрузит его на FTP. На сервере распакуйте через SSH или файловый менеджер панели хостинга.

**Вариант 2 — по SSH (рекомендуется при настроенном доступе по ключу):**

```bash
./scripts/deploy_ssh.sh
```

Скрипт: собирает статику → загружает файлы через rsync → выполняет `migrate` и `collectstatic` на сервере → перезапускает приложение (Passenger).

Переменные: `SSH_SERVER`, `REMOTE_PATH`, `SKIP_STATIC=1`, `DRY_RUN=1`.

**Вариант 3 — по файлам (FTP):**

```bash
export FTP_HOST=141.8.192.20
export FTP_USER=s1150101
export FTP_PASS='ваш_пароль'
export FTP_REMOTE_DIR=/tomsk-skupka-shop.ru

python deploy.py
```

2. **После загрузки на сервере** (через панель хостинга или SSH) выполните:

```bash
cd /domains/tomsk-skupka.ru   # или полный путь
python manage.py migrate
python manage.py load_initial_data
python manage.py createsuperuser
```

3. Создайте `.env` на сервере с продакшен-настройками (см. ниже).

### Настройки на сервере

1. **Переменные окружения** (в `.env` на сервере):

```env
SECRET_KEY=ваш-секретный-ключ-сгенерируйте-новый
DEBUG=False
ALLOWED_HOSTS=tomsk-skupka.ru,www.tomsk-skupka.ru
CSRF_TRUSTED_ORIGINS=https://tomsk-skupka.ru,https://www.tomsk-skupka.ru
```

2. **Первый запуск на сервере:**

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_initial_data   # настраивает домен tomsk-skupka.ru и контент
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

3. **Запуск приложения:** Gunicorn (или uWSGI) + Nginx. Nginx должен передавать заголовок `X-Forwarded-Proto: https` для корректной работы редиректа на HTTPS и cookie.

4. **Статика:** WhiteNoise раздаёт статику из `staticfiles/` после `collectstatic`; при желании можно отдавать `/static/` и `/media/` через Nginx.

5. **WSGI:** В корне проекта лежит `index.wsgi`. В начале файла заданы `PROJECT_ROOT` и `VENV_ACTIVATE` — замените их на фактические пути на сервере (каталог проекта и путь к `venv/bin/activate_this.py` или к каталогу venv). Модуль настроек: `config.settings`.

6. **Домен в sitemap:** Команда `load_initial_data` выставляет для сайта (SITE_ID=1) домен `tomsk-skupka.ru`, поэтому `sitemap.xml` и канонические URL будут с этим доменом.
