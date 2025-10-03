from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event, Ticket, Purchase, Coupon, TicketValidation

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'location', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['event', 'price', 'type', 'quantity', 'max_per_person', 'is_active']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_per_person': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PurchaseForm(forms.ModelForm):
    coupon_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código do cupom (opcional)'
        })
    )
    
    class Meta:
        model = Purchase
        fields = ['quantity', 'payment_method']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)
        
        if self.ticket:
            self.fields['quantity'].widget.attrs['max'] = min(self.ticket.quantity, self.ticket.max_per_person)
            self.fields['quantity'].widget.attrs['value'] = '1'
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        
        if not quantity or quantity <= 0:
            raise forms.ValidationError("A quantidade deve ser maior que zero.")
        
        if self.ticket:
            # Verificar se o ticket ainda existe
            try:
                ticket = Ticket.objects.get(pk=self.ticket.pk)
            except Ticket.DoesNotExist:
                raise forms.ValidationError("Ticket não encontrado ou foi removido.")
            
            # Verificar se o ticket está ativo
            if not ticket.is_active:
                raise forms.ValidationError("Este ticket não está mais ativo.")
            
            # Verificar se o evento está ativo
            if not ticket.event.is_active:
                raise forms.ValidationError("O evento deste ticket não está mais ativo.")
            
            # Verificar se o evento ainda está no futuro
            from django.utils import timezone
            if ticket.event.date <= timezone.now():
                raise forms.ValidationError("O evento já ocorreu.")
            
            # Verificar disponibilidade
            if quantity > ticket.quantity:
                raise forms.ValidationError(f"Quantidade solicitada ({quantity}) maior que a disponível ({ticket.quantity}).")
            
            # Verificar limite por pessoa
            if quantity > ticket.max_per_person:
                raise forms.ValidationError(f"Máximo de {ticket.max_per_person} ingressos por pessoa.")
        
        return quantity
    
    def clean_coupon_code(self):
        coupon_code = self.cleaned_data.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if not coupon.is_valid():
                    raise forms.ValidationError("Cupom inválido ou expirado.")
            except Coupon.DoesNotExist:
                raise forms.ValidationError("Cupom não encontrado.")
        return coupon_code
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        coupon_code = cleaned_data.get('coupon_code')
        
        # Verificar se o ticket ainda existe e está válido
        if self.ticket:
            try:
                ticket = Ticket.objects.get(pk=self.ticket.pk)
                
                # Verificar se há quantidade suficiente
                if quantity and quantity > ticket.quantity:
                    raise forms.ValidationError({
                        'quantity': f"Quantidade solicitada ({quantity}) maior que a disponível ({ticket.quantity})."
                    })
                
                # Verificar valor mínimo do cupom
                if coupon_code and quantity:
                    try:
                        coupon = Coupon.objects.get(code=coupon_code)
                        total_price = ticket.price * quantity
                        if total_price < coupon.min_purchase_amount:
                            raise forms.ValidationError({
                                'coupon_code': f"Valor mínimo para este cupom é R$ {coupon.min_purchase_amount:.2f}."
                            })
                    except Coupon.DoesNotExist:
                        pass  # Já tratado em clean_coupon_code
                        
            except Ticket.DoesNotExist:
                raise forms.ValidationError("Ticket não encontrado ou foi removido.")
        
        return cleaned_data

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class EventSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar eventos...'
        })
    )
    
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    date_to = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Local...'
        })
    )

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount_type', 'discount_value', 'min_purchase_amount', 'max_uses', 'is_active', 'valid_from', 'valid_until']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_type': forms.Select(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_purchase_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_uses': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class QRCodeValidationForm(forms.Form):
    qr_code = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escaneie ou digite o código QR'
        })
    )

class PaymentForm(forms.Form):
    """
    Formulário para dados de pagamento
    """
    PAYMENT_METHOD_CHOICES = [
        ('pix', 'PIX'),
        ('credit_card', 'Cartão de Crédito'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Método de Pagamento"
    )
    
    payer_document = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'data-mask': '000.000.000-00'
        }),
        label="CPF"
    )
    
    installments = forms.IntegerField(
        min_value=1,
        max_value=12,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '12'
        }),
        label="Parcelas"
    )
    
    def clean_payer_document(self):
        document = self.cleaned_data.get('payer_document')
        if document:
            # Remover formatação
            document = document.replace('.', '').replace('-', '').replace('/', '')
            
            # Validar CPF básico
            if len(document) != 11 or not document.isdigit():
                raise forms.ValidationError("CPF inválido.")
            
            # Adicionar formatação
            document = f"{document[:3]}.{document[3:6]}.{document[6:9]}-{document[9:]}"
        
        return document
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        installments = cleaned_data.get('installments')
        
        # Validar parcelas para cartão de crédito
        if payment_method == 'credit_card' and installments and installments > 1:
            # Aqui você pode adicionar validações específicas para parcelas
            # como verificar se o valor permite parcelamento
            pass
        
        return cleaned_data
