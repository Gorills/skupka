from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.urls import reverse
from .models import Page, SiteSettings
from .forms import ContactForm
from .services import send_telegram_notification, verify_recaptcha


def privacy_page(request):
    """Статичная страница политики конфиденциальности"""
    class StaticPage:
        def get_meta_title(self):
            return 'Политика в области обработки персональных данных'
        meta_description = 'Политика обработки персональных данных. Согласие на обработку данных при отправке заявок.'
        meta_keywords = 'политика конфиденциальности, персональные данные'
        og_image = None
    site_url = request.build_absolute_uri('/')
    seo_breadcrumbs = [
        {'name': 'Главная', 'url': site_url},
        {'name': 'Политика конфиденциальности', 'url': request.build_absolute_uri('/privacy/')},
    ]
    return render(request, 'pages/privacy.html', {
        'page': StaticPage(),
        'seo_breadcrumbs': seo_breadcrumbs,
    })


def home_page(request):
    """Главная страница"""
    page = Page.objects.filter(slug='home', is_published=True).first()
    
    if not page:
        page = Page(
            title='Скупка техники в Томске',
            slug='home',
            page_type='home',
            hero_title='Скупка техники в Томске',
            hero_subtitle='Нашли где купят дороже? Дадим цену выше!',
        )
    
    form = ContactForm(page=page, page_url=request.path)
    settings = SiteSettings.get_settings()
    
    service_pages = Page.objects.filter(
        is_published=True,
        page_type__in=['skupka', 'remont']
    ).order_by('order')[:6]
    
    site_url = request.build_absolute_uri('/')
    seo_breadcrumbs = [{'name': 'Главная', 'url': site_url}]
    return render(request, 'pages/home.html', {
        'page': page,
        'form': form,
        'settings': settings,
        'service_pages': service_pages,
        'seo_breadcrumbs': seo_breadcrumbs,
    })


def page_detail(request, slug):
    """Детальная страница"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    form = ContactForm(page=page, page_url=request.path)
    site_url = request.build_absolute_uri('/')
    seo_breadcrumbs = [
        {'name': 'Главная', 'url': site_url},
        {'name': page.title, 'url': request.build_absolute_uri(page.get_absolute_url())},
    ]
    return render(request, 'pages/page.html', {
        'page': page,
        'form': form,
        'seo_breadcrumbs': seo_breadcrumbs,
    })


@require_POST
def submit_contact(request):
    """Обработка формы обратной связи (AJAX)"""
    
    recaptcha_token = request.POST.get('g-recaptcha-response', '')
    client_ip = get_client_ip(request)
    
    recaptcha_valid, recaptcha_score = verify_recaptcha(recaptcha_token, client_ip)
    
    if not recaptcha_valid:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': {'__all__': ['Проверка безопасности не пройдена. Попробуйте еще раз.']}
            }, status=400)
        messages.error(request, 'Проверка безопасности не пройдена.')
        return redirect(request.POST.get('page_url', '/'))
    
    page_slug = request.POST.get('page_slug', '')
    page = Page.objects.filter(slug=page_slug).first() if page_slug else None
    
    form = ContactForm(
        request.POST,
        page=page,
        page_url=request.POST.get('page_url', '')
    )
    
    if form.is_valid():
        contact_request = form.save()
        
        send_telegram_notification(contact_request)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'
            })
        messages.success(request, 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.')
        return redirect(request.POST.get('page_url', '/'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
    messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    return redirect(request.POST.get('page_url', '/'))


def get_client_ip(request):
    """Получает IP адрес клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_GET
@cache_control(max_age=86400)
def robots_txt(request):
    """Отдача robots.txt для поисковых систем"""
    sitemap_url = request.build_absolute_uri(reverse('django.contrib.sitemaps.views.sitemap'))
    content = (
        'User-agent: *\n'
        'Allow: /\n'
        f'Sitemap: {sitemap_url}\n'
    )
    return HttpResponse(content, content_type='text/plain; charset=utf-8')
