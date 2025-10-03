"""
Sistema de pagamento simplificado
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Purchase
import mercadopago
import json

@login_required
def simple_payment(request, purchase_id):
    """
    Pagamento simples - apenas PIX
    """
    purchase = get_object_or_404(Purchase, pk=purchase_id, user=request.user)
    
    if request.method == 'POST':
        try:
            # Configurar Mercado Pago
            mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            
            # Criar preferência
            preference_data = {
                "items": [
                    {
                        "title": f"Ingresso {purchase.ticket.type} - {purchase.ticket.event.name}",
                        "quantity": purchase.quantity,
                        "unit_price": float(purchase.ticket.price),
                        "currency_id": "BRL"
                    }
                ],
                "payer": {
                    "email": request.user.email,
                    "name": request.user.get_full_name() or request.user.username
                },
                "payment_methods": {
                    "excluded_payment_methods": [
                        {"id": "credit_card"},
                        {"id": "debit_card"}
                    ]
                },
                "back_urls": {
                    "success": f"{settings.SITE_URL}/payment/success/",
                    "failure": f"{settings.SITE_URL}/payment/failure/",
                    "pending": f"{settings.SITE_URL}/payment/pending/"
                },
                "auto_return": "approved"
            }
            
            # Criar preferência
            result = mp.preference().create(preference_data)
            
            if result["status"] == 201:
                preference = result["response"]
                
                # Atualizar compra
                purchase.status = 'processing'
                purchase.mercado_pago_id = preference['id']
                purchase.save()
                
                # Redirecionar para checkout
                return redirect(preference['init_point'])
            else:
                messages.error(request, 'Erro ao processar pagamento.')
                
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
    
    context = {
        'purchase': purchase,
    }
    return render(request, 'events/simple_payment.html', context)

@login_required
def payment_success(request):
    """
    Página de sucesso
    """
    return render(request, 'events/payment_success.html')

@login_required
def payment_failure(request):
    """
    Página de falha
    """
    return render(request, 'events/payment_failure.html')

@login_required
def payment_pending(request):
    """
    Página pendente
    """
    return render(request, 'events/payment_pending.html')

@csrf_exempt
def webhook_simple(request):
    """
    Webhook simples
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if data.get('type') == 'payment':
                payment_id = data.get('data', {}).get('id')
                
                # Buscar compra pelo ID do Mercado Pago
                purchase = Purchase.objects.get(mercado_pago_id=payment_id)
                
                # Atualizar status
                purchase.status = 'approved'
                purchase.save()
                
                # Atualizar quantidade de tickets
                ticket = purchase.ticket
                ticket.quantity -= purchase.quantity
                ticket.save()
                
        except Exception as e:
            print(f"Erro no webhook: {e}")
    
    return JsonResponse({'status': 'ok'})
