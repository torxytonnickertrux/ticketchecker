from django.db import models
from django.utils import timezone
import json


class WebhookEvent(models.Model):
    """
    Modelo para armazenar eventos recebidos via webhook do Mercado Pago
    """
    EVENT_TYPES = [
        ('payment', 'Pagamento'),
        ('plan', 'Plano'),
        ('subscription', 'Assinatura'),
        ('invoice', 'Fatura'),
        ('point_integration_whitelist', 'Integração Ponto'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processed', 'Processado'),
        ('failed', 'Falhou'),
        ('ignored', 'Ignorado'),
    ]
    
    # Dados do webhook
    event_id = models.CharField(max_length=100, unique=True, verbose_name="ID do Evento")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Tipo do Evento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Dados do payload
    raw_data = models.JSONField(verbose_name="Dados Brutos")
    processed_data = models.JSONField(blank=True, null=True, verbose_name="Dados Processados")
    
    # Metadados
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="Recebido em")
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name="Processado em")
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensagem de Erro")
    
    # Dados de validação
    signature_valid = models.BooleanField(default=False, verbose_name="Assinatura Válida")
    source_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP de Origem")
    
    class Meta:
        verbose_name = "Evento Webhook"
        verbose_name_plural = "Eventos Webhook"
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.event_id} ({self.status})"
    
    def mark_processed(self):
        """Marcar evento como processado"""
        self.status = 'processed'
        self.processed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Marcar evento como falhou"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()


class WebhookLog(models.Model):
    """
    Modelo para logs detalhados de webhooks
    """
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    webhook_event = models.ForeignKey(WebhookEvent, on_delete=models.CASCADE, related_name='logs', verbose_name="Evento Webhook")
    level = models.CharField(max_length=10, choices=LOG_LEVELS, verbose_name="Nível")
    message = models.TextField(verbose_name="Mensagem")
    details = models.JSONField(blank=True, null=True, verbose_name="Detalhes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Log Webhook"
        verbose_name_plural = "Logs Webhook"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.level} - {self.message[:50]}..."


class PaymentNotification(models.Model):
    """
    Modelo para notificações de pagamento processadas
    """
    NOTIFICATION_TYPES = [
        ('payment_approved', 'Pagamento Aprovado'),
        ('payment_rejected', 'Pagamento Rejeitado'),
        ('payment_cancelled', 'Pagamento Cancelado'),
        ('payment_refunded', 'Pagamento Reembolsado'),
        ('payment_pending', 'Pagamento Pendente'),
    ]
    
    webhook_event = models.OneToOneField(WebhookEvent, on_delete=models.CASCADE, related_name='payment_notification', verbose_name="Evento Webhook")
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name="Tipo de Notificação")
    
    # Dados do pagamento
    payment_id = models.CharField(max_length=100, verbose_name="ID do Pagamento")
    external_reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referência Externa")
    
    # Dados financeiros
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    currency = models.CharField(max_length=3, default='BRL', verbose_name="Moeda")
    
    # Status
    payment_status = models.CharField(max_length=50, verbose_name="Status do Pagamento")
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name="Método de Pagamento")
    
    # Timestamps
    payment_date = models.DateTimeField(blank=True, null=True, verbose_name="Data do Pagamento")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Notificação de Pagamento"
        verbose_name_plural = "Notificações de Pagamento"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.payment_id}"