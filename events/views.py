from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from users.views import role_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, transaction
from .models import Event, Ticket, Purchase, Coupon, TicketValidation, EventAnalytics
from .forms import EventSearchForm, PurchaseForm, QRCodeValidationForm, CouponForm
from django.db.models import F
from .utils.error_logger import ErrorLogger
from django.http import HttpResponse

def event_list(request):
    form = EventSearchForm(request.GET)
    events = Event.objects.filter(is_active=True)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        location = form.cleaned_data.get('location')
        
        if search:
            events = events.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        if date_from:
            events = events.filter(date__gte=date_from)
        
        if date_to:
            events = events.filter(date__lte=date_to)
        
        if location:
            events = events.filter(location__icontains=location)
    
    # Filtrar apenas eventos futuros
    events = events.filter(date__gt=timezone.now())
    
    paginator = Paginator(events, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id, is_active=True)
    tickets = event.tickets.filter(is_active=True, quantity__gt=0)
    
    context = {
        'event': event,
        'tickets': tickets,
    }
    return render(request, 'events/event_detail.html', context)

def vite_client_placeholder(request):
    return HttpResponse("", content_type="application/javascript")

@login_required
def purchase_ticket(request, ticket_id):
    try:
        # Log do início da compra
        ErrorLogger.log_purchase_flow("PURCHASE_START", {
            'ticket_id': ticket_id,
            'user_id': request.user.id,
        })
        
        # Verificar se o ticket existe e está ativo
        ticket = get_object_or_404(Ticket, pk=ticket_id, is_active=True)
        
        # Log do ticket encontrado
        ErrorLogger.log_object_state(ticket, "TICKET_FOUND")
        
        # Verificar se o evento ainda está ativo
        if not ticket.event.is_active:
            ErrorLogger.log_ticket_error(Exception("Evento inativo"), {
                'ticket_id': ticket_id,
                'event_id': ticket.event.id,
                'user_id': request.user.id,
            })
            messages.error(request, 'Este evento não está mais ativo.')
            return redirect('event_list')
        
        # Verificar se o evento ainda está no futuro
        if ticket.event.date <= timezone.now():
            ErrorLogger.log_ticket_error(Exception("Evento no passado"), {
                'ticket_id': ticket_id,
                'event_date': ticket.event.date.isoformat(),
                'user_id': request.user.id,
            })
            messages.error(request, 'Este evento já ocorreu.')
            return redirect('event_list')
        
        # Verificar disponibilidade do ticket
        if not ticket.is_available:
            ErrorLogger.log_ticket_error(Exception("Ticket não disponível"), {
                'ticket_id': ticket_id,
                'quantity': ticket.quantity,
                'is_active': ticket.is_active,
                'user_id': request.user.id,
            })
            messages.error(request, 'Este ingresso não está mais disponível.')
            return redirect('event_detail', event_id=ticket.event.id)
        
        if request.method == 'POST':
            form = PurchaseForm(request.POST, ticket=ticket)
            if form.is_valid():
                try:
                    quantity = form.cleaned_data['quantity']
                    coupon_code = form.cleaned_data.get('coupon_code')
                    
                    # Verificar disponibilidade novamente (race condition)
                    if ticket.quantity < quantity:
                        messages.error(request, f'Quantidade solicitada ({quantity}) maior que a disponível ({ticket.quantity}).')
                        return render(request, 'events/purchase_ticket.html', {'ticket': ticket, 'form': form})
                    
                    # Verificar limite por pessoa
                    if quantity > ticket.max_per_person:
                        messages.error(request, f'Máximo de {ticket.max_per_person} ingressos por pessoa.')
                        return render(request, 'events/purchase_ticket.html', {'ticket': ticket, 'form': form})
                    
                    # Calcular preço total
                    total_price = ticket.price * quantity
                    discount_amount = 0
                    coupon = None
                    
                    # Aplicar cupom se fornecido
                    if coupon_code:
                        try:
                            coupon = Coupon.objects.get(code=coupon_code)
                            if coupon.is_valid() and total_price >= coupon.min_purchase_amount:
                                discount_amount = coupon.apply_discount(total_price)
                                total_price -= discount_amount
                            else:
                                messages.error(request, 'Cupom inválido ou valor mínimo não atingido.')
                                return render(request, 'events/purchase_ticket.html', {'ticket': ticket, 'form': form})
                        except Coupon.DoesNotExist:
                            messages.error(request, 'Cupom não encontrado.')
                            return render(request, 'events/purchase_ticket.html', {'ticket': ticket, 'form': form})
                    
                    # Usar transação atômica para garantir consistência
                    with transaction.atomic():
                        # Bloquear linha do ingresso para evitar corrida
                        ticket_locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
                        if ticket_locked.quantity < quantity:
                            messages.error(request, f'Quantidade solicitada ({quantity}) maior que a disponível ({ticket_locked.quantity}).')
                            return render(request, 'events/purchase_ticket.html', {'ticket': ticket_locked, 'form': form})
                        
                        # Log antes de criar a compra
                        ErrorLogger.log_purchase_flow("BEFORE_PURCHASE_CREATE", {
                            'ticket_id': ticket.id,
                            'user_id': request.user.id,
                            'quantity': quantity,
                            'total_price': total_price,
                        })
                        
                        # Criar a compra manualmente (PurchaseForm não é ModelForm)
                        purchase = Purchase(
                            ticket=ticket,
                            user=request.user,
                            quantity=quantity,
                            total_price=total_price,
                        )
                        
                        # Log do objeto purchase antes de salvar
                        ErrorLogger.log_object_state(purchase, "PURCHASE_BEFORE_SAVE")
                        
                        purchase.save()
                        
                        # Log do objeto purchase após salvar
                        ErrorLogger.log_object_state(purchase, "PURCHASE_AFTER_SAVE")
                        
                        # Atualizar quantidade disponível de forma atômica
                        Ticket.objects.filter(pk=ticket_locked.pk).update(quantity=F('quantity') - quantity)
                        
                        # Atualizar uso do cupom
                        if coupon:
                            coupon.current_uses += 1
                            coupon.save()
                        
                        # Criar validação com QR code
                        validation = TicketValidation.objects.create(purchase=purchase)
                    
                    # Enviar email de confirmação
                    try:
                        send_confirmation_email(request.user, purchase)
                    except Exception as e:
                        # Log do erro mas não falha a compra
                        print(f"Erro ao enviar email: {e}")
                    
                    messages.success(request, f'Compra criada com sucesso! Total: R$ {purchase.total_price:.2f}')
                    return redirect('payment_form', purchase_id=purchase.id)
                    
                except ValidationError as e:
                    messages.error(request, f'Erro de validação: {str(e)}')
                except Exception as e:
                    messages.error(request, f'Erro inesperado ao processar a compra: {str(e)}')
                    # Log do erro para debug
                    print(f"Erro na compra: {e}")
            else:
                # Formulário inválido - mostrar erros
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            form = PurchaseForm(ticket=ticket)
        
        context = {
            'ticket': ticket,
            'form': form,
        }
        return render(request, 'events/purchase_ticket.html', context)
        
    except Ticket.DoesNotExist:
        messages.error(request, 'Ticket não encontrado.')
        return redirect('event_list')
    except Exception as e:
        messages.error(request, f'Erro inesperado: {str(e)}')
        return redirect('event_list')

