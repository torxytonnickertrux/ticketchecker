from django import forms
from .models import Coupon


class EventSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Buscar', max_length=255)
    date_from = forms.DateField(required=False, label='Data inicial', widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, label='Data final', widget=forms.DateInput(attrs={'type': 'date'}))
    location = forms.CharField(required=False, label='Local', max_length=255)

    def clean(self):
        cleaned = super().clean()
        df = cleaned.get('date_from')
        dt = cleaned.get('date_to')
        if df and dt and df > dt:
            raise forms.ValidationError('Data inicial deve ser anterior à data final.')
        return cleaned


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label='Quantidade')
    coupon_code = forms.CharField(required=False, max_length=20, label='Cupom')

    def __init__(self, *args, ticket=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticket = ticket

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if self.ticket:
            if qty > self.ticket.quantity:
                raise forms.ValidationError(
                    f'Quantidade solicitada ({qty}) maior que a disponível ({self.ticket.quantity}).'
                )
            if qty > self.ticket.max_per_person:
                raise forms.ValidationError(
                    f'Máximo de {self.ticket.max_per_person} ingressos por pessoa.'
                )
        return qty


class QRCodeValidationForm(forms.Form):
    qr_code = forms.CharField(label='Código QR', max_length=255)


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code',
            'description',
            'discount_type',
            'discount_value',
            'min_purchase_amount',
            'max_uses',
            'valid_from',
            'valid_until',
            'is_active',
        ]
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned = super().clean()
        vf = cleaned.get('valid_from')
        vu = cleaned.get('valid_until')
        if vf and vu and vf >= vu:
            raise forms.ValidationError('Data inicial deve ser anterior à data final.')
        return cleaned