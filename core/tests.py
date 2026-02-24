"""Тесты для core приложения"""
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from .models import SiteSettings, ContactRequest


class ContactFormRecaptchaTest(TestCase):
    """Проверка интеграции reCAPTCHA с формой обратной связи"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:submit_contact')
        self.valid_data = {
            'csrfmiddlewaretoken': 'test',
            'name': 'Тест',
            'phone': '+7 999 123-45-67',
            'email': 'test@example.com',
            'message': 'Тестовое сообщение',
            'privacy_agreement': 'on',
            'page_slug': '',
            'page_url': '/',
        }

    @patch('core.views.verify_recaptcha')
    def test_reject_when_recaptcha_invalid(self, mock_verify):
        """Форма отклоняется при невалидной reCAPTCHA"""
        mock_verify.return_value = (False, 0.3)
        response = self.client.post(
            self.url,
            {**self.valid_data, 'g-recaptcha-response': 'invalid-token'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('__all__', data['errors'])
        mock_verify.assert_called_once()

    @patch('core.views.verify_recaptcha')
    def test_reject_when_recaptcha_token_missing(self, mock_verify):
        """Форма отклоняется при отсутствии токена reCAPTCHA"""
        mock_verify.return_value = (False, 0.0)
        response = self.client.post(
            self.url,
            self.valid_data,  # без g-recaptcha-response
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        mock_verify.assert_called_once()
        args, kwargs = mock_verify.call_args
        self.assertEqual(args[0], '')  # пустой токен

    @patch('core.views.verify_recaptcha')
    def test_accept_when_recaptcha_valid(self, mock_verify):
        """Форма принимается при валидной reCAPTCHA"""
        mock_verify.return_value = (True, 0.9)
        response = self.client.post(
            self.url,
            {**self.valid_data, 'g-recaptcha-response': 'valid-token'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(ContactRequest.objects.count(), 1)
        mock_verify.assert_called_once()
