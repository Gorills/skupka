from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class SiteSettings(models.Model):
    """Настройки сайта (singleton)"""
    site_name = models.CharField('Название сайта', max_length=200, default='Компьютеры?')
    phone = models.CharField('Телефон', max_length=50, default='8 (953) 921-15-72')
    phone_link = models.CharField('Телефон для ссылки', max_length=20, default='+79539211572')
    email = models.EmailField('Email', blank=True)
    address = models.CharField('Адрес', max_length=300, default='г.Томск, ул. Советская, д. 90')
    working_hours = models.CharField('Часы работы', max_length=100, default='Ежедневно с 10:00 до 20:00')
    whatsapp_link = models.URLField('Ссылка на WhatsApp', blank=True, help_text='Например: https://wa.me/79539211572')
    telegram_link = models.URLField('Ссылка на Telegram', blank=True, help_text='Например: https://t.me/username')
    
    years_work = models.PositiveIntegerField('Лет работы', default=10)
    devices_bought = models.PositiveIntegerField('Купленных устройств', default=1580)
    devices_sold = models.PositiveIntegerField('Проданных устройств', default=1705)
    happy_clients = models.PositiveIntegerField('Довольных клиентов', default=3285)
    devices_repaired = models.PositiveIntegerField('Отремонтированных устройств', default=1287)
    
    footer_text = models.TextField('Текст в футере', blank=True)
    
    map_code = models.TextField(
        'Код карты (iframe)', 
        blank=True,
        help_text='Вставьте код iframe с Яндекс.Карт или Google Maps'
    )
    
    telegram_bot_token = models.CharField(
        'Telegram Bot Token',
        max_length=100,
        blank=True,
        help_text='Токен бота от @BotFather (например: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)'
    )
    telegram_chat_id = models.CharField(
        'Telegram Chat ID',
        max_length=50,
        blank=True,
        help_text='ID группы или чата для отправки заявок (например: -1001234567890)'
    )
    
    recaptcha_site_key = models.CharField(
        'reCAPTCHA Site Key',
        max_length=100,
        blank=True,
        help_text='Публичный ключ reCAPTCHA v3 (получить на google.com/recaptcha)'
    )
    recaptcha_secret_key = models.CharField(
        'reCAPTCHA Secret Key',
        max_length=100,
        blank=True,
        help_text='Секретный ключ reCAPTCHA v3'
    )
    recaptcha_min_score = models.FloatField(
        'Минимальный score reCAPTCHA',
        default=0.5,
        help_text='От 0.0 до 1.0. Рекомендуется 0.5. Чем выше - тем строже проверка'
    )

    yandex_metrika = models.TextField(
        'Код счётчика Яндекс.Метрики',
        blank=True,
        help_text='Вставьте полный код счётчика из личного кабинета Метрики (скрипт целиком)'
    )
    yandex_verification = models.CharField(
        'Код верификации Яндекс.Вебмастер',
        max_length=100,
        blank=True,
        help_text='Значение content из тега <meta name="yandex-verification" content="..."> (только значение, без кавычек)'
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'
    
    def __str__(self):
        return 'Настройки сайта'
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings


class Page(models.Model):
    """Страница сайта"""
    PAGE_TYPES = [
        ('home', 'Главная страница'),
        ('skupka', 'Страница скупки'),
        ('remont', 'Страница ремонта'),
        ('info', 'Информационная страница'),
    ]
    
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, 
                           help_text='Адрес страницы, например: skupka-noutbukov')
    page_type = models.CharField('Тип страницы', max_length=20, choices=PAGE_TYPES, default='info')
    
    hero_title = models.CharField('Заголовок в hero-секции', max_length=300, blank=True)
    hero_subtitle = models.CharField('Подзаголовок в hero-секции', max_length=500, blank=True)
    
    content = CKEditor5Field('Основной контент', config_name='extends', blank=True)
    
    advantages_title = models.CharField('Заголовок блока преимуществ', max_length=200, blank=True)
    advantage_1_title = models.CharField('Преимущество 1 - заголовок', max_length=100, blank=True)
    advantage_1_text = models.CharField('Преимущество 1 - текст', max_length=200, blank=True)
    advantage_2_title = models.CharField('Преимущество 2 - заголовок', max_length=100, blank=True)
    advantage_2_text = models.CharField('Преимущество 2 - текст', max_length=200, blank=True)
    advantage_3_title = models.CharField('Преимущество 3 - заголовок', max_length=100, blank=True)
    advantage_3_text = models.CharField('Преимущество 3 - текст', max_length=200, blank=True)
    advantage_4_title = models.CharField('Преимущество 4 - заголовок', max_length=100, blank=True)
    advantage_4_text = models.CharField('Преимущество 4 - текст', max_length=200, blank=True)
    advantage_5_title = models.CharField('Преимущество 5 - заголовок', max_length=100, blank=True)
    advantage_5_text = models.CharField('Преимущество 5 - текст', max_length=200, blank=True)
    
    show_contact_form = models.BooleanField('Показывать форму заявки', default=True)
    show_in_menu = models.BooleanField('Показывать в меню', default=True)
    menu_title = models.CharField('Название в меню', max_length=100, blank=True,
                                 help_text='Если пусто, будет использован заголовок страницы')
    is_published = models.BooleanField('Опубликована', default=True)
    order = models.PositiveIntegerField('Порядок в меню', default=0)
    
    meta_title = models.CharField('SEO: Title', max_length=200, blank=True,
                                 help_text='Если пусто, будет использован заголовок страницы')
    meta_description = models.TextField('SEO: Description', blank=True, max_length=500)
    meta_keywords = models.CharField('SEO: Keywords', max_length=500, blank=True)
    og_image = models.ImageField('SEO: OG Image', upload_to='og_images/', blank=True)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.slug == 'home':
            return '/'
        return f'/{self.slug}/'
    
    def get_menu_title(self):
        return self.menu_title or self.title
    
    def get_meta_title(self):
        return self.meta_title or self.title
    
    def get_advantages(self):
        advantages = []
        for i in range(1, 6):
            title = getattr(self, f'advantage_{i}_title', '')
            text = getattr(self, f'advantage_{i}_text', '')
            if title:
                advantages.append({'title': title, 'text': text})
        return advantages


class ContactRequest(models.Model):
    """Заявка с формы обратной связи"""
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    message = models.TextField('Сообщение', blank=True)
    device_info = models.TextField('Информация об устройстве', blank=True,
                                   help_text='Модель, состояние и т.д.')
    
    page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, blank=True,
                            verbose_name='Страница', related_name='requests')
    page_url = models.CharField('URL страницы', max_length=200, blank=True)
    
    is_processed = models.BooleanField('Обработана', default=False)
    admin_notes = models.TextField('Заметки администратора', blank=True)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Заявка от {self.name} ({self.phone})'
