from django import forms
from .models import ContactRequest


class ContactForm(forms.ModelForm):
    """Форма обратной связи с антиспам защитой"""
    
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input--honeypot',
            'tabindex': '-1',
            'autocomplete': 'off',
        })
    )
    privacy_agreement = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'id_privacy_agreement',
        })
    )
    
    class Meta:
        model = ContactRequest
        fields = ['name', 'phone', 'email', 'message', 'device_info']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя *',
                'class': 'form-input',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 (___) ___-__-__',
                'class': 'form-input js-phone-mask',
                'required': True,
                'type': 'tel',
                'inputmode': 'numeric',
                'autocomplete': 'tel',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email (необязательно)',
                'class': 'form-input',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Опишите устройство: модель, состояние, комплектация',
                'class': 'form-textarea',
                'rows': 4,
            }),
            'device_info': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page', None)
        self.page_url = kwargs.pop('page_url', '')
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if cleaned_data.get('website'):
            raise forms.ValidationError('Обнаружена подозрительная активность.')
        
        if not cleaned_data.get('privacy_agreement'):
            raise forms.ValidationError('Необходимо согласие на обработку персональных данных.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.page = self.page
        instance.page_url = self.page_url
        if commit:
            instance.save()
        return instance
