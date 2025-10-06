"""
Admin para comunicação com Mercado Pago
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import WebhookEvent, WebhookLog, PaymentNotification


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_id', 'event_type', 'status', 'signature_valid', 
        'received_at', 'processed_at', 'source_ip'
    ]
    list_filter = [
        'event_type', 'status', 'signature_valid', 'received_at'
    ]
    search_fields = ['event_id', 'event_type', 'source_ip']
    readonly_fields = [
        'event_id', 'event_type', 'raw_data', 'processed_data',
        'received_at', 'processed_at', 'source_ip', 'signature_valid'
    ]
    ordering = ['-received_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('event_id', 'event_type', 'status', 'received_at', 'processed_at')
        }),
        ('Validação', {
            'fields': ('signature_valid', 'source_ip', 'error_message')
        }),
        ('Dados', {
            'fields': ('raw_data', 'processed_data'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('logs', 'payment_notification')
    
    def has_add_permission(self, request):
        return False  # Webhooks são criados apenas via API


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = [
        'webhook_event', 'level', 'message_short', 'created_at'
    ]
    list_filter = ['level', 'created_at', 'webhook_event__event_type']
    search_fields = ['message', 'webhook_event__event_id']
    readonly_fields = ['webhook_event', 'level', 'message', 'details', 'created_at']
    ordering = ['-created_at']
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'Mensagem'
    
    def has_add_permission(self, request):
        return False  # Logs são criados automaticamente


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'notification_type', 'payment_status', 
        'amount', 'currency', 'created_at'
    ]
    list_filter = [
        'notification_type', 'payment_status', 'currency', 'created_at'
    ]
    search_fields = ['payment_id', 'external_reference']
    readonly_fields = [
        'webhook_event', 'notification_type', 'payment_id', 'external_reference',
        'amount', 'currency', 'payment_status', 'payment_method', 'payment_date', 'created_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações da Notificação', {
            'fields': ('webhook_event', 'notification_type', 'created_at')
        }),
        ('Dados do Pagamento', {
            'fields': ('payment_id', 'external_reference', 'amount', 'currency')
        }),
        ('Status', {
            'fields': ('payment_status', 'payment_method', 'payment_date')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Notificações são criadas automaticamente


# Personalizar o admin
admin.site.site_header = "Sistema de Ingressos - Admin"
admin.site.site_title = "Admin Ingressos"
admin.site.index_title = "Comunicação Mercado Pago"