
from django.urls import path
from . import views, payment_views, simple_payment, debug_views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('purchase/<int:ticket_id>/', views.purchase_ticket, name='purchase_ticket'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('register/', views.register, name='register'),
    path('cancel/<int:purchase_id>/', views.cancel_purchase, name='cancel_purchase'),
    
    # Auth views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('validate/', views.validate_ticket, name='validate_ticket'),
    path('coupons/', views.coupon_management, name='coupon_management'),
    path('analytics/<int:event_id>/', views.analytics, name='analytics'),
    
    # Payment views (simples)
    path('pay/<int:purchase_id>/', simple_payment.simple_payment, name='simple_payment'),
    path('payment/success/', simple_payment.payment_success, name='payment_success'),
    path('payment/failure/', simple_payment.payment_failure, name='payment_failure'),
    path('payment/pending/', simple_payment.payment_pending, name='payment_pending'),
    
    # Payment views (complexas com QR Code PIX)
    path('payment/form/<int:purchase_id>/', payment_views.payment_form, name='payment_form'),
    path('payment/checkout/<int:payment_id>/', payment_views.payment_checkout, name='payment_checkout'),
    path('payment/status/<int:payment_id>/', payment_views.payment_status, name='payment_status'),
    path('payment/cancel/<int:payment_id>/', payment_views.cancel_payment, name='cancel_payment'),
    
    # Webhooks
    path('webhook/', simple_payment.webhook_simple, name='webhook_simple'),
    path('webhook/mercadopago/', payment_views.webhook_mercadopago, name='webhook_mercadopago'),
    
    # Debug views (apenas para staff)
    path('debug/', debug_views.debug_dashboard, name='debug_dashboard'),
    path('debug/ticket/<int:ticket_id>/', debug_views.debug_ticket, name='debug_ticket'),
    path('debug/purchase/<int:purchase_id>/', debug_views.debug_purchase, name='debug_purchase'),
    path('debug/logs/', debug_views.debug_logs, name='debug_logs'),
]
