from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.sitemaps import StaticSitemap, PageSitemap
from core.views import robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', sitemap, {
        'sitemaps': {'static': StaticSitemap(), 'pages': PageSitemap()},
    }, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),  # view в core.views
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
