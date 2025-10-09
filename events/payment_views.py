from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Purchase, Payment
from .services.mercadopago_service import MercadoPagoService


@login_required
def payment_form(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id, user=request.user)
    if hasattr(purchase, 'payment') and purchase.payment.status == 'approved':
        messages.info(request, 'Pagamento já aprovado.')
        return redirect('purchase_history')

    mp = MercadoPagoService()
    description = f"Ingresso {purchase.ticket.type} - {purchase.ticket.event.name}"
    try:
        payment = purchase.payment
    except Payment.DoesNotExist:
        payment = mp.create_pix_payment(purchase, description=description)
    # Em sandbox sem SDK, garantir QR local para exibição
    payment = mp.ensure_local_pix_qr(payment, purchase, description=description)

    context = {
        'purchase': purchase,
        'payment': payment,
        'public_key': mp.public_key,
        'sandbox': mp.sandbox,
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_checkout(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, purchase__user=request.user)
    mp = MercadoPagoService()
    status = mp.get_payment_status(payment)
    if status == 'approved':
        payment.purchase.status = 'approved'
        payment.purchase.payment_status = 'approved'
        payment.purchase.payment_date = payment.paid_at
        payment.purchase.save()
        messages.success(request, 'Pagamento aprovado!')
        return redirect('purchase_history')
    messages.info(request, f'Status do pagamento: {status}')
    return render(request, 'payments/payment_status.html', {'payment': payment})


@login_required
def cancel_payment(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, purchase__user=request.user)
    payment.status = 'cancelled'
    payment.purchase.status = 'cancelled'
    payment.purchase.save()
    payment.save()
    messages.info(request, 'Pagamento cancelado.')
    return redirect('purchase_history')


@login_required
def payment_success(request):
    messages.success(request, 'Pagamento concluído com sucesso.')
    return redirect('purchase_history')


@login_required
def payment_failure(request):
    messages.error(request, 'Pagamento falhou ou foi rejeitado.')
    return redirect('purchase_history')


@login_required
def payment_pending(request):
    messages.info(request, 'Pagamento pendente de confirmação.')
    return redirect('purchase_history')


@csrf_exempt
@require_POST
def webhook_mercadopago(request):
    mp = MercadoPagoService()
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict() or {}
    payment = mp.handle_webhook(payload)
    if payment and payment.status == 'approved':
        purchase = payment.purchase
        purchase.status = 'approved'
        purchase.payment_status = 'approved'
        purchase.payment_date = payment.paid_at
        purchase.save()
    return JsonResponse({'ok': True})