@login_required
def purchase_history(request):
    purchases = Purchase.objects.filter(user=request.user).select_related('ticket__event')
    
    paginator = Paginator(purchases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'events/purchase_history.html', context)

def register(request):
    # Redireciona para o fluxo de registro do app users
    return redirect('users:register')

@login_required
def cancel_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id, user=request.user)
    
    if purchase.status == 'cancelled':
        messages.warning(request, 'Esta compra já foi cancelada.')
        return redirect('purchase_history')
    
    if request.method == 'POST':
        purchase.status = 'cancelled'
        purchase.save()
        
        # Restaurar quantidade disponível
        purchase.ticket.quantity += purchase.quantity
        purchase.ticket.save()
        
        messages.success(request, 'Compra cancelada com sucesso.')
        return redirect('purchase_history')
    
    return render(request, 'events/cancel_purchase.html', {'purchase': purchase})

def home(request):
    # Eventos em destaque (próximos 3 eventos)
    featured_events = Event.objects.filter(
        is_active=True,
        date__gt=timezone.now()
    ).order_by('date')[:3]

    # Personalização básica por usuário
    user_events = None
    recommended_events = None
    last_ticket_types = []

    if request.user.is_authenticated:
        # Compras aprovadas do usuário e tipos de ingressos comprados
        user_purchases = Purchase.objects.filter(user=request.user, status='approved').select_related('ticket__event')
        last_ticket_types = list(
            user_purchases.values_list('ticket__type', flat=True).distinct()
        )
        # Próximos eventos do usuário (onde há compras aprovadas)
        user_events = Event.objects.filter(
            id__in=user_purchases.values_list('ticket__event__id', flat=True),
            is_active=True,
            date__gt=timezone.now()
        ).order_by('date')[:6]

        # Recomendação simples: eventos ativos com tickets do mesmo tipo comprado
        if last_ticket_types:
            recommended_events = Event.objects.filter(
                is_active=True,
                date__gt=timezone.now(),
                tickets__type__in=last_ticket_types
            ).exclude(id__in=user_events.values_list('id', flat=True)).distinct().order_by('date')[:6]

    context = {
        'featured_events': featured_events,
        'user_events': user_events,
        'recommended_events': recommended_events,
        'last_ticket_types': last_ticket_types,
    }
    return render(request, 'events/home.html', context)

