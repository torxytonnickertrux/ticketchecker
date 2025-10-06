# Generated manually

from django.db import migrations


def update_purchase_status(apps, schema_editor):
    """Atualiza o status 'confirmed' para 'approved' nas compras existentes"""
    Purchase = apps.get_model('events', 'Purchase')
    Purchase.objects.filter(status='confirmed').update(status='approved')


def reverse_update_purchase_status(apps, schema_editor):
    """Reverte o status 'approved' para 'confirmed'"""
    Purchase = apps.get_model('events', 'Purchase')
    Purchase.objects.filter(status='approved').update(status='confirmed')


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_add_preference_id_to_purchase'),
    ]

    operations = [
        migrations.RunPython(update_purchase_status, reverse_update_purchase_status),
    ]