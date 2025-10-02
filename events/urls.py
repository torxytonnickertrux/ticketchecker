
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('purchase/<int:ticket_id>/', views.purchase_ticket, name='purchase_ticket'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('register/', views.register, name='register'),
    path('cancel/<int:purchase_id>/', views.cancel_purchase, name='cancel_purchase'),
    
    # Admin views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('validate/', views.validate_ticket, name='validate_ticket'),
    path('coupons/', views.coupon_management, name='coupon_management'),
    path('analytics/<int:event_id>/', views.analytics, name='analytics'),
]
