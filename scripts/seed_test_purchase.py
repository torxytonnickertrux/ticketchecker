import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import transaction
from users.models import User
from events.models import Ticket, Purchase, TicketValidation


def main():
    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={'name': 'Test User'}
    )
    user.set_password('Test1234!')
    user.save()

    # Selecionar ticket ativo com id=1
    ticket = Ticket.objects.get(pk=1)
    quantity = 2
    total_price = ticket.price * quantity

    with transaction.atomic():
        purchase = Purchase.objects.create(
            ticket=ticket,
            user=user,
            quantity=quantity,
            total_price=total_price,
        )
        # Criar validação com QR
        TicketValidation.objects.create(purchase=purchase)

    # Persistir o ID em arquivo para leitura posterior
    out_path = os.path.join(os.path.dirname(__file__), 'seed_purchase_id.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(str(purchase.id))
    print(f'PURCHASE_ID={purchase.id}')


if __name__ == '__main__':
    main()