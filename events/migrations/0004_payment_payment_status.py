# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_purchase_mercado_pago_id_purchase_payment_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Status do Pagamento'),
        ),
    ]