from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Event(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome do Evento")
    description = models.TextField(verbose_name="Descrição")
    date = models.DateTimeField(verbose_name="Data e Hora")
    location = models.CharField(max_length=255, verbose_name="Local")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Imagem")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return self.name
    
    def clean(self):
        if self.date and self.date <= timezone.now():
            raise ValidationError("A data do evento deve ser no futuro.")
    
    @property
    def is_available(self):
        return self.is_active and self.date > timezone.now()

class Ticket(models.Model):
    TICKET_TYPES = [
        ('VIP', 'VIP'),
        ('Standard', 'Padrão'),
        ('Student', 'Estudante'),
        ('Early Bird', 'Early Bird'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets', verbose_name="Evento")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço")
    type = models.CharField(max_length=255, choices=TICKET_TYPES, verbose_name="Tipo")
    quantity = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Quantidade Disponível")
    max_per_person = models.IntegerField(default=5, validators=[MinValueValidator(1)], verbose_name="Máximo por Pessoa")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ingresso"
        verbose_name_plural = "Ingressos"
        unique_together = ['event', 'type']

    def __str__(self):
        return f"{self.type} - {self.event.name}"
    
    @property
    def is_available(self):
        return self.is_active and self.quantity > 0 and self.event.is_available
    
    def clean(self):
        if self.price < 0:
            raise ValidationError("O preço não pode ser negativo.")
        if self.quantity < 0:
            raise ValidationError("A quantidade não pode ser negativa.")

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name="Ingresso")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Quantidade")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Total")
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="Data da Compra")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed', verbose_name="Status")
    payment_method = models.CharField(max_length=50, default='credit_card', verbose_name="Método de Pagamento")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID da Transação")
    
    class Meta:
        ordering = ['-purchase_date']
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    def __str__(self):
        return f"{self.quantity} x {self.ticket.type} para {self.user.username}"
    
    def clean(self):
        if self.quantity > self.ticket.quantity:
            raise ValidationError("Quantidade solicitada maior que a disponível.")
        if self.quantity > self.ticket.max_per_person:
            raise ValidationError(f"Máximo de {self.ticket.max_per_person} ingressos por pessoa.")
    
    def save(self, *args, **kwargs):
        self.total_price = self.ticket.price * self.quantity
        super().save(*args, **kwargs)

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    description = models.CharField(max_length=255, verbose_name="Descrição")
    discount_type = models.CharField(max_length=10, choices=[
        ('percentage', 'Porcentagem'),
        ('fixed', 'Valor Fixo')
    ], verbose_name="Tipo de Desconto")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Desconto")
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Mínimo")
    max_uses = models.IntegerField(default=1, verbose_name="Máximo de Usos")
    current_uses = models.IntegerField(default=0, verbose_name="Usos Atuais")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    valid_from = models.DateTimeField(verbose_name="Válido de")
    valid_until = models.DateTimeField(verbose_name="Válido até")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"
    
    def __str__(self):
        return f"{self.code} - {self.description}"
    
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.current_uses < self.max_uses and
                self.valid_from <= now <= self.valid_until)
    
    def apply_discount(self, amount):
        if not self.is_valid():
            return 0
        
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        else:
            return min(self.discount_value, amount)

class TicketValidation(models.Model):
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='validation')
    qr_code = models.CharField(max_length=255, unique=True, verbose_name="Código QR")
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name="Imagem QR")
    is_validated = models.BooleanField(default=False, verbose_name="Validado")
    validated_at = models.DateTimeField(blank=True, null=True, verbose_name="Validado em")
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Validado por")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Validação de Ingresso"
        verbose_name_plural = "Validações de Ingressos"
    
    def __str__(self):
        return f"QR: {self.qr_code[:10]}... - {self.purchase.ticket.event.name}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = str(uuid.uuid4())
        super().save(*args, **kwargs)
        
        # Gerar QR code se não existir
        if not self.qr_code_image:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f'qr_{self.qr_code}.png'
        self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        self.save()

class EventAnalytics(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='analytics')
    total_views = models.IntegerField(default=0, verbose_name="Total de Visualizações")
    total_purchases = models.IntegerField(default=0, verbose_name="Total de Compras")
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita Total")
    conversion_rate = models.FloatField(default=0, verbose_name="Taxa de Conversão")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Analytics do Evento"
        verbose_name_plural = "Analytics dos Eventos"
    
    def __str__(self):
        return f"Analytics - {self.event.name}"
    
    def update_analytics(self):
        purchases = Purchase.objects.filter(ticket__event=self.event, status='confirmed')
        self.total_purchases = purchases.count()
        self.total_revenue = sum(p.total_price for p in purchases)
        self.conversion_rate = (self.total_purchases / max(self.total_views, 1)) * 100
        self.save()