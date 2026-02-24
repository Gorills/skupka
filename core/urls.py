from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]
