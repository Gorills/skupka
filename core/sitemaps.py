from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Page


class StaticSitemap(Sitemap):
    """Статичные страницы: главная, политика"""
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['home', 'privacy']

    def location(self, item):
        if item == 'home':
            return '/'
        if item == 'privacy':
            return '/privacy/'
        return '/'


class PageSitemap(Sitemap):
    """Страницы из БД (скупка, ремонт и т.д.)"""
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return Page.objects.filter(is_published=True).exclude(slug='home')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