def send_confirmation_email(user, purchase):
    """Enviar email de confirmação de compra"""
    try:
        subject = f'Confirmação de Compra - {purchase.ticket.event.name}'
        # Determinar nome de exibição seguro
        try:
            full_name = user.get_full_name()
        except Exception:
            full_name = ''
        display_name = full_name or getattr(user, 'name', '') or getattr(user, 'email', '') or str(user)
        message = f'''
        Olá {display_name},
        
        Sua compra foi confirmada com sucesso!
        
        Evento: {purchase.ticket.event.name}
        Data: {purchase.ticket.event.date.strftime("%d/%m/%Y %H:%M")}
        Local: {purchase.ticket.event.location}
        Ingresso: {purchase.ticket.get_type_display()}
        Quantidade: {purchase.quantity}
        Total: R$ {purchase.total_price:.2f}
        
        Seu QR Code será enviado em breve.
        
        Obrigado por escolher nosso sistema!
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

@role_required(['admin', 'ticket_validator'])
def validate_ticket(request):
    """View para validar ingressos (para administradores)"""
    # Acesso controlado por roles: admin e ticket_validator
    
    if request.method == 'POST':
        form = QRCodeValidationForm(request.POST)
        if form.is_valid():
            qr_code = form.cleaned_data['qr_code']
            try:
                validation = TicketValidation.objects.get(qr_code=qr_code)
                if validation.is_validated:
                    messages.warning(request, 'Ingresso já foi validado.')
                else:
                    validation.is_validated = True
                    validation.validated_at = timezone.now()
                    validation.validated_by = request.user
                    validation.save()
                    messages.success(request, 'Ingresso validado com sucesso!')
            except TicketValidation.DoesNotExist:
                messages.error(request, 'Código QR inválido.')
    else:
        form = QRCodeValidationForm()
    
    return render(request, 'events/validate_ticket.html', {'form': form})

@role_required(['admin', 'event_manager'])
def dashboard(request):
    """Dashboard administrativo"""
    # Acesso controlado por roles: admin e event_manager
    
    # Estatísticas gerais
    total_events = Event.objects.count()
    total_tickets = Ticket.objects.count()
    total_purchases = Purchase.objects.filter(status='approved').count()
    total_revenue = Purchase.objects.filter(status='approved').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Eventos recentes
    recent_events = Event.objects.order_by('-created_at')[:5]
    
    # Compras recentes
    recent_purchases = Purchase.objects.filter(status='approved').order_by('-purchase_date')[:10]
    
    context = {
        'total_events': total_events,
        'total_tickets': total_tickets,
        'total_purchases': total_purchases,
        'total_revenue': total_revenue,
        'recent_events': recent_events,
        'recent_purchases': recent_purchases,
    }
    return render(request, 'events/dashboard.html', context)

@role_required(['admin', 'event_manager'])
def coupon_management(request):
    """Gerenciamento de cupons"""
    # Acesso controlado por roles: admin e event_manager
    
    coupons = Coupon.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cupom criado com sucesso!')
            return redirect('coupon_management')
    else:
        form = CouponForm()
    
    context = {
        'coupons': coupons,
        'form': form,
    }
    return render(request, 'events/coupon_management.html', context)

@role_required(['admin', 'event_manager'])
def analytics(request, event_id):
    """Analytics de um evento específico"""
    # Acesso controlado por roles: admin e event_manager
    
    event = get_object_or_404(Event, pk=event_id)
    analytics, created = EventAnalytics.objects.get_or_create(event=event)
    analytics.update_analytics()
    
    # Dados para gráficos
    ticket_sales = Ticket.objects.filter(event=event).annotate(
        sold=Count('purchase')
    ).values('type', 'sold')
    
    context = {
        'event': event,
        'analytics': analytics,
        'ticket_sales': list(ticket_sales),
    }
    return render(request, 'events/analytics.html', context)

@login_required
def logout_view(request):
    return redirect('users:logout')

def handle_purchase_error(request, error_message, redirect_url='event_list'):
    """
    Função auxiliar para tratar erros de compra de forma consistente
    """
    messages.error(request, error_message)
    return redirect(redirect_url)

def safe_purchase_ticket(request, ticket_id):
    """
    Wrapper seguro para purchase_ticket com tratamento de erros
    """
    try:
        return purchase_ticket(request, ticket_id)
    except ObjectDoesNotExist as e:
        if 'ticket' in str(e).lower():
            return handle_purchase_error(request, 'Ticket não encontrado ou foi removido.')
        elif 'purchase' in str(e).lower():
            return handle_purchase_error(request, 'Compra não encontrada.', 'purchase_history')
        else:
            return handle_purchase_error(request, f'Objeto não encontrado: {str(e)}')
    except ValidationError as e:
        return handle_purchase_error(request, f'Erro de validação: {str(e)}')
    except IntegrityError as e:
        return handle_purchase_error(request, 'Erro de integridade do banco de dados.')
    except Exception as e:
        # Log do erro para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro inesperado na compra: {e}", exc_info=True)
        return handle_purchase_error(request, 'Erro inesperado. Tente novamente.')

def login_view(request):
    return redirect('users:login')