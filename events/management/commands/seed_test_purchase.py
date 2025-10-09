from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from events.models import Event, Ticket, Purchase, TicketValidation
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Cria um usuário e uma compra de teste, imprimindo o ID da compra.'

    def add_arguments(self, parser):
        parser.add_argument('--ticket-id', type=int, default=1, help='ID do ticket a comprar')
        parser.add_argument('--email', type=str, default='test@example.com', help='Email do usuário de teste')
        parser.add_argument('--password', type=str, default='Test1234!', help='Senha do usuário de teste')
        parser.add_argument('--quantity', type=int, default=1, help='Quantidade de ingressos')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']
        password = options['password']
        ticket_id = options['ticket_id']
        quantity = options['quantity']

        user, created = User.objects.get_or_create(email=email, defaults={'name': 'Test User'})
        if created:
            self.stdout.write(self.style.SUCCESS(f'Usuário criado: {email}'))
        user.set_password(password)
        user.save()

        try:
            ticket = Ticket.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            # Criar evento e ticket padrão quando o ticket não existe
            event = Event.objects.create(
                name='Evento de Teste',
                description='Evento criado automaticamente pelo seed.',
                date=timezone.now() + timedelta(days=1),
                location='Local de Teste',
                is_active=True,
            )
            ticket = Ticket.objects.create(
                event=event,
                price=Decimal('50.00'),
                type='Standard',
                quantity=100,
                max_per_person=5,
                is_active=True,
            )
            self.stdout.write(self.style.WARNING(
                f'Ticket ID {ticket_id} não encontrado. Ticket criado automaticamente com ID {ticket.id}.'
            ))

        total_price = ticket.price * quantity

        with transaction.atomic():
            purchase = Purchase.objects.create(
                ticket=ticket,
                user=user,
                quantity=quantity,
                total_price=total_price,
            )
            TicketValidation.objects.create(purchase=purchase)

        self.stdout.write(self.style.SUCCESS(f'PURCHASE_ID={purchase.id}'))