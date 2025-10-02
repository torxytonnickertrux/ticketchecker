from django.contrib import admin
from .models import Event, Ticket, Purchase, Coupon, TicketValidation, EventAnalytics

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'date', 'created_at']
    search_fields = ['name', 'description', 'location']
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'image')
        }),
        ('Data e Local', {
            'fields': ('date', 'location')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['event', 'type', 'price', 'quantity', 'max_per_person', 'is_active']
    list_filter = ['type', 'is_active', 'event__date']
    search_fields = ['event__name', 'type']
    ordering = ['event__date', 'type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações do Ingresso', {
            'fields': ('event', 'type', 'price')
        }),
        ('Disponibilidade', {
            'fields': ('quantity', 'max_per_person', 'is_active')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'ticket', 'quantity', 'total_price', 'status', 'purchase_date']
    list_filter = ['status', 'payment_method', 'purchase_date']
    search_fields = ['user__username', 'user__email', 'ticket__event__name']
    ordering = ['-purchase_date']
    readonly_fields = ['purchase_date', 'total_price']
    
    fieldsets = (
        ('Informações da Compra', {
            'fields': ('user', 'ticket', 'quantity', 'total_price')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'transaction_id', 'status')
        }),
        ('Metadados', {
            'fields': ('purchase_date',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'ticket__event')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'discount_type', 'discount_value', 'is_active', 'current_uses', 'max_uses']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['current_uses', 'created_at']
    
    fieldsets = (
        ('Informações do Cupom', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Desconto', {
            'fields': ('discount_type', 'discount_value', 'min_purchase_amount')
        }),
        ('Limites', {
            'fields': ('max_uses', 'current_uses')
        }),
        ('Validade', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(TicketValidation)
class TicketValidationAdmin(admin.ModelAdmin):
    list_display = ['qr_code', 'purchase', 'is_validated', 'validated_at', 'validated_by']
    list_filter = ['is_validated', 'validated_at', 'created_at']
    search_fields = ['qr_code', 'purchase__user__username', 'purchase__ticket__event__name']
    readonly_fields = ['qr_code', 'created_at']
    
    fieldsets = (
        ('Informações da Validação', {
            'fields': ('purchase', 'qr_code', 'qr_code_image')
        }),
        ('Status', {
            'fields': ('is_validated', 'validated_at', 'validated_by')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(EventAnalytics)
class EventAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['event', 'total_views', 'total_purchases', 'total_revenue', 'conversion_rate', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['event__name']
    readonly_fields = ['total_views', 'total_purchases', 'total_revenue', 'conversion_rate', 'last_updated']
    
    fieldsets = (
        ('Evento', {
            'fields': ('event',)
        }),
        ('Estatísticas', {
            'fields': ('total_views', 'total_purchases', 'total_revenue', 'conversion_rate')
        }),
        ('Metadados', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
