from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Page, ContactRequest


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек сайта"""
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('site_name', 'phone', 'phone_link', 'email', 'address', 'working_hours')
        }),
        ('Мессенджеры', {
            'fields': ('whatsapp_link', 'telegram_link'),
            'description': 'Ссылки для связи через мессенджеры'
        }),
        ('Статистика', {
            'fields': ('years_work', 'devices_bought', 'devices_sold', 'happy_clients', 'devices_repaired'),
            'description': 'Числа, отображаемые на главной странице'
        }),
        ('Telegram уведомления', {
            'fields': ('telegram_bot_token', 'telegram_chat_id'),
            'description': 'Настройки для отправки заявок в Telegram группу'
        }),
        ('Антиспам (reCAPTCHA v3)', {
            'fields': ('recaptcha_site_key', 'recaptcha_secret_key', 'recaptcha_min_score'),
            'description': 'Защита от спама. Получите ключи на google.com/recaptcha (выберите reCAPTCHA v3)'
        }),
        ('Яндекс', {
            'fields': ('yandex_metrika', 'yandex_verification'),
            'description': 'Яндекс.Метрика: вставьте код счётчика целиком. Вебмастер: укажите только значение content из мета-тега верификации.'
        }),
        ('Карта', {
            'fields': ('map_code',),
            'description': 'Вставьте код iframe с Яндекс.Карт или Google Maps'
        }),
        ('Дополнительно', {
            'fields': ('footer_text',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Админка для страниц"""
    
    list_display = ('title', 'slug', 'page_type', 'is_published', 'show_in_menu', 'order')
    list_filter = ('is_published', 'show_in_menu', 'page_type')
    list_editable = ('is_published', 'show_in_menu', 'order')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'page_type')
        }),
        ('Hero-секция', {
            'fields': ('hero_title', 'hero_subtitle'),
            'description': 'Верхняя секция страницы с заголовком'
        }),
        ('Контент', {
            'fields': ('content',)
        }),
        ('Преимущества', {
            'fields': (
                'advantages_title',
                ('advantage_1_title', 'advantage_1_text'),
                ('advantage_2_title', 'advantage_2_text'),
                ('advantage_3_title', 'advantage_3_text'),
                ('advantage_4_title', 'advantage_4_text'),
                ('advantage_5_title', 'advantage_5_text'),
            ),
            'classes': ('collapse',),
            'description': 'Блок с преимуществами (иконки выбираются автоматически)'
        }),
        ('Настройки отображения', {
            'fields': ('show_contact_form', 'show_in_menu', 'menu_title', 'is_published', 'order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_image'),
            'classes': ('collapse',),
            'description': 'Настройки для поисковых систем'
        }),
    )
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    """Админка для заявок"""
    
    list_display = ('name', 'phone', 'page', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at', 'page')
    list_editable = ('is_processed',)
    search_fields = ('name', 'phone', 'email', 'message', 'device_info')
    readonly_fields = ('name', 'phone', 'email', 'message', 'device_info', 'page', 'page_url', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Контактные данные', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Заявка', {
            'fields': ('message', 'device_info', 'page', 'page_url', 'created_at')
        }),
        ('Обработка', {
            'fields': ('is_processed', 'admin_notes')
        }),
    )
    
    def has_add_permission(self, request):
        return False


admin.site.site_header = 'TOMSK-SKUPKA.RU'
admin.site.site_title = 'Управление сайтом'
admin.site.index_title = 'Панель управления'
