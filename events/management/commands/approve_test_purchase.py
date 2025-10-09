from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Purchase, EventAnalytics


class Command(BaseCommand):
    help = 'Aprova uma compra de teste pelo ID e atualiza analytics.'

    def add_arguments(self, parser):
        parser.add_argument('--purchase-id', type=int, required=True, help='ID da compra a aprovar')

    def handle(self, *args, **options):
        purchase_id = options['purchase_id']
        try:
            with transaction.atomic():
                purchase = Purchase.objects.select_related('ticket__event').get(id=purchase_id)
                purchase.status = 'approved'
                purchase.payment_status = 'approved'
                purchase.save(update_fields=['status', 'payment_status'])

                # Atualizar analytics do evento
                event = purchase.ticket.event
                analytics, _ = EventAnalytics.objects.get_or_create(event=event)
                analytics.update_analytics()

                self.stdout.write(self.style.SUCCESS(f"Purchase {purchase_id} approved."))
        except Purchase.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Purchase {purchase_id} not found."))