import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)


def verify_recaptcha(token, remote_ip=None):
    """Проверяет токен reCAPTCHA v3"""
    from .models import SiteSettings
    
    settings = SiteSettings.get_settings()
    
    if not settings.recaptcha_secret_key:
        return True, 1.0
    
    if not token:
        logger.warning('reCAPTCHA токен отсутствует')
        return False, 0.0
    
    url = 'https://www.google.com/recaptcha/api/siteverify'
    
    data = {
        'secret': settings.recaptcha_secret_key,
        'response': token,
    }
    
    if remote_ip:
        data['remoteip'] = remote_ip
    
    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, data=encoded_data, method='POST')
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            success = result.get('success', False)
            score = result.get('score', 0.0)
            
            if success and score >= settings.recaptcha_min_score:
                logger.info(f'reCAPTCHA passed: score={score}')
                return True, score
            else:
                logger.warning(f'reCAPTCHA failed: success={success}, score={score}, errors={result.get("error-codes", [])}')
                return False, score
                
    except Exception as e:
        logger.error(f'Ошибка проверки reCAPTCHA: {e}')
        return True, 1.0


def send_telegram_notification(contact_request):
    """Отправляет уведомление о новой заявке в Telegram"""
    from .models import SiteSettings
    
    settings = SiteSettings.get_settings()
    
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.info('Telegram не настроен, уведомление не отправлено')
        return False
    
    page_info = ''
    if contact_request.page:
        page_info = f"\n📄 Страница: {contact_request.page.title}"
    elif contact_request.page_url:
        page_info = f"\n📄 URL: {contact_request.page_url}"
    
    message = f"""🔔 <b>Новая заявка с сайта!</b>

👤 <b>Имя:</b> {contact_request.name}
📞 <b>Телефон:</b> {contact_request.phone}"""
    
    if contact_request.email:
        message += f"\n\n📧 <b>Email:</b> {contact_request.email}"
    
    if contact_request.message:
        message += f"\n\n💬 <b>Сообщение:</b>\n{contact_request.message}"
    
    message += page_info
    message += f"\n\n🕐 {contact_request.created_at.strftime('%d.%m.%Y %H:%M')}"

    return send_telegram_message(
        settings.telegram_bot_token,
        settings.telegram_chat_id,
        message
    )


def send_telegram_message(bot_token, chat_id, message):
    """Отправляет сообщение в Telegram"""
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, data=encoded_data, method='POST')
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                logger.info(f'Telegram уведомление отправлено в чат {chat_id}')
                return True
            else:
                logger.error(f'Telegram API error: {result}')
                return False
                
    except Exception as e:
        logger.error(f'Ошибка отправки в Telegram: {e}')
        return False
