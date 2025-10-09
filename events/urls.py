
from django.urls import path
from . import views
from . import payment_views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('purchase/<int:ticket_id>/', views.purchase_ticket, name='purchase_ticket'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('cancel/<int:purchase_id>/', views.cancel_purchase, name='cancel_purchase'),
    
    # Auth views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('validate/', views.validate_ticket, name='validate_ticket'),
    path('coupons/', views.coupon_management, name='coupon_management'),
    path('analytics/<int:event_id>/', views.analytics, name='analytics'),
    # Dev helper to avoid 404 from vite client in templates
    path('@vite/client', views.vite_client_placeholder, name='vite_client'),
    
    # Payment views (MercadoPago PIX/cartão)
    path('payment/form/<int:purchase_id>/', payment_views.payment_form, name='payment_form'),
    # Card payment routes
    path('payment/card/form/<int:purchase_id>/', payment_views.card_payment_form, name='card_payment_form'),
    path('payment/card/process/<int:purchase_id>/', payment_views.card_payment_process, name='card_payment_process'),
    path('payment/card/status/<int:payment_id>/', payment_views.card_payment_status, name='card_payment_status'),
    path('payment/checkout/<int:payment_id>/', payment_views.payment_checkout, name='payment_checkout'),
    path('payment/cancel/<int:payment_id>/', payment_views.cancel_payment, name='cancel_payment'),
    path('payment/success/', payment_views.payment_success, name='payment_success'),
    path('payment/failure/', payment_views.payment_failure, name='payment_failure'),
    path('payment/pending/', payment_views.payment_pending, name='payment_pending'),
    path('webhook/mercadopago/', payment_views.webhook_mercadopago, name='webhook_mercadopago'),
]
