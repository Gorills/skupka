from .models import SiteSettings, Page


def site_settings(request):
    """Добавляет настройки сайта и меню во все шаблоны"""
    settings = SiteSettings.get_settings()
    menu_pages = Page.objects.filter(
        is_published=True,
        show_in_menu=True
    ).exclude(slug='home').order_by('order', 'title')

    canonical_url = request.build_absolute_uri(request.path)

    return {
        'site_settings': settings,
        'menu_pages': menu_pages,
        'recaptcha_site_key': settings.recaptcha_site_key,
        'seo_canonical_url': canonical_url,
        'seo_site_url': request.build_absolute_uri('/'),
    }
