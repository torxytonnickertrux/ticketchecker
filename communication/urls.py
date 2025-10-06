"""
URLs para comunicação com Mercado Pago
"""
from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Webhooks
    path('build/teste', views.webhook_test, name='webhook_test'),
    path('build/production', views.webhook_production, name='webhook_production'),
    
    # Status e monitoramento
    path('status/', views.webhook_status, name='webhook_status'),
    path('test/', views.webhook_test_endpoint, name='webhook_test_endpoint'),
